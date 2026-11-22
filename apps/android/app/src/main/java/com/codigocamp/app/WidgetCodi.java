package com.codigocamp.app;

import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** Codi en tu pantalla de inicio: cambia de ánimo con tu racha y la hora, y te dice cuánto queda del día. */
public class WidgetCodi extends WidgetBase {
    @Override
    RemoteViews vistas(Context c, JSONObject d, String error, boolean cerrada) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_codi);
        v.setOnClickPendingIntent(R.id.raiz, Widgets.abrirApp(c, d != null ? d.optString("url_practicar", "") : "", 2));
        if (cerrada || d == null) {
            v.setImageViewResource(R.id.codi, Codi.imagen("dormido"));
            v.setTextViewText(R.id.racha, "—");
            v.setTextViewText(R.id.frase, error != null ? error : "Abre CódigoCamp e inicia sesión.");
            return v;
        }
        String animo = d.optString("animo", "feliz");
        boolean practicado = d.optBoolean("practicado_hoy");
        int racha = d.optInt("racha", 0);
        v.setImageViewResource(R.id.codi, Codi.imagen(animo));
        v.setTextViewText(R.id.racha, "🔥 " + racha);
        v.setTextColor(R.id.racha, "alarma".equals(animo) ? 0xFFFF5A6E : 0xFFFF9F1C);
        v.setTextViewText(R.id.frase, Codi.frase(animo, practicado, racha));
        return v;
    }

    @Override
    void despues(Context c, JSONObject d) {
        long fin = Widgets.finDelDia();
        Widgets.programar(c, WidgetCodi.class, fin - Widgets.TRES_HORAS + 1000, 41);
        Widgets.programar(c, WidgetCodi.class, fin + 5000, 42);
    }
}
