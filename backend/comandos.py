"""Comandos de terminal para cargar, sincronizar y revisar el catálogo de retos."""
import click

from models import db


def registrar_comandos(app):
    """Añade a la app los comandos para cargar y revisar el catálogo de retos."""
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

    @app.cli.command("check-retos")
    def check_retos():
        """Revisa los archivos de retos (sin base de datos) y muestra cuántas preguntas tiene cada curso."""
        from retos import revisar_catalogo

        raise SystemExit(revisar_catalogo())
