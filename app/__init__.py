from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from flask_mail import Mail  # 1. Importamos la clase Mail
from app.common.filters import format_datetime

login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # 2. Instanciamos un objeto de tipo Mail

def create_app(settings_module):
    app = Flask(__name__, instance_relative_config=True)

    # Load the config file specified by the APP environment variable
    app.config.from_object(settings_module)
    with open('archivo.txt', 'w') as archivo:
        archivo.write(str(settings_module))
        archivo.write('\nEsto un es un texto')
    # Load the configuration from the instance folder
    if app.config.get('TESTING', False):
        app.config.from_pyfile('config-testing.py', silent=True)
    else:
        app.config.from_pyfile('config.py', silent=True)
    
    configure_logging(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # 3. Inicializamos el objeto mail

    register_filters(app)

    # Registro de los Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    # Custom error handlers
    register_error_handlers(app)

    return app

def register_filters(app):
    app.jinja_env.filters['datetime'] = format_datetime

def register_error_handlers(app):
    @app.errorhandler(500)
    def base_error_handler(e):
        return render_template('500.html'), 500
    @app.errorhandler(404)
    def error_404_handler(e):
        return render_template('404.html'), 404
    @app.errorhandler(401)
    def errorhandler(e):
        return render_template('401.html'), 401 


def configure_logging(app):
    # Eliminamos los posibles manejadores, si existen, del logger por defecto
    del app.logger.handlers[:]

    # Añadimos el logger por defecto a la lista de loggers
    loggers = [app.logger]
    handlers = []

    # Creamos un manejador para escribir los mensajes por consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter())

    if (app.config['APP_ENV'] == app.config['APP_ENV_LOCAL']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_TESTING']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_DEVELOPMENT']):
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)
    elif app.config['APP_ENV'] == app.config['APP_ENV_PRODUCTION']:
        console_handler.setLevel(logging.INFO)
        handlers.append(console_handler)

    # Asociamos cada uno de los handlers a cada uno de los loggers
    for l in loggers:
        for handler in handlers:
            l.addHandler(handler)
        l.propagate = False
        l.setLevel(logging.DEBUG)

def verbose_formatter():
    return logging.Formatter(
        '[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )