# Librerías incluidas (sin CDN)

Se sirven desde el propio CódigoCamp para que el espacio Trabajo funcione aunque el colegio o la red bloqueen los CDN.

| Carpeta | Qué es | Versión | Licencia |
|---|---|---|---|
| `monaco/vs` | Monaco Editor, el editor de VS Code (versión `min`, solo con la traducción al español) | 0.57.0 | MIT (`monaco/LICENSE.txt`) |
| `sqljs` | sql.js (SQLite en WebAssembly) para `sqlite3` en la terminal | 1.8.0 | MIT (`sqljs/LICENSE.txt`) |
| `pyodide` | Python 3.12 en WebAssembly (núcleo y biblioteca estándar). En `pyodide-lock.json` los paquetes extra apuntan a jsDelivr | 0.26.4 | MPL-2.0 |
| `typescript` | Compilador de TypeScript (para JSX/TSX/TS en la vista previa y `ts-node`), minificado | 5.4.5 | Apache-2.0 (`typescript/LICENSE.txt`) |

Para actualizar Monaco: `npm pack monaco-editor`, copiar `package/min/vs` aquí y borrar `vs/nls/lang/*` salvo `es.js`.

Python base viene incluido. Solo los paquetes extra (numpy, pandas, sqlite3, micropip para `pip install`…) se descargan de jsDelivr la primera vez que se usan.
Para actualizar Pyodide: `npm pack pyodide@X`, copiar pyodide.js, pyodide.asm.js, pyodide.asm.wasm y python_stdlib.zip, y regenerar pyodide-lock.json con `file_name` absolutos al CDN de la misma versión.
