"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flasgger import Swagger
from flask_rq2 import RQ

import printing_solution.services.svc_print as svc_print

DEFAULT_QUEUE = "printing-default"

rq = RQ()
swagger = Swagger()

print_service = svc_print.RemotePrintService()
