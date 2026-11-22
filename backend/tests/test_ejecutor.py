"""Ejecutor de Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin y Ruby: local, Piston y en línea (Wandbox / Kotlin)."""
import json
import shutil
import subprocess
import unittest
from unittest import mock

from servicios import ejecutor as E


def sin_locales():
    """Simula un PC sin compiladores instalados."""
    falta = {"java": "Java (JDK)", "c": "gcc", "cpp": "g++", "csharp": ".NET SDK (dotnet)", "php": "php", "go": "go",
             "rust": "rustc", "swift": "swift", "kotlin": "kotlinc", "ruby": "ruby"}
    return mock.patch.dict(E.LENGUAJES, {k: {**v, "f": (lambda n: lambda c, d, e: (None, n))(falta[k])} for k, v in E.LENGUAJES.items()})


class PrepararCodigo(unittest.TestCase):
    def test_unir_java_quita_package_y_public_de_las_demas(self):
        principal = "import java.util.*;\npublic class Main { public static void main(String[] a) { new Persona(); } }"
        codigo = E.preparar("java", principal, [{"nombre": "Persona.java", "contenido": "package app;\nimport java.util.*;\npublic class Persona {}"}])
        self.assertEqual(codigo.count("import java.util.*;"), 1)
        self.assertNotIn("package", codigo)
        self.assertIn("public class Main", codigo)
        self.assertIn("\nclass Persona", codigo)

    def test_clase_con_main(self):
        self.assertEqual(E._clase_java("class A {}\npublic class Saludo { public static void main(String[] x) {} }"), "Saludo")
        self.assertEqual(E._clase_java("class Util {}\nclass App { static void main(String[] x) {} }"), "App")

    def test_unir_c_mete_cabeceras_y_su_implementacion(self):
        codigo = E.unir_c('#include <stdio.h>\n#include "m.h"\nint main(){}', [
            {"nombre": "m.h", "contenido": "int doble(int);"}, {"nombre": "m.c", "contenido": "int doble(int x){return 2*x;}"}])
        self.assertIn("int doble(int);", codigo)
        self.assertIn("return 2*x;", codigo)
        self.assertIn("#include <stdio.h>", codigo)

    def test_a_ascii_solo_toca_cadenas_y_comentarios(self):
        for leng in ("c", "cpp", "go", "rust", "php", "ruby", "swift", "csharp", "kotlin", "java"):
            r = E.a_ascii(leng, '// canción\nprint("¡ñandú!")')
            self.assertTrue(all(ord(c) < 128 for c in r), leng)
        self.assertEqual(E.a_ascii("rust", 'let s = "ñ";'), 'let s = "\\u{f1}";')
        self.assertEqual(E.a_ascii("c", 'puts("ñ");'), 'puts("\\303\\261");')

    def test_mojibake(self):
        self.assertEqual(E._arreglar_mojibake("cÃ³mo estÃ¡s"), "cómo estás")
        self.assertEqual(E._arreglar_mojibake("cómo"), "cómo")


@unittest.skipUnless(shutil.which("gcc"), "sin gcc")
class EscapesCompilan(unittest.TestCase):
    def test_escapes_de_c_imprimen_lo_mismo(self):
        import tempfile, os
        d = tempfile.mkdtemp()
        open(os.path.join(d, "p.c"), "w").write(E.a_ascii("c", '#include <stdio.h>\nint main(){ printf("¿Cómo estás? ñ —\\n"); }'))
        subprocess.run(["gcc", "p.c", "-o", "p"], cwd=d, check=True)
        self.assertEqual(subprocess.run([os.path.join(d, "p")], capture_output=True).stdout.decode(), "¿Cómo estás? ñ —\n")


