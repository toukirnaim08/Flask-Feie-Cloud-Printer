import requests_mock
import webtest
import re

import printing_solution.extensions as extensions

from tests.test_helper import load_mock_from_file, clear_queues


class TestPrinter:
	PRINT_DATA = {
		"ticket_number": "1234",
		"qr": "www.printme.com"
	}

	def test_print_ticket(self, testapp_no_auth: webtest.app.TestApp):
		with requests_mock.Mocker() as mock:
			load_mock_from_file(key=None, mock=mock, regex=re.compile(r"printer_mock_.*"))

			r = testapp_no_auth.post_json(url="/rest/v1/print_ticket",
			                              params=TestPrinter.PRINT_DATA)
			assert r.status_code == 200
			# Just one read queue'd up
			assert extensions.rq.get_queue(name=extensions.DEFAULT_QUEUE).count == 1

			# Call the async printing task in sync mode.
			order_id = extensions.print_service. \
				send_printing_request(ticket_number=TestPrinter.PRINT_DATA['ticket_number'],
			                          qr=TestPrinter.PRINT_DATA['qr'])

			assert order_id == '62944f7ff4b4ae46db963a89'

			clear_queues()
