package com.codigocamp.app;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.util.Calendar;

/** Utilidades comunes de todos los widgets. */
final class Widgets {
    static final long TRES_HORAS = 3L * 60 * 60 * 1000;

    private Widgets() { }

    /** Actualiza todos los widgets de CódigoCamp (al abrir la app, iniciar o cerrar sesión). */
    static void actualizarTodos(Context c) {
        WidgetRacha.actualizarTodos(c);
        actualizar(c, WidgetReloj.class);
        actualizar(c, WidgetCodi.class);
        actualizar(c, WidgetMeta.class);
    }

    static void actualizar(Context c, Class<?> clase) {
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        int[] ids = m.getAppWidgetIds(new ComponentName(c, clase));
        if (ids.length == 0) return;
        Intent i = new Intent(c, clase);
        i.setAction(AppWidgetManager.ACTION_APPWIDGET_UPDATE);
        i.putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, ids);
        c.sendBroadcast(i);
    }

    /** Milisegundos (reloj del sistema) en que termina hoy: la medianoche del teléfono. */
    static long finDelDia() {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_YEAR, 1);
        cal.set(Calendar.HOUR_OF_DAY, 0);
        cal.set(Calendar.MINUTE, 0);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        return cal.getTimeInMillis();
    }

    /** Pide que el widget se vuelva a dibujar en un momento (cuando faltan 3 horas y a medianoche). */
    static void programar(Context c, Class<?> clase, long cuando, int codigo) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null || cuando <= System.currentTimeMillis()) return;
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        int[] ids = m.getAppWidgetIds(new ComponentName(c, clase));
        Intent i = new Intent(c, clase);
        i.setAction(AppWidgetManager.ACTION_APPWIDGET_UPDATE);
        i.putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, ids);
        PendingIntent pi = PendingIntent.getBroadcast(c, codigo, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        // Sin permiso de alarmas exactas: Android lo entrega cerca de la hora pedida (suficiente para cambiar de color).
        if (Build.VERSION.SDK_INT >= 23) am.setAndAllowWhileIdle(AlarmManager.RTC, cuando, pi);
        else am.set(AlarmManager.RTC, cuando, pi);
    }

    /** Tocar el widget abre la app (en la página para practicar si hay datos). */
    static PendingIntent abrirApp(Context c, String url, int codigo) {
        Intent abrir = new Intent(c, MainActivity.class);
        if (url != null && !url.isEmpty()) abrir.putExtra(MainActivity.EXTRA_URL, url);
        abrir.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(c, codigo, abrir, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}
