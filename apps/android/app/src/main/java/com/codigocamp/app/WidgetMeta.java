package com.codigocamp.app;

import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

/** Meta de hoy: XP de hoy con barra, encargos del día y la pregunta de Codi para animarte. */
public class WidgetMeta extends WidgetBase {
    @Override
    RemoteViews vistas(Context c, JSONObject d, String error, boolean cerrada) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_meta);
        v.setOnClickPendingIntent(R.id.raiz, Widgets.abrirApp(c, d != null ? d.optString("url_cofres", "") : "", 3));
        if (cerrada || d == null) {
            v.setTextViewText(R.id.xp, "—");
            v.setTextViewText(R.id.encargos, error != null ? error : "Abre CódigoCamp e inicia sesión.");
            v.setImageViewResource(R.id.codi, Codi.imagen("dormido"));
            return v;
        }
        int pct = d.optInt("progreso_hoy", 0);
        v.setTextViewText(R.id.xp, d.optInt("xp_hoy", 0) + " / " + d.optInt("meta_xp", 0) + " XP");
        v.setTextViewText(R.id.pct, pct + "%");
        v.setProgressBar(R.id.barra, 100, Math.min(100, pct), false);
        v.setImageViewResource(R.id.codi, Codi.imagen(pct >= 100 ? "celebra" : d.optString("animo", "feliz")));
        StringBuilder sb = new StringBuilder();
        JSONArray enc = d.optJSONArray("encargos");
        if (enc != null) {
            for (int i = 0; i < enc.length() && i < 3; i++) {
                JSONObject e = enc.optJSONObject(i);
                if (e == null) continue;
                if (sb.length() > 0) sb.append('\n');
                sb.append(e.optBoolean("completado") ? "✅ " : "▫️ ").append(e.optString("titulo"))
                  .append("  ").append(e.optInt("progreso")).append('/').append(e.optInt("meta"));
            }
        }
        v.setTextViewText(R.id.encargos, sb.length() > 0 ? sb.toString() : "Sin encargos hoy");
        return v;
    }
}
