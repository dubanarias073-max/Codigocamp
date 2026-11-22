package com.codigocamp.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

/** Widget de pantalla de inicio: racha, semana, meta de hoy, vidas y diamantes. Se actualiza cada 30 minutos y al abrir la app. */
public class WidgetRacha extends AppWidgetProvider {
    private static final int[] LETRAS = { R.id.l0, R.id.l1, R.id.l2, R.id.l3, R.id.l4, R.id.l5, R.id.l6 };
    private static final int[] ICONOS = { R.id.i0, R.id.i1, R.id.i2, R.id.i3, R.id.i4, R.id.i5, R.id.i6 };

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        actualizar(context, manager, ids, goAsync());
    }

    /** Actualiza todos los widgets (lo llama la app al iniciar o cerrar sesión). */
    static void actualizarTodos(Context context) {
        AppWidgetManager m = AppWidgetManager.getInstance(context);
        int[] ids = m.getAppWidgetIds(new ComponentName(context, WidgetRacha.class));
        if (ids.length > 0) actualizar(context, m, ids, null);
    }

    private static void actualizar(Context context, AppWidgetManager manager, int[] ids, PendingResult pendiente) {
        final Context app = context.getApplicationContext();
        new Thread(() -> {
            JSONObject d = null;
            String error = null;
            boolean cerrada = false;
            try {
                d = Datos.descargar(app);
            } catch (Datos.SesionCerrada e) {
                cerrada = true;
                error = e.getMessage();
            } catch (Exception e) {
                error = e.getMessage();
                d = Datos.ultimo(app);   // sin internet: se muestran los últimos datos
            }
            try {
                for (int id : ids) manager.updateAppWidget(id, vistas(app, d, error, cerrada));
            } finally {
                if (pendiente != null) pendiente.finish();
            }
        }).start();
    }

    private static RemoteViews vistas(Context c, JSONObject d, String error, boolean cerrada) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_racha);
        // Tocar el widget abre la app (en la página para practicar si hay datos)
        Intent abrir = new Intent(c, MainActivity.class);
        if (d != null) abrir.putExtra(MainActivity.EXTRA_URL, d.optString("url_practicar", ""));
        abrir.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(c, 0, abrir, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.raiz, pi);

        if (cerrada || d == null) {
            v.setTextViewText(R.id.racha, "—");
            v.setTextViewText(R.id.vidas, "");
            v.setTextViewText(R.id.meta, "");
            v.setTextViewText(R.id.estado, error != null ? error : "Abre CódigoCamp e inicia sesión.");
            v.setTextColor(R.id.estado, cerrada ? 0xFFFF9F1C : 0xFFFF6B6B);
            return v;
        }
        int racha = d.optInt("racha", 0);
        v.setTextViewText(R.id.titulo, "CódigoCamp · " + d.optString("nombre", ""));
        v.setTextViewText(R.id.vidas, "❤️ " + d.optInt("vidas", 0) + "  💎 " + d.optInt("diamantes", 0));
        v.setTextViewText(R.id.racha, String.valueOf(racha));
        v.setTextViewText(R.id.rachaTxt, racha == 1 ? "día de racha" : "días de racha");
        JSONArray encargos = d.optJSONArray("encargos");
        String lineaEncargos = encargos != null && encargos.length() > 0 ? "\n📋 " + d.optInt("encargos_hechos", 0) + "/" + encargos.length() + " encargos" : "";
        v.setTextViewText(R.id.meta, "🎯 " + d.optInt("xp_hoy", 0) + "/" + d.optInt("meta_xp", 0) + " XP\n" + d.optInt("progreso_hoy", 0) + "% de hoy" + lineaEncargos);
        // Codi, la mascota (igual que en el widget web): cambia con tu racha y la hora
        v.setImageViewResource(R.id.codi, Codi.imagen(d.optString("animo", "feliz")));
        JSONArray semana = d.optJSONArray("semana");
        for (int i = 0; i < 7; i++) {
            JSONObject dia = semana != null ? semana.optJSONObject(i) : null;
            if (dia == null) continue;
            v.setTextViewText(LETRAS[i], dia.optString("letra"));
            v.setTextColor(LETRAS[i], dia.optBoolean("hoy") ? 0xFFE5EAFF : 0xFF8B95B8);
            v.setTextViewText(ICONOS[i], dia.optString("icono"));
        }
        String estado = error != null ? "Sin conexión · " + d.optString("actualizado", "") : d.optString("estado", "");
        v.setTextViewText(R.id.estado, estado);
        v.setTextColor(R.id.estado, d.optBoolean("practicado_hoy") ? 0xFFCAFF4E : 0xFFFF9F1C);
        return v;
    }
}
