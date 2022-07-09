import logging.config

logging.config.fileConfig("logging.conf")

from printing_solution.app import create_app
app = create_app()
