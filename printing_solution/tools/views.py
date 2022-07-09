import json
import os
import time

import flask
from flask_restful import Resource, Api
from flask.json import dumps
from flask.wrappers import Response

import printing_solution.extensions as extensions


def register_blueprint(app):
    api_bp = flask.Blueprint('tools',
                             __name__,
                             url_prefix=app.config.get('APPLICATION_ROOT', '') + '/rest/v1/tools',
                             static_folder='../static')
    api = Api(api_bp)

    api.add_resource(ToolsInfoV1, '/info')
    app.register_blueprint(api_bp)


class ToolsInfoV1(Resource):
    CACHE_TIMEOUT = 60

    def get(self):
        """API Version
        ---
        parameters: []
        responses:
          '200':
            description: ok
        """
        try:
            with open(os.path.join("static", "application_info.json")) as f:
                return ToolsInfoV1.jsonify_with_cache(
                    payload=json.loads(f.read()),
                    cache_timeout=ToolsInfoV1.CACHE_TIMEOUT
                )

        except Exception:
            return flask.jsonify({})

    @staticmethod
    def jsonify_with_cache(payload, cache_timeout: int) -> Response:
        js = dumps(payload)
        rv = flask.current_app.response_class(js, mimetype='application/json')
        rv.cache_control.public = True
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time.time() + cache_timeout)
        return rv
