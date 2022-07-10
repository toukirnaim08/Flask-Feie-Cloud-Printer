import typing
import flask
import hashlib

from flask_restful import Resource, Api
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from werkzeug.exceptions import BadRequest

import printing_solution.tasks.tasks as tasks


def register_blueprint(app):
    api_bp = flask.Blueprint('printing',
                             __name__,
                             url_prefix=app.config.get('APPLICATION_ROOT', '') + '/rest/v1',
                             static_folder='../static')
    api = Api(api_bp)

    api.add_resource(PrintContent, '/print_ticket')
    app.register_blueprint(api_bp)


class PrintContent(Resource):
    PRINT_CONTENT_JSONSCHEMA = {
        "type": "object",
        "properties": {
            "ticket_number": {"type": "string"},
            "qr": {"type": "string"},
        },
        "required": ["ticket_number", "qr"],
        "additionalProperties": False
    }

    def post(self):
        """Send request to print ticket
        ---
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  ticket_number:
                    type: string
                  qr:
                    type: string
                required:
                  - ticket_number
                  - qr
        responses:
          '200':
            response: ok
        """
        # Now apply json schema validation
        r = PrintContent.validate_json_schema(PrintContent.PRINT_CONTENT_JSONSCHEMA,
                                              payload_expected=True)
        # We generate hash/job_id using ticket, qr
        job_id = PrintContent.sha256(data=r)

        # Send printing request asynchronously using redis queue.
        # If we pass in job_id to queue, then only one task can exist with that name
        tasks.queue_async_send_printing_request(
            job_id=job_id,
            ticket_number=r['ticket_number'],
            qr=r['qr']
        )

        return flask.jsonify({"response": "ok"})

    @staticmethod
    def validate_json_schema(schema, payload_expected=True):
        """
        Helper to validate json schema and perform basic non-null checks
        """
        r = flask.request.get_json()
        if payload_expected:
            if not r:
                raise BadRequest("JSON payload expected")
        else:
            if r is None:
                return {}

        # Now apply json schema validation
        try:
            validate(instance=r, schema=schema)
        except ValidationError as e:
            raise BadRequest("Invalid payload format - %s" % e.message)
        return r

    @staticmethod
    def sha256(data: typing.Dict):
        x = data['ticket_number'] + data['qr']
        m = hashlib.sha256()
        m.update(x.encode('utf8'))
        return m.hexdigest()
