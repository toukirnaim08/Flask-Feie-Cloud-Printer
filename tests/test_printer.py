import requests_mock
import webtest
import re

import printing_solution.extensions as extensions

from tests.test_helper import load_mock_from_file, clear_queues


class TestPrinter:
    PRINT_DATA = {
        "heading": "1234",
        "qr": "a14deb013f98075dc1bd0831b1322f69038fd34056127424c3e468fd7fa0b0b2",
        "body": [
            "prod",
            "",
            "a14deb01",
            "3f98075d",
            "c1bd0831",
            "b1322f69",
            "038fd340",
            "56127424",
            "c3e468fd",
            "7fa0b0b2",
            "",
            "2022-05-02T12:45:32"
        ],
        "include_timestamp": True
    }

    def test_print_service(self, testapp_no_auth: webtest.app.TestApp):
        with requests_mock.Mocker() as mock:
            load_mock_from_file(key=None, mock=mock, regex=re.compile(r"printer_svc_.*"))

            r = testapp_no_auth.post_json(url="/rest/v1/print",
                                          params=TestPrinter.PRINT_DATA)
            assert r.status_code == 200
            # Just one read queue'd up
            assert extensions.rq.get_queue(name=extensions.DEFAULT_QUEUE).count == 1

            # Call the async printing task in sync mode.
            order_id = extensions.print_service.send_printing_request(heading=TestPrinter.PRINT_DATA['heading'],
                                                                      qr=TestPrinter.PRINT_DATA['qr'],
                                                                      body=TestPrinter.PRINT_DATA['body'],
                                                                      include_timestamp=TestPrinter.PRINT_DATA[
                                                                          'include_timestamp'])

            assert order_id == '62944f7ff4b4ae46db963a89'

            clear_queues()
