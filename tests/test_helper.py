import re
import os
import json
import typing

import requests_mock

import printing_solution.extensions as extensions

CONFIGS = {
    "printer_svc_01": {
        "url": f"http://fake-printer-com/FPServer/printOrderAction",
        "method": "POST",
        "data": '{"ret": 0, "msg": "ok", "data": "62944f7ff4b4ae46db963a89", "serverExecutedTime": 0}'
    },
    "printer_svc_02": {
        "url": "/rest/v1/printing",
        "method": "POST",
        "data": '{"response": "ok"}'
    },
}


def load_mock_from_file(
    key: typing.Optional[str],
    mock: requests_mock.Mocker,
    data_patcher=None,
    regex: re.Pattern = None,
):
    keys_to_load = set()
    if key and key in CONFIGS:
        keys_to_load.add(key)
    if regex:
        for k in CONFIGS:
            if regex.match(k):
                keys_to_load.add(k)

    for k in keys_to_load:
        config = CONFIGS[k]
        if "data" in config:
            json_data = json.loads(config["data"])
        else:
            filename = k
            if 'source_key' in config:
                filename = config['source_key']

            json_data = load_config_from_file(filename)

        if data_patcher:
            data_patcher(json_data)
        mock.register_uri(
            method=config["method"],
            url=config["url"],
            json=json_data,
            status_code=config["status_code"] if "status_code" in config else 200,
        )


def load_config_from_file(name):
    return json.loads(
        open(os.path.join("tests", "config", name + ".json"), "r").read()
    )


def clear_queues():
    # The queue is not automatically flushed as part of testing scope completion.
    # This can lead to problems related to fakeredis and lupa
    extensions.rq.get_queue(name=extensions.DEFAULT_QUEUE).empty()
    extensions.rq.get_queue().empty()
