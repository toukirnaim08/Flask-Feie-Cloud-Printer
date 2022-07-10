# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"

APPLICATION_ROOT = "/printing-solution"

RQ_REDIS_URL = env.str("RQ_REDIS_URL", "redis://localhost:6379/0")

# Printer Configuration
PRINTER_ENABLED = env.bool("PRINTER_ENABLED", default=True)
PRINTER_URL = env.str("PRINTER_URL", default="http://global1.feieapi.com")
PRINTER_SN = env.str("PRINTER_SN")
PRINTER_KEY = env.str("PRINTER_KEY")

SWAGGER = {
    'title': 'Unido Printing Service',
    "version": "1.0.0",

    'uiversion': 3,
    'specs': [
        {
            'endpoint': 'apispec',
            'route':  APPLICATION_ROOT + '/rest/v1/apispec.json'
        }
    ],
    "specs_route": APPLICATION_ROOT + "/pages/apidocs/",
    'openapi': '3.0.2',
    "static_url_path": APPLICATION_ROOT + "/pages/flasgger_static",
    "doc_expansion": 'none',

    'components': {
        'schemas': {}
    },
}
