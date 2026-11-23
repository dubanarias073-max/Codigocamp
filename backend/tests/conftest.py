"""Las pruebas nunca tocan los datos reales: el almacén de archivos (proyectos de Trabajo, fotos, adjuntos) se
redirige a una carpeta temporal. Antes, una prueba que registraba un usuario con id 1 podía borrar la carpeta real
backend/almacen_archivos/1 (el proyecto de la primera cuenta del servidor)."""
import atexit
import os
import shutil
import tempfile

_ALMACEN = tempfile.mkdtemp(prefix="cc-pruebas-")
os.environ["ALMACEN_ARCHIVOS"] = _ALMACEN
atexit.register(shutil.rmtree, _ALMACEN, ignore_errors=True)
