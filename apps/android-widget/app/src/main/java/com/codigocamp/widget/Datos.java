package com.codigocamp.widget;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

import org.json.JSONObject;

/** Guarda el enlace privado del widget y descarga los datos de /api/widget/?t=… */
final class Datos {
    private static final String PREFS = "codigocamp";
    private static final String CLAVE_BASE = "base";
    private static final String CLAVE_TOKEN = "token";
    private static final String CLAVE_ULTIMO = "ultimo";

    private Datos() { }

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    /**
     * Acepta cualquiera de los enlaces que muestra CódigoCamp:
     *   https://servidor/pages/widget.html?t=TOKEN · https://servidor/api/widget/?t=TOKEN · …/scriptable.js?t=TOKEN
     * Devuelve null si no es válido.
     */
    static String[] interpretar(String texto) {
        if (texto == null) return null;
        String t = texto.trim();
        int i = t.indexOf("http");
        if (i > 0 && !t.startsWith("codigocamp-widget:")) t = t.substring(i);
        int esp = t.indexOf(' ');
        if (esp > 0) t = t.substring(0, esp);
        try {
            Uri u = Uri.parse(t);
            String token = u.getQueryParameter("t");
            if ("codigocamp-widget".equals(u.getScheme())) {
                // Enlace de «Conectar widget de Android»: trae el servidor y el token de la sesión abierta.
                String b = u.getQueryParameter("base");
                if (b == null || token == null || token.length() < 20) return null;
                Uri ub = Uri.parse(b);
                if (!"https".equals(ub.getScheme()) && !"http".equals(ub.getScheme())) return null;
                return new String[] { ub.getScheme() + "://" + ub.getEncodedAuthority(), token };
            }
            String esquema = u.getScheme();
            String host = u.getEncodedAuthority();
            if (token == null || token.length() < 20 || host == null || esquema == null) return null;
            if (!"https".equals(esquema) && !"http".equals(esquema)) return null;
            return new String[] { esquema + "://" + host, token };
        } catch (Exception e) {
            return null;
        }
    }

    static void guardar(Context c, String base, String token) {
        prefs(c).edit().putString(CLAVE_BASE, base).putString(CLAVE_TOKEN, token).remove(CLAVE_ULTIMO).apply();
    }

    static boolean configurado(Context c) {
        return prefs(c).getString(CLAVE_TOKEN, null) != null;
    }

    static String base(Context c) {
        return prefs(c).getString(CLAVE_BASE, "");
    }

    static JSONObject ultimo(Context c) {
        try {
            String s = prefs(c).getString(CLAVE_ULTIMO, null);
            return s == null ? null : new JSONObject(s);
        } catch (Exception e) {
            return null;
        }
    }

    /** Descarga los datos (en un hilo aparte: nunca en el hilo principal). Lanza Exception con un mensaje legible. */
    static JSONObject descargar(Context c) throws Exception {
        SharedPreferences p = prefs(c);
        String base = p.getString(CLAVE_BASE, null);
        String token = p.getString(CLAVE_TOKEN, null);
        if (base == null || token == null) throw new Exception("Abre CódigoCamp (con tu sesión) → Configuración → App y widgets → «Conectar widget de Android».");
        URL url = new URL(base + "/api/widget/?t=" + Uri.encode(token));
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setConnectTimeout(8000);
        con.setReadTimeout(8000);
        con.setRequestProperty("Accept", "application/json");
        con.setRequestProperty("User-Agent", "CodigoCampWidget/1.0 Android");
        try {
            int estado = con.getResponseCode();
            InputStream in = estado >= 400 ? con.getErrorStream() : con.getInputStream();
            String cuerpo = leer(in);
            if (estado == 401) throw new Exception("Tu sesión de CódigoCamp se cerró. Inicia sesión y pulsa «Conectar widget de Android».");
            if (estado != 200) throw new Exception("El servidor respondió " + estado);
            JSONObject d = new JSONObject(cuerpo);
            p.edit().putString(CLAVE_ULTIMO, cuerpo).apply();
            return d;
        } finally {
            con.disconnect();
        }
    }

    private static String leer(InputStream in) throws Exception {
        if (in == null) return "";
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        in.close();
        return new String(out.toByteArray(), StandardCharsets.UTF_8);
    }
}
