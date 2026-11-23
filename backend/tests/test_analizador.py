"""Detector de errores de Trabajo: errores reales sí; lo que vive en el resto del proyecto o en las librerías del equipo, no."""
import shutil
import unittest

from servicios.analizador import analizar


def mensajes(codigo, lang):
    return [p["mensaje"] for p in analizar(codigo, f"x.{lang}", lang)]


class AnalizadorTest(unittest.TestCase):
    def test_python(self):
        self.assertTrue(any("«:»" in m for m in mensajes("def f(a)\n    return a\n", "py")))
        self.assertEqual(mensajes("import requests\nimport numpy as np\nfrom servicios.db import conectar\nprint(requests, np, conectar)\n", "py"), [])

    @unittest.skipUnless(shutil.which("javac"), "sin javac")
    def test_java_de_un_proyecto_real(self):
        codigo = ("import org.springframework.boot.SpringApplication;\npublic class App { public static void main(String[] a) {\n"
                  "SpringApplication.run(App.class, a); Usuario u = new Usuario(); } }\n")
        self.assertEqual(mensajes(codigo, "java"), [])                       # Spring y Usuario.java están en tu proyecto
        self.assertIn("Falta «;»", mensajes("public class App { void f() { int x = 5 } }\n", "java"))

    @unittest.skipUnless(shutil.which("gcc"), "sin gcc")
    def test_c_con_includes_de_tu_equipo(self):
        codigo = '#include <stdio.h>\n#include <mysql/mysql.h>\n#include "miarchivo.h"\nint main(){ MYSQL *c = mysql_init(NULL); printf("%p", c); return 0; }\n'
        self.assertEqual([m for m in mensajes(codigo, "c") if "no se usa" not in m], [])
        self.assertTrue(any("«;»" in m for m in mensajes('#include "modelo.h"\nint main(){ int x = 5 return x; }\n', "c")))

    @unittest.skipUnless(shutil.which("javac"), "sin javac")
    def test_java_errores_al_escribir_clases_conocidas(self):
        m = mensajes("public class App { public static void main(String[] a){ Sytem.out.println(1); } }\n", "java")
        self.assertTrue(any("¿Quisiste decir «System»?" in x for x in m), m)
