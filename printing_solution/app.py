import flask
from flask import Flask

from printing_solution import printing, commands
from printing_solution.extensions import (
    rq,
    swagger,
    print_service,
)


def create_app(config_object="printing_solution.settings"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    rq.init_app(app)
    load_swagger_component_schemas(app)
    swagger.init_app(app)
    print_service.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    printing.views.register_blueprint(app)
    # tools.views.register_blueprint(app)

    @app.route('/')
    def home():
        return flask.redirect(app.config.get('APPLICATION_ROOT') + '/pages/apidocs', 307)

    return None


def load_swagger_component_schemas(app):
    swagger_config = app.config.get("SWAGGER", {})
    if 'components' not in swagger_config:
        swagger_config['components'] = {}
    if 'schemas' not in swagger_config['components']:
        swagger_config['components']['schemas'] = {}

    app.config['SWAGGER'] = swagger_config


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
