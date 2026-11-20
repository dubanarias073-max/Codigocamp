package com.codigocamp.widget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

/** Widget de pantalla de inicio: racha, semana, meta de hoy, vidas y diamantes. Se actualiza cada 30 minutos. */
public class WidgetRacha extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        actualizar(context, manager, ids, goAsync());
    }

    /** Actualiza todos los widgets (lo llama también la pantalla de configuración). */
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
            try {
                d = Datos.descargar(app);
            } catch (Exception e) {
                error = e.getMessage();
                d = Datos.ultimo(app);
            }
            try {
                for (int id : ids) manager.updateAppWidget(id, vistas(app, d, error));
            } finally {
                if (pendiente != null) pendiente.finish();
            }
        }).start();
    }

    private static RemoteViews vistas(Context c, JSONObject d, String error) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_racha);
        String base = Datos.base(c);
        Intent abrir;
        if (!Datos.configurado(c)) {
            abrir = new Intent(c, ConfigActivity.class);
            v.setTextViewText(R.id.estado, "Toca para pegar tu enlace de CódigoCamp");
        } else {
            String url = d != null ? d.optString("url_practicar", base + "/pages/inicio.html?app=1") : base + "/pages/inicio.html?app=1";
            abrir = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        }
        abrir.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        PendingIntent pi = PendingIntent.getActivity(c, 0, abrir, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.raiz, pi);

        if (d != null) {
            int racha = d.optInt("racha", 0);
            v.setTextViewText(R.id.titulo, "CódigoCamp · " + d.optString("nombre", ""));
            v.setTextViewText(R.id.vidas, "❤️ " + d.optInt("vidas", 0) + "   💎 " + d.optInt("diamantes", 0));
            v.setTextViewText(R.id.racha, String.valueOf(racha));
            v.setTextViewText(R.id.rachaTxt, racha == 1 ? "día de racha" : "días de racha");
            v.setTextViewText(R.id.meta, "🎯 " + d.optInt("xp_hoy", 0) + "/" + d.optInt("meta_xp", 0) + " XP\n" + d.optInt("progreso_hoy", 0) + "% de hoy");
            StringBuilder letras = new StringBuilder();
            StringBuilder iconos = new StringBuilder();
            JSONArray semana = d.optJSONArray("semana");
            if (semana != null) {
                for (int i = 0; i < semana.length(); i++) {
                    JSONObject dia = semana.optJSONObject(i);
                    if (dia == null) continue;
                    letras.append(dia.optString("letra")).append(i < semana.length() - 1 ? "    " : "");
                    iconos.append(dia.optString("icono")).append(i < semana.length() - 1 ? "  " : "");
                }
            }
            v.setTextViewText(R.id.semana, letras + "\n" + iconos);
            String estado = error != null ? "Sin conexión · " + d.optString("actualizado", "") : d.optString("estado", "");
            v.setTextViewText(R.id.estado, estado);
            v.setTextColor(R.id.estado, d.optBoolean("practicado_hoy") ? 0xFFCAFF4E : 0xFFFF9F1C);
        } else if (error != null && Datos.configurado(c)) {
            v.setTextViewText(R.id.estado, error);
            v.setTextColor(R.id.estado, 0xFFFF6B6B);
        }
        return v;
    }
}
