"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flasgger import Swagger
from flask_rq2 import RQ

import printing_solution.services.feie_printer as feie_printer

DEFAULT_QUEUE = "printing-queue"

rq = RQ()
swagger = Swagger()

print_service = feie_printer.FeiePrintService()
