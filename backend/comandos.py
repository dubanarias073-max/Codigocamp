"""Comandos de terminal para cargar, sincronizar y revisar el catálogo de retos."""
import click

from models import db


def registrar_comandos(app):
    """Añade a la app los comandos para cargar y revisar el catálogo de retos."""
    @app.cli.command("reparar-workbench")
    def reparar_workbench():
        """Quita lo que hace que MySQL Workbench se cierre al crear el diagrama de tablas."""
        from models import db
        from servicios.workbench import reparar
        cambios = reparar(db.engine)
        click.echo("\n".join(cambios) if cambios else "La base ya estaba lista para el diagrama de Workbench.")

    @app.cli.command("seed-retos")
    @click.option("--reset", is_flag=True, help="Borra el catálogo (y el progreso de niveles) y lo vuelve a cargar.")
    def seed_retos(reset):
        """Carga etapas, secciones, lecciones y preguntas desde backend/retos/*.py."""
        from retos import poblar_catalogo

        if poblar_catalogo(db.session, reset=reset):
            print("Catálogo cargado: etapas, secciones, lecciones y preguntas listas.")
        else:
            print("El catálogo ya estaba completo; no se hicieron cambios. Usa sync-retos para aplicar ediciones sin borrar el progreso.")

    @app.cli.command("sync-retos")
    def sync_retos():
        """Actualiza o amplía el catálogo sin borrar el progreso guardado."""
        from retos import sincronizar_catalogo

        if sincronizar_catalogo(db.session):
            print("Catálogo sincronizado; el progreso de niveles se conservó.")
        else:
            print("El catálogo ya estaba actualizado; no se hicieron cambios.")

    @app.cli.command("recordar-rachas")
    @click.option("--nivel", type=click.IntRange(1, 2), default=1, help="1 = aviso de la tarde, 2 = última oportunidad.")
    def recordar_rachas_cmd(nivel):
        """Envía ya el aviso de racha a quien aún no practicó hoy. Flask también lo hace solo mientras está encendido
        (a las 18 y a las 21; ver RECORDATORIO_HORA en backend/.env)."""
        from servicios.correo import recordar_rachas
        print(f"Avisos enviados: {recordar_rachas(nivel=nivel)}")

    @app.cli.command("probar-ia")
    def probar_ia_cmd():
        """Comprueba la clave y el modelo de Gemini de backend/.env con una pregunta corta."""
        import json
        import urllib.error
        from flask import current_app
        from rutas.tutor import explicar_error_gemini, generar, normalizar_modelo
        clave, modelo = current_app.config["GEMINI_API_KEY"].strip(), normalizar_modelo(current_app.config["GEMINI_MODEL"])
        if not clave:
            print("✖ Falta GEMINI_API_KEY en backend/.env"); return
        print(f"Modelo: {modelo} · clave: {clave[:6]}…{clave[-4:]} ({len(clave)} caracteres)")
        cuerpo = json.dumps({"contents": [{"role": "user", "parts": [{"text": "Di hola en una palabra."}]}]}).encode()
        try:
            d, usado = generar(cuerpo, clave, modelo, 60)
            texto = "".join(x.get("text", "") for x in d["candidates"][0]["content"]["parts"] if not x.get("thought")).strip()
            print(f"✔ Gemini responde ({usado}):", texto)
            if usado != modelo:
                print(f"  «{modelo}» no está disponible para tu clave. Pon en backend/.env: GEMINI_MODEL={usado}")
        except urllib.error.HTTPError as e:
            texto = e.read()[:800].decode("utf-8", "replace")
            print(f"✖ {explicar_error_gemini(e.code, texto, modelo)}\n  Respuesta de Gemini: {texto[:300]}")
        except Exception as e:  # noqa: BLE001
            print(f"✖ No se pudo conectar con Gemini: {e}")

    @app.cli.command("probar-correo")
    @click.argument("para")
    def probar_correo_cmd(para):
        """Envía un correo de prueba para comprobar la configuración MAIL_* de backend/.env."""
        from flask import current_app
        from servicios.correo import _config, _enviar_ya, enviar, plantilla
        cfg = _config(current_app)
        if not cfg["servidor"]:
            print("No hay servidor de correo configurado: el correo se guarda como .eml en ALMACEN_ARCHIVOS/correos/.\n"
                  "Agrega en backend/.env: MAIL_SERVER=smtp.gmail.com, MAIL_USER=tu@gmail.com y MAIL_PASSWORD=<contraseña de aplicación>.")
        else:
            print(f"Servidor {cfg['servidor']}:{cfg['puerto']} ({'SSL' if cfg['ssl'] else 'STARTTLS' if cfg['tls'] else 'sin cifrar'}) · usuario {cfg['usuario'] or '(ninguno)'} · desde {cfg['de']}")
        try:
            from email.message import EmailMessage
            from pathlib import Path
            m = EmailMessage()
            m["Subject"], m["From"], m["To"] = "Prueba de correo de CódigoCamp", cfg["de"], para
            m.set_content("Si lees esto, el correo de CódigoCamp está bien configurado.")
            m.add_alternative(plantilla("¡Funciona!", ["Si lees esto, el correo de CódigoCamp está bien configurado."]), subtype="html")
            _enviar_ya(cfg, m, Path(current_app.config.get("ALMACEN_ARCHIVOS") or "almacen_archivos") / "correos")
            print("✔ Enviado. Revisa también la carpeta de spam." if cfg["servidor"] else "✔ Guardado como .eml.")
        except Exception as e:  # noqa: BLE001
            print(f"✖ No se pudo enviar: {e}")
            if "535" in str(e) or "Username and Password not accepted" in str(e):
                print("  Gmail rechazó la clave: usa una «contraseña de aplicación» (myaccount.google.com/apppasswords, requiere verificación en 2 pasos), no tu contraseña normal.")

    @app.cli.command("migrar-camino")
    def migrar_camino_cmd():
        """Pasa el camino a la estructura nueva (preguntas sin repetir) conservando el progreso de cada estudiante."""
        from retos.migracion import migrar_camino
        r = migrar_camino(db.session)
        click.echo(f"Camino migrado. Progreso trasladado: {r['niveles_restaurados']} niveles de {r['personas']} estudiantes.")

    @app.cli.command("limpiar-archivos")
    def limpiar_archivos():
        """Borra del disco los archivos de Trabajo que ya no están en la base (cuentas borradas, subidas cortadas)."""
        from rutas.archivos import limpiar_disco
        click.echo(f"Archivos borrados del disco: {limpiar_disco(app)}")

    @app.cli.command("check-retos")
    def check_retos():
        """Revisa los archivos de retos (sin base de datos) y muestra cuántas preguntas tiene cada curso."""
        from retos import revisar_catalogo

        raise SystemExit(revisar_catalogo())
