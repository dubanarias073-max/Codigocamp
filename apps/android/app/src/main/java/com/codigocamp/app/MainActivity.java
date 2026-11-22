package com.codigocamp.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Dialog;
import android.app.DownloadManager;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Message;
import android.database.Cursor;
import android.provider.ContactsContract;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.ViewGroup;
import android.view.Window;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.LinkedHashMap;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * CódigoCamp en una sola app: la plataforma completa (en un WebView con su propia sesión) + el widget de racha.
 * La página sabe que está dentro de la app por el objeto «CodigoCampApp» (puente JS) y por el User-Agent.
 */
public class MainActivity extends Activity {
    static final String EXTRA_URL = "url";
    private static final int PEDIR_ARCHIVOS = 41;
    private static final int PEDIR_PERMISO = 42;
    private static final int PEDIR_CONTACTOS = 43;

    private WebView web;
    private ValueCallback<Uri[]> alElegirArchivos;
    private String base;
    private byte[] pendienteDatos;
    private String pendienteNombre, pendienteTipo;

    // Si una descarga es un blob: (el .zip de Trabajo), la página la manda por el puente en base64.
    private static final String JS_DESCARGAS = "(function(){if(window.__ccDescargas)return;window.__ccDescargas=1;"
            + "var blobs=new Map(),crear=URL.createObjectURL.bind(URL);"
            + "URL.createObjectURL=function(o){var u=crear(o);try{if(o instanceof Blob)blobs.set(u,o)}catch(e){}return u};"
            + "function enviar(b,n){var r=new FileReader();r.onload=function(){var s=String(r.result);CodigoCampApp.guardarArchivo(n||'archivo',s.slice(s.indexOf(',')+1),b.type||'application/octet-stream')};r.readAsDataURL(b)}"
            + "function bajar(a){var h=a.href||'';if(!a.hasAttribute('download')||!/^(blob:|data:)/.test(h))return false;var n=a.getAttribute('download');"
            + "var b=blobs.get(h);if(b){enviar(b,n)}else{fetch(h).then(function(r){return r.blob()}).then(function(x){enviar(x,n)})}return true}"
            + "var clic=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(!bajar(this))return clic.call(this)};"
            + "document.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[download]');if(a&&bajar(a)){e.preventDefault();e.stopPropagation()}},true);"
            + "})();";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        // En el celular la app va siempre en vertical (en horizontal se descuadra todo). Las tabletas pueden girar.
        if (getResources().getConfiguration().smallestScreenWidthDp < 600) {
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        }
        base = BuildConfig.URL_SERVIDOR;
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0B1020"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportMultipleWindows(true);              // window.open (inicio de sesión con GitHub) → ventana dentro de la app
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setTextZoom(100);                             // el tamaño de letra del sistema no desarma el diseño
        s.setUserAgentString(s.getUserAgentString() + " CodigoCampApp/2.0");
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true);

        web.addJavascriptInterface(new Puente(), "CodigoCampApp");
        web.setWebViewClient(new Cliente());
        web.setWebChromeClient(new Cromo());
        web.setDownloadListener((url, agente, disposicion, tipo, largo) -> descargarUrl(url, agente, disposicion, tipo));

        if (estado != null) web.restoreState(estado);
        else web.loadUrl(urlInicial(getIntent()));
    }

    private String urlInicial(Intent intent) {
        String entrar = urlDeEntrada(intent);
        if (entrar != null) return entrar;
        String u = intent != null ? intent.getStringExtra(EXTRA_URL) : null;
        if (u != null && u.startsWith(base)) return u;
        return base + "/pages/inicio.html?app=1";
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        String entrar = urlDeEntrada(intent);
        if (entrar != null) { web.loadUrl(entrar); return; }
        String u = intent.getStringExtra(EXTRA_URL);
        if (u != null && u.startsWith(base)) web.loadUrl(u);
    }

    @Override
    protected void onSaveInstanceState(Bundle salida) {
        super.onSaveInstanceState(salida);
        web.saveState(salida);
    }

    @Override
    protected void onPause() {
        super.onPause();
        CookieManager.getInstance().flush();   // que la sesión quede guardada aunque Android cierre la app
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    // ---------------------------------------------------------------- puente con la página ----
    /** Métodos que la página de CódigoCamp puede llamar: window.CodigoCampApp.xxx(...) */
    final class Puente {
        /** La página (con sesión iniciada) entrega el token de SU sesión: el widget queda conectado a la app. */
        @JavascriptInterface
        public void conectarWidget(String servidor, String token) {
            if (token == null || token.length() < 20) return;
            String b = servidor != null && servidor.startsWith("http") ? servidor.replaceAll("/+$", "") : base;
            Datos.guardar(MainActivity.this, b, token);
            Widgets.actualizarTodos(MainActivity.this);
        }

        /** Al cerrar sesión en la app, el widget deja de mostrar tus datos. */
        @JavascriptInterface
        public void desconectarWidget() {
            Datos.olvidar(MainActivity.this);
            Widgets.actualizarTodos(MainActivity.this);
        }

        @JavascriptInterface
        public String version() { return "2.1"; }

        /** Pide permiso para leer los contactos (solo la primera vez) y se los entrega a la página con window.ccContactosApp(json). */
        @JavascriptInterface
        public void pedirContactos() {
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT >= 23 && checkSelfPermission(Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[] { Manifest.permission.READ_CONTACTS }, PEDIR_CONTACTOS);
                } else {
                    leerContactos();
                }
            });
        }

        @JavascriptInterface
        public boolean tieneContactos() {
            return Build.VERSION.SDK_INT < 23 || checkSelfPermission(Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED;
        }

        /** Guarda en Descargas un archivo que la página armó en memoria (el .zip de Trabajo, un archivo del proyecto…). */
        @JavascriptInterface
        public void guardarArchivo(String nombre, String base64, String tipo) {
            try {
                byte[] datos = Base64.decode(base64, Base64.DEFAULT);
                runOnUiThread(() -> guardarEnDescargas(limpiar(nombre), datos, tipo));
            } catch (IllegalArgumentException e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "No se pudo guardar el archivo.", Toast.LENGTH_LONG).show());
            }
        }

        @JavascriptInterface
        public void abrirFuera(String url) {
            runOnUiThread(() -> abrirEnNavegador(Uri.parse(url)));
        }
    }

    private static String limpiar(String nombre) {
        String n = nombre == null ? "" : nombre.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        return n.isEmpty() ? "archivo" : n;
    }

    private void guardarEnDescargas(String nombre, byte[] datos, String tipo) {
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues v = new ContentValues();
                v.put(MediaStore.Downloads.DISPLAY_NAME, nombre);
                v.put(MediaStore.Downloads.MIME_TYPE, tipo == null || tipo.isEmpty() ? "application/octet-stream" : tipo);
                v.put(MediaStore.Downloads.IS_PENDING, 1);
                Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                if (uri == null) throw new Exception("sin espacio");
                try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                    if (out == null) throw new Exception("sin acceso");
                    out.write(datos);
                }
                v.clear();
                v.put(MediaStore.Downloads.IS_PENDING, 0);
                getContentResolver().update(uri, v, null, null);
            } else {
                if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                    pendienteDatos = datos; pendienteNombre = nombre; pendienteTipo = tipo;
                    requestPermissions(new String[] { Manifest.permission.WRITE_EXTERNAL_STORAGE }, PEDIR_PERMISO);
                    return;
                }
                File carpeta = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                if (!carpeta.exists() && !carpeta.mkdirs()) throw new Exception("sin carpeta");
                try (FileOutputStream out = new FileOutputStream(new File(carpeta, nombre))) { out.write(datos); }
            }
            Toast.makeText(this, "Guardado en Descargas: " + nombre, Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "No se pudo guardar «" + nombre + "»: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    /** Lee nombre, correos y teléfonos de la agenda (en segundo plano) y los manda a la página. Nada se guarda en la app. */
    private void leerContactos() {
        new Thread(() -> {
            JSONArray lista = new JSONArray();
            try {
                Map<String, JSONObject> porId = new LinkedHashMap<>();
                String[] cols = { ContactsContract.Data.CONTACT_ID, ContactsContract.Data.DISPLAY_NAME, ContactsContract.Data.MIMETYPE, ContactsContract.Data.DATA1 };
                String filtro = ContactsContract.Data.MIMETYPE + " IN (?, ?)";
                String[] tipos = { ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE, ContactsContract.CommonDataKinds.Phone.CONTENT_ITEM_TYPE };
                try (Cursor c = getContentResolver().query(ContactsContract.Data.CONTENT_URI, cols, filtro, tipos, ContactsContract.Data.DISPLAY_NAME + " ASC")) {
                    while (c != null && c.moveToNext() && porId.size() < 2000) {
                        String id = c.getString(0), nombre = c.getString(1), tipo = c.getString(2), dato = c.getString(3);
                        if (dato == null || dato.trim().isEmpty()) continue;
                        JSONObject o = porId.get(id);
                        if (o == null) {
                            o = new JSONObject();
                            o.put("nombre", nombre == null ? "" : nombre);
                            o.put("email", new JSONArray());
                            o.put("tel", new JSONArray());
                            porId.put(id, o);
                        }
                        o.getJSONArray(ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE.equals(tipo) ? "email" : "tel").put(dato.trim());
                    }
                }
                for (JSONObject o : porId.values()) lista.put(o);
                enviarContactos(lista.toString());
            } catch (Exception e) {
                enviarContactos("{\"error\":" + JSONObject.quote(String.valueOf(e.getMessage())) + "}");
            }
        }).start();
    }

    private void enviarContactos(String json) {
        runOnUiThread(() -> web.evaluateJavascript("window.ccContactosApp&&window.ccContactosApp(" + json + ")", null));
    }

    @Override
    public void onRequestPermissionsResult(int codigo, String[] permisos, int[] resultados) {
        super.onRequestPermissionsResult(codigo, permisos, resultados);
        if (codigo == PEDIR_CONTACTOS) {
            if (resultados.length > 0 && resultados[0] == PackageManager.PERMISSION_GRANTED) leerContactos();
            else enviarContactos("{\"error\":\"permiso\"}");
            return;
        }
        if (codigo == PEDIR_PERMISO && pendienteDatos != null) {
            byte[] d = pendienteDatos; pendienteDatos = null;
            if (resultados.length > 0 && resultados[0] == PackageManager.PERMISSION_GRANTED) guardarEnDescargas(pendienteNombre, d, pendienteTipo);
            else Toast.makeText(this, "Sin permiso para guardar en Descargas.", Toast.LENGTH_LONG).show();
        }
    }

    /** Descargas con dirección normal (archivos de tu cuenta, el APK…): con DownloadManager y la cookie de la sesión. */
    private void descargarUrl(String url, String agente, String disposicion, String tipo) {
        if (url.startsWith("blob:") || url.startsWith("data:")) return;   // las maneja JS_DESCARGAS
        try {
            String nombre = URLUtil.guessFileName(url, disposicion, tipo);
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(url));
            r.addRequestHeader("Cookie", CookieManager.getInstance().getCookie(url));
            r.addRequestHeader("User-Agent", agente);
            r.setMimeType(tipo);
            r.setTitle(nombre);
            r.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            r.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, nombre);
            DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
            if (dm != null) dm.enqueue(r);
            Toast.makeText(this, "Descargando " + nombre + "…", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            abrirEnNavegador(Uri.parse(url));
        }
    }

    private void abrirEnNavegador(Uri uri) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "No hay una app para abrir ese enlace.", Toast.LENGTH_LONG).show();
        }
    }

    /** codigocamp-app://entrar?c=CÓDIGO (después de entrar con Google en el navegador) -> abrir la sesión aquí. */
    private String urlDeEntrada(Intent intent) {
        if (intent == null || intent.getData() == null) return null;
        Uri d = intent.getData();
        if (!"codigocamp-app".equals(d.getScheme()) || !"entrar".equals(d.getHost())) return null;
        String c = d.getQueryParameter("c");
        if (c == null || !c.matches("[A-Za-z0-9_-]{20,100}")) return null;
        return base + "/api/auth/app/entrar?c=" + c;
    }

    /** Google no deja iniciar sesión dentro de una app: se hace en el navegador y vuelve con el código. */
    private boolean esInicioGoogle(Uri u) {
        String p = u.getPath() == null ? "" : u.getPath();
        return esDeCodigoCamp(u) && p.startsWith("/auth/google") && !p.contains("callback");
    }

    private boolean esDeCodigoCamp(Uri u) {
        Uri b = Uri.parse(base);
        return u.getHost() != null && u.getHost().equalsIgnoreCase(b.getHost());
    }

    // ------------------------------------------------------------------------- navegación ----
    final class Cliente extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView vista, WebResourceRequest pedido) {
            Uri u = pedido.getUrl();
            String esquema = u.getScheme() == null ? "" : u.getScheme();
            if ("codigocamp-widget".equals(esquema)) {   // enlace de la versión anterior: la app ya se conecta sola
                Toast.makeText(MainActivity.this, "El widget ya está conectado a esta app.", Toast.LENGTH_SHORT).show();
                return true;
            }
            if (esInicioGoogle(u)) {
                abrirEnNavegador(Uri.parse(base + "/auth/google/?app=1"));
                Toast.makeText(MainActivity.this, "Elige tu cuenta de Google y luego vuelve a la app.", Toast.LENGTH_LONG).show();
                return true;
            }
            if ("codigocamp-app".equals(esquema)) {
                Intent i = new Intent(Intent.ACTION_VIEW, u);
                String entrar = urlDeEntrada(i);
                if (entrar != null) vista.loadUrl(entrar);
                return true;
            }
            if (("http".equals(esquema) || "https".equals(esquema)) && esDeCodigoCamp(u)) return false;
            if ("intent".equals(esquema)) return true;
            abrirEnNavegador(u);   // GitHub, documentación y demás páginas: en el navegador del celular
            return true;
        }

        @Override
        public void onPageFinished(WebView vista, String url) {
            vista.evaluateJavascript(JS_DESCARGAS, null);
            CookieManager.getInstance().flush();
        }

        @Override
        public void onReceivedError(WebView vista, WebResourceRequest pedido, WebResourceError error) {
            if (!pedido.isForMainFrame()) return;
            String html = "<!DOCTYPE html><html lang=es><meta name=viewport content='width=device-width,initial-scale=1'>"
                    + "<body style='margin:0;min-height:100vh;display:grid;place-items:center;background:#0b1020;color:#e5eaff;font:16px system-ui;text-align:center;padding:24px'>"
                    + "<div><div style='font-size:48px'>📡</div><h2>Sin conexión con CódigoCamp</h2><p style='opacity:.75'>Revisa tu internet (o que el servidor esté encendido) y vuelve a intentarlo.</p>"
                    + "<button onclick=\"location.href='" + base + "/pages/inicio.html?app=1'\" style='margin-top:12px;padding:12px 22px;border:0;border-radius:10px;background:#caff4e;font-weight:800;font-size:16px'>Reintentar</button></div></body></html>";
            vista.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
        }
    }

    final class Cromo extends WebChromeClient {
        /** «Subir archivos» de Trabajo, foto de perfil, adjuntos del chat. */
        @Override
        public boolean onShowFileChooser(WebView vista, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (alElegirArchivos != null) alElegirArchivos.onReceiveValue(null);
            alElegirArchivos = callback;
            try {
                Intent i = params.createIntent();
                if (params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE) i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                startActivityForResult(Intent.createChooser(i, "Elegir archivos"), PEDIR_ARCHIVOS);
                return true;
            } catch (ActivityNotFoundException e) {
                alElegirArchivos = null;
                return false;
            }
        }

        /** window.open: ventana dentro de la app (así el inicio de sesión con GitHub vuelve a esta sesión). */
        @SuppressLint("SetJavaScriptEnabled")
        @Override
        public boolean onCreateWindow(WebView vista, boolean dialogo, boolean gesto, Message resultado) {
            WebView hija = new WebView(MainActivity.this);
            hija.getSettings().setJavaScriptEnabled(true);
            hija.getSettings().setDomStorageEnabled(true);
            hija.getSettings().setUserAgentString(vista.getSettings().getUserAgentString());
            Dialog ventana = new Dialog(MainActivity.this, android.R.style.Theme_Material_NoActionBar);
            ventana.requestWindowFeature(Window.FEATURE_NO_TITLE);
            ventana.setContentView(hija, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            hija.setWebViewClient(new WebViewClient());
            hija.setWebChromeClient(new WebChromeClient() {
                @Override
                public void onCloseWindow(WebView w) { ventana.dismiss(); }
            });
            ventana.setOnDismissListener(d -> hija.destroy());
            ventana.show();
            WebView.WebViewTransport t = (WebView.WebViewTransport) resultado.obj;
            t.setWebView(hija);
            resultado.sendToTarget();
            return true;
        }
    }

    @Override
    protected void onActivityResult(int codigo, int resultado, Intent datos) {
        super.onActivityResult(codigo, resultado, datos);
        if (codigo != PEDIR_ARCHIVOS || alElegirArchivos == null) return;
        Uri[] elegidos = null;
        if (resultado == RESULT_OK && datos != null) {
            if (datos.getClipData() != null) {
                int n = datos.getClipData().getItemCount();
                elegidos = new Uri[n];
                for (int i = 0; i < n; i++) elegidos[i] = datos.getClipData().getItemAt(i).getUri();
            } else if (datos.getData() != null) {
                elegidos = new Uri[] { datos.getData() };
            }
        }
        alElegirArchivos.onReceiveValue(elegidos);
        alElegirArchivos = null;
    }
}
