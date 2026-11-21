package com.codigocamp.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

import org.json.JSONObject;

/**
 * Datos del widget. El token lo entrega la propia app (la página de CódigoCamp abierta en la app lo manda por el puente
 * cada vez que se abre con la sesión iniciada), así el widget usa SIEMPRE la sesión de la app y no se desconecta.
 */
final class Datos {
    private static final String PREFS = "codigocamp";
    private static final String CLAVE_BASE = "base";
    private static final String CLAVE_TOKEN = "token";
    private static final String CLAVE_ULTIMO = "ultimo";
    /** El servidor dijo 401: la sesión se cerró. Se guarda para no seguir mostrando datos viejos como si nada. */
    private static final String CLAVE_CERRADA = "sesion_cerrada";

    private Datos() { }

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static void guardar(Context c, String base, String token) {
        SharedPreferences p = prefs(c);
        boolean igual = token.equals(p.getString(CLAVE_TOKEN, null)) && base.equals(p.getString(CLAVE_BASE, null));
        SharedPreferences.Editor e = p.edit().putString(CLAVE_BASE, base).putString(CLAVE_TOKEN, token).putBoolean(CLAVE_CERRADA, false);
        if (!igual) e.remove(CLAVE_ULTIMO);
        e.apply();
    }

    static void olvidar(Context c) {
        prefs(c).edit().remove(CLAVE_TOKEN).remove(CLAVE_ULTIMO).putBoolean(CLAVE_CERRADA, true).apply();
    }

    static boolean configurado(Context c) {
        return prefs(c).getString(CLAVE_TOKEN, null) != null;
    }

    static boolean sesionCerrada(Context c) {
        return prefs(c).getBoolean(CLAVE_CERRADA, false);
    }

    static String base(Context c) {
        String b = prefs(c).getString(CLAVE_BASE, null);
        return b != null ? b : BuildConfig.URL_SERVIDOR;
    }

    static JSONObject ultimo(Context c) {
        try {
            String s = prefs(c).getString(CLAVE_ULTIMO, null);
            return s == null ? null : new JSONObject(s);
        } catch (Exception e) {
            return null;
        }
    }

    /** Errores que significan «la sesión se cerró» (no un problema de red). */
    static final class SesionCerrada extends Exception {
        SesionCerrada(String m) { super(m); }
    }

    /** Descarga los datos (en un hilo aparte, nunca en el principal). */
    static JSONObject descargar(Context c) throws Exception {
        SharedPreferences p = prefs(c);
        String token = p.getString(CLAVE_TOKEN, null);
        if (token == null) throw new SesionCerrada("Abre CódigoCamp e inicia sesión.");
        URL url = new URL(base(c) + "/api/widget/?t=" + Uri.encode(token));
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setConnectTimeout(10000);
        con.setReadTimeout(10000);
        con.setRequestProperty("Accept", "application/json");
        con.setRequestProperty("User-Agent", "CodigoCampApp/2.0 Android");
        try {
            int estado = con.getResponseCode();
            InputStream in = estado >= 400 ? con.getErrorStream() : con.getInputStream();
            String cuerpo = leer(in);
            if (estado == 401) {
                olvidar(c);
                throw new SesionCerrada("Tu sesión se cerró. Abre CódigoCamp e inicia sesión.");
            }
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
