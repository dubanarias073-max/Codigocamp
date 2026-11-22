package com.codigocamp.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** Base de los widgets nuevos: descarga los datos en otro hilo (sin internet usa los últimos) y dibuja. */
abstract class WidgetBase extends AppWidgetProvider {
    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        final PendingResult pendiente = goAsync();
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
                d = Datos.ultimo(app);
            }
            try {
                for (int id : ids) manager.updateAppWidget(id, vistas(app, d, error, cerrada));
                despues(app, d);
            } finally {
                pendiente.finish();
            }
        }).start();
    }

    abstract RemoteViews vistas(Context c, JSONObject d, String error, boolean cerrada);

    void despues(Context c, JSONObject d) { }
}
