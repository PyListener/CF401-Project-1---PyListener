from pyramid.config import Configurator
import os

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if "sqlalchemy.url" not in settings:
        settings["sqlalchemy.url"] = os.environ["DATABASE_URL"]
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.include('.security')
    config.scan()
    return config.make_wsgi_app()
