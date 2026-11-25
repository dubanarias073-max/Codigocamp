# Firma de la app de Android (para que se pueda ACTUALIZAR)

Android solo instala una versión nueva encima de la que ya tienes si las dos están firmadas con **la misma llave**
y la nueva tiene un número de versión mayor. Antes GitHub firmaba cada APK con una llave de depuración nueva, por eso
salía «La app no se instaló: el paquete entra en conflicto con uno existente».

## Una sola vez
1. Guarda la carpeta `llave-android-codigocamp` (te la entregó Claude aparte) en un lugar seguro. **No la subas al repositorio.**
2. En GitHub: **Settings → Secrets and variables → Actions → New repository secret** y crea los 4 secrets que dice `SECRETS.txt`:
   `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.
3. Sube los cambios (o en **Actions → App de Android → Run workflow**). El APK sale firmado con tu llave.
4. En el celular **desinstala UNA última vez** la app vieja (estaba firmada con una llave al azar que ya no existe)
   e instala el APK nuevo.

## Desde ahí
Cada APK nuevo que salga de GitHub se instala **encima** del anterior (Actualizar), sin desinstalar y sin perder nada.
El número de versión sube solo en cada compilación.

Si pierdes la llave, ningún APK nuevo podrá actualizar la app instalada: guárdala bien.