class EnLinea(unittest.TestCase):
    def falso(self, respuestas):
        """respuestas: lista de dicts (o excepciones) que irá devolviendo compile.json."""
        llamadas = []

        def pedir(url, cuerpo=None, cab=None, tiempo=0):
            if url.endswith("/api/list.json"):
                return [{"name": n} for ls in E.WANDBOX_PREFERIDOS.values() for n in ls]
            llamadas.append(json.loads(cuerpo))
            r = respuestas.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        E._lista.update(cuando=0.0, nombres=set())
        return mock.patch.object(E, "_pedir_json", pedir), llamadas

    def test_sin_compilador_usa_wandbox_con_entrada(self):
        p, llamadas = self.falso([{"status": "0", "program_message": "Hola Ana\n"}])
        with sin_locales(), p:
            r = E.ejecutar("php", '<?php echo "Hola ".trim(fgets(STDIN));', "Ana")
        self.assertEqual(r, {"salida": "Hola Ana\n", "error": False, "donde": "en_linea"})
        self.assertEqual(llamadas[0]["stdin"], "Ana\n")
        self.assertEqual(llamadas[0]["compiler"], "php-8.3.12")

    def test_java_va_sin_public_y_en_ascii(self):
        p, llamadas = self.falso([{"status": "0", "program_message": "¡Hola!\n"}])
        with sin_locales(), p:
            E.ejecutar("java", 'public class Main { public static void main(String[] a) { System.out.println("¡Hola!"); } }')
        enviado = llamadas[0]["code"]
        self.assertNotIn("public class Main", enviado)
        self.assertTrue(all(ord(c) < 128 for c in enviado))
        self.assertIn("UTF-8", enviado)

    def test_error_de_compilacion_se_muestra(self):
        p, _ = self.falso([{"status": "1", "compiler_error": "prog.c:1: error: falta ;", "compiler_message": "prog.c:1: error: falta ;"}])
        with sin_locales(), p:
            r = E.ejecutar("c", "int main(){ return 0 }")
        self.assertTrue(r["error"])
        self.assertIn("main.c:1: error", r["salida"])

    def test_si_una_version_falla_prueba_otra(self):
        p, llamadas = self.falso([E._FalloServicio("timeout"), {"status": "0", "program_message": "ok\n"}])
        with sin_locales(), p:
            r = E.ejecutar("go", 'package main\nfunc main(){}')
        self.assertEqual(r["salida"], "ok\n")
        self.assertNotEqual(llamadas[0]["compiler"], llamadas[1]["compiler"])

    def test_sin_internet_explica_que_hacer(self):
        p, _ = self.falso([E._FalloServicio("x")] * 5)
        with sin_locales(), p:
            r = E.ejecutar("rust", "fn main(){}")
        self.assertTrue(r["error"])
        self.assertIn("no respondieron", r["salida"])
        self.assertIn("rustup", r["salida"])

    def test_apagado_por_env(self):
        with sin_locales(), mock.patch.dict("os.environ", {"EJECUCION_EN_LINEA": "0"}):
            r = E.ejecutar("ruby", "puts 1")
        self.assertIn("EJECUCION_EN_LINEA=0", r["salida"])

    def test_kotlin_playground(self):
        def pedir(url, cuerpo=None, cab=None, tiempo=0):
            if url.endswith("/versions"):
                return [{"version": "2.1.20", "latestStable": True}]
            self.assertIn("/api/2.1.20/compiler/run", url)
            texto = json.loads(cuerpo)["files"][0]["text"]
            if "error" in texto:
                return {"errors": {"File.kt": [{"severity": "ERROR", "message": "Unresolved reference 'x'.",
                                                "interval": {"start": {"line": 1, "ch": 4}}}]}, "text": ""}
            return {"errors": {"File.kt": []}, "exception": None, "text": "<outStream>Hola Kotlin\n</outStream>"}
        with sin_locales(), mock.patch.object(E, "_pedir_json", pedir):
            self.assertEqual(E.ejecutar("kotlin", 'fun main() { println("Hola Kotlin") }')["salida"], "Hola Kotlin\n")
            r = E.ejecutar("kotlin", "fun main() {\n    error(x)\n}")
        self.assertTrue(r["error"])
        self.assertIn("main.kt:2:5: error: Unresolved reference", r["salida"])


@unittest.skipUnless(shutil.which("javac") and shutil.which("java"), "sin JDK")
class JavaLocal(unittest.TestCase):
    def test_varias_clases_y_entrada(self):
        r = E.ejecutar("java", 'import java.util.Scanner;\npublic class Main { public static void main(String[] a){ '
                               'System.out.println("Hola " + new Scanner(System.in).nextLine() + " " + new P().x); } }',
                       "Ñandú", [{"nombre": "P.java", "contenido": "public class P { int x = 7; }"}])
        self.assertEqual(r["salida"], "Hola Ñandú 7\n")
        self.assertEqual(r["donde"], "local")


@unittest.skipUnless(shutil.which("go"), "sin Go")
class GoLocal(unittest.TestCase):
    def test_go_run_compila_aunque_escriba_archivos_grandes(self):
        r = E.ejecutar("go", 'package main\nimport "fmt"\nfunc main(){ var s string; fmt.Scanln(&s); fmt.Println("hola", s) }', "Go")
        self.assertEqual(r["salida"], "hola Go\n")


if __name__ == "__main__":
    unittest.main()
