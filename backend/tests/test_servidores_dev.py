"""php -S real para Trabajo: arranca, responde con sesiones/POST/headers y se apaga."""
import shutil
import unittest

from servicios import servidores_dev as sd


@unittest.skipUnless(shutil.which("php"), "PHP no está instalado")
class PhpServidorTest(unittest.TestCase):
    UID = 987654

    def tearDown(self):
        sd.detener(self.UID)

    def test_php_real(self):
        sd.iniciar(self.UID, [
            {"ruta": "index.php", "contenido": "<?php session_start(); $_SESSION['n']=($_SESSION['n']??0)+1; header('X-Hola: si'); echo 'visita '.$_SESSION['n'];"},
            {"ruta": "api/eco.php", "contenido": "<?php http_response_code(201); echo json_encode($_POST);"},
        ])
        estado, cab, cuerpo, _ = sd.pedir(self.UID, "GET", "/", [], b"")
        self.assertEqual((estado, cuerpo), (200, b"visita 1"))
        self.assertEqual(dict(cab).get("X-Hola"), "si")
        cookie = dict(cab)["Set-Cookie"].split(";")[0]
        _, _, cuerpo, _ = sd.pedir(self.UID, "GET", "/", [("Cookie", cookie)], b"")
        self.assertEqual(cuerpo, b"visita 2")
        estado, _, cuerpo, _ = sd.pedir(self.UID, "POST", "/api/eco.php", [("Content-Type", "application/x-www-form-urlencoded")], b"a=1")
        self.assertEqual((estado, cuerpo), (201, b'{"a":"1"}'))

    def test_no_sale_de_la_carpeta(self):
        with self.assertRaises(sd.ErrorServidor):
            sd.iniciar(self.UID, [{"ruta": "index.php", "contenido": "<?php echo 1;"}], docroot="../../etc")
        self.assertFalse(sd.detener(self.UID))


if __name__ == "__main__":
    unittest.main()
