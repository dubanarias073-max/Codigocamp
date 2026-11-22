package com.codigocamp.app;

/** Codi, la mascota de CódigoCamp: la imagen que va en los widgets según su ánimo. */
final class Codi {
    private Codi() { }

    static int imagen(String animo) {
        if (animo == null) return R.drawable.codi_feliz;
        switch (animo) {
            case "fuego": return R.drawable.codi_fuego;
            case "preocupado": return R.drawable.codi_preocupado;
            case "alarma": return R.drawable.codi_alarma;
            case "dormido": return R.drawable.codi_dormido;
            case "saludo": return R.drawable.codi_saludo;
            case "pensando": return R.drawable.codi_pensando;
            case "triste": return R.drawable.codi_triste;
            case "celebra": return R.drawable.codi_celebra;
            default: return R.drawable.codi_feliz;
        }
    }

    static String frase(String animo, boolean practicado, int racha) {
        if ("fuego".equals(animo)) return "¡Estás en llamas! Sigue así";
        if ("feliz".equals(animo)) return "¡Hoy cumpliste! Nos vemos mañana";
        if ("alarma".equals(animo)) return "¡Tu racha está en peligro!";
        if ("preocupado".equals(animo)) return "¿Practicamos un ratito hoy?";
        if ("dormido".equals(animo)) return racha > 0 ? "Zzz… despiértame con una lección" : "¿Hoy empezamos una racha?";
        return practicado ? "¡Bien hecho!" : "¿Listo para programar?";
    }
}
