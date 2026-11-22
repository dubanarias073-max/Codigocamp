package com.codigocamp.app;

import android.content.Context;
import android.os.SystemClock;
import android.widget.RemoteViews;

import org.json.JSONObject;

/**
 * Reloj del día (como Duolingo): cuenta regresiva de las horas que quedan antes de medianoche para salvar la racha.
 * Avanza solo cada segundo y se pone ROJO cuando faltan menos de 3 horas y aún no practicaste.
 */
public class WidgetReloj extends WidgetBase {
    @Override
    RemoteViews vistas(Context c, JSONObject d, String error, boolean cerrada) {
        long ahora = System.currentTimeMillis();
        long fin = Widgets.finDelDia();
        long quedan = fin - ahora;
        boolean practicado = d != null && d.optBoolean("practicado_hoy");
        int racha = d != null ? d.optInt("racha", 0) : 0;
        boolean urgente = !practicado && quedan <= Widgets.TRES_HORAS;

        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_reloj);
        v.setOnClickPendingIntent(R.id.raiz, Widgets.abrirApp(c, d != null ? d.optString("url_practicar", "") : "", 1));
        v.setInt(R.id.raiz, "setBackgroundResource", urgente ? R.drawable.fondo_widget_rojo : practicado ? R.drawable.fondo_widget_verde : R.drawable.fondo_widget);

        // Cronómetro hacia atrás: Android lo hace avanzar solo, sin gastar batería en actualizaciones.
        v.setChronometer(R.id.cronometro, SystemClock.elapsedRealtime() + quedan, null, true);
        v.setChronometerCountDown(R.id.cronometro, true);
        int color = practicado ? 0xFFCAFF4E : urgente ? 0xFFFF5A6E : 0xFFFF9F1C;
        v.setTextColor(R.id.cronometro, color);
        v.setProgressBar(R.id.barra, 1000, (int) Math.min(1000, Math.max(0, 1000 - quedan * 1000 / (24L * 3600 * 1000))), false);

        String animo = practicado ? (racha >= 7 ? "fuego" : "feliz") : urgente ? "alarma" : racha > 0 ? "preocupado" : "dormido";
        v.setImageViewResource(R.id.codi, Codi.imagen(animo));
        if (cerrada || d == null) {
            v.setTextViewText(R.id.titulo, "CódigoCamp · Reloj del día");
            v.setTextViewText(R.id.estado, error != null ? error : "Abre CódigoCamp e inicia sesión.");
            v.setTextColor(R.id.estado, 0xFFFF9F1C);
            return v;
        }
        v.setTextViewText(R.id.titulo, practicado ? "Tu racha está a salvo hoy" : racha > 0 ? "Quedan para salvar tu racha de " + racha + " 🔥" : "Quedan para empezar tu racha");
        v.setTextViewText(R.id.estado, practicado ? "✅ Ya practicaste. Mañana empieza otro día."
                : urgente ? "🔴 ¡Menos de 3 horas! Haz una lección ya." : "⏳ El día termina a medianoche.");
        v.setTextColor(R.id.estado, color);
        return v;
    }

    @Override
    void despues(Context c, JSONObject d) {
        long fin = Widgets.finDelDia();
        // Redibujar justo al entrar en las últimas 3 horas (rojo) y al empezar el día siguiente.
        Widgets.programar(c, WidgetReloj.class, fin - Widgets.TRES_HORAS + 1000, 31);
        Widgets.programar(c, WidgetReloj.class, fin + 5000, 32);
    }
}
