package com.codigocamp.widget;

import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.json.JSONObject;

/** Pantalla para pegar el enlace privado del widget (se abre desde el ícono o al agregar el widget). */
public class ConfigActivity extends Activity {
    private int widgetId = AppWidgetManager.INVALID_APPWIDGET_ID;

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        setContentView(R.layout.config);
        Intent intent = getIntent();
        if (intent.getExtras() != null) {
            widgetId = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID);
        }
        // Si se cancela al agregar el widget, Android no lo agrega.
        if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
            setResult(RESULT_CANCELED, new Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId));
        }
        // Al agregar otro widget cuando ya hay un enlace guardado: no hace falta volver a pegarlo.
        if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID && Datos.configurado(this)) {
            WidgetRacha.actualizarTodos(this);
            setResult(RESULT_OK, new Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId));
            finish();
            return;
        }
        EditText enlace = findViewById(R.id.enlace);
        Button guardar = findViewById(R.id.guardar);
        TextView resultado = findViewById(R.id.resultado);

        // «Conectar widget de Android» desde CódigoCamp (con la sesión ya iniciada): se guarda solo, sin escribir nada.
        if (Intent.ACTION_VIEW.equals(intent.getAction()) && intent.getData() != null) {
            String[] partes = Datos.interpretar(intent.getData().toString());
            if (partes != null) {
                Datos.guardar(this, partes[0], partes[1]);
                resultado.setText("Conectando con tu cuenta…");
                comprobar(guardar, resultado);
                return;
            }
        }
        // Enlace compartido desde el navegador (Compartir → CódigoCamp Widget) o copiado en el portapapeles.
        String compartido = Intent.ACTION_SEND.equals(intent.getAction()) ? intent.getStringExtra(Intent.EXTRA_TEXT) : null;
        if (compartido == null) {
            try {
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                ClipData clip = cm != null ? cm.getPrimaryClip() : null;
                if (clip != null && clip.getItemCount() > 0 && clip.getItemAt(0).getText() != null) {
                    String t = clip.getItemAt(0).getText().toString();
                    if (Datos.interpretar(t) != null) compartido = t;
                }
            } catch (Exception ignorado) { /* sin permiso para leer el portapapeles */ }
        }
        if (compartido != null) enlace.setText(compartido.trim());
        else if (Datos.configurado(this)) resultado.setText("Ya tienes un enlace guardado para " + Datos.base(this) + ". Pega otro para cambiarlo.");

        guardar.setOnClickListener(b -> {
            String[] partes = Datos.interpretar(enlace.getText().toString());
            if (partes == null) {
                resultado.setText("Ese enlace no es válido. Cópialo de CódigoCamp → Configuración → App y widgets.");
                return;
            }
            Datos.guardar(this, partes[0], partes[1]);
            resultado.setText("Comprobando…");
            comprobar(guardar, resultado);
        });
    }

    /** Prueba la conexión, actualiza los widgets y, si se estaba agregando uno, lo confirma. */
    private void comprobar(Button guardar, TextView resultado) {
            guardar.setEnabled(false);
            Handler principal = new Handler(Looper.getMainLooper());
            new Thread(() -> {
                String mensaje;
                boolean ok;
                try {
                    JSONObject d = Datos.descargar(this);
                    ok = true;
                    mensaje = "✅ Conectado a tu cuenta, " + d.optString("nombre", "") + " (racha de " + d.optInt("racha", 0) + "). Funciona hasta que cierres sesión en CódigoCamp. Ahora agrega el widget: mantén pulsada la pantalla de inicio → Widgets → CódigoCamp.";
                } catch (Exception e) {
                    ok = false;
                    mensaje = "⚠️ " + e.getMessage();
                }
                final boolean bien = ok;
                final String texto = mensaje;
                principal.post(() -> {
                    guardar.setEnabled(true);
                    resultado.setText(texto);
                    WidgetRacha.actualizarTodos(this);
                    if (bien && widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                        setResult(RESULT_OK, new Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId));
                        finish();
                    }
                });
            }).start();
    }
}
