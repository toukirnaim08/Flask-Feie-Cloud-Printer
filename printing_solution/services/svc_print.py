import typing
import requests
import flask
import datetime as dt


class APIException(Exception):
    """We use this to indicate a generic issue with a remote API. Generates a 400 if not caught"""
    def __init__(self, message):
        super().__init__(message)


class RemotePrintService:
    # Two types of printing formats found "Ticket Print Format" and "Label Print Format"
    # Also, two printer management portals found http://global1.feieapi.com/FPServer/ and
    # http://developer.de.feieyun.com/#/dashboard
    # Apparently, our current printers support http://global1.feieapi.com/FPServer/ and
    # allow "Ticket Print Format" only
    # see https://github.com/stark-tech-space/feieyun-node/packages/524242#ticket-print-format
    # for api documentation see http://www.feieyun.com/open/apidoc-en.html
    DEFAULT_TIMEOUT = 5  # seconds
    MAX_DATA_CHUNK = 8

    def __init__(self, app=None):
        self.enabled = False
        self.base_url = None
        self.sn = None
        self.key = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.enabled = app.config.get("PRINTER_ENABLED", True)
        if self.enabled:
            self.base_url = app.config["PRINTER_URL"]
            self.sn = app.config["PRINTER_SN"]
            self.key = app.config["PRINTER_KEY"]

    @staticmethod
    def __generic_failure(r: requests.models.Response, raise_exception_on_error: bool = True):
        if r.status_code not in (200, 201, 204):
            flask.current_app.logger.warning(
                f"Printing request failure - {r.status_code} - r:{raise_exception_on_error}",
                extra={'context': {
                    'text': r.text,
                    'raise_exception_on_error': raise_exception_on_error,
                    'status_code': r.status_code
                }})

            if raise_exception_on_error:
                raise APIException(f"Printing service error encountered - {r.status_code} - {r.text}")

    @staticmethod
    def qr(code, new_line=True):
        # <QR></QR> : QR code
        return f"<QR>{code}</QR>{'<BR>' if new_line else ''}"

    @staticmethod
    def heading(text, new_line=True):
        # <CB></CB> : Center to zoom in
        return f"<CB>{text}</CB>{'<BR>' if new_line else ''}"

    @staticmethod
    def center(text, new_line=True):
        # <C></C> : Centered
        return f"<C>{text}</C>{'<BR>' if new_line else ''}"

    @staticmethod
    def generate_printable_content(heading: str,
                                   qr: str,
                                   body: typing.Optional[typing.List[str]] = None,
                                   include_timestamp: bool = True) -> str:
        # Add heading and qr code in large font and center position
        print_content = RemotePrintService.heading(heading)
        print_content += RemotePrintService.qr(qr)

        # If body doest exist, we can use qr code to create body
        if not body:
            body = ['prod', '-----------']
            body += [chunked_data for chunked_data in [qr[i:i + RemotePrintService.MAX_DATA_CHUNK]
                                                       for i in range(0, len(qr), RemotePrintService.MAX_DATA_CHUNK)]]
            body += ['-----------']
            body += [dt.datetime.utcnow().isoformat() if include_timestamp else '']

        # Convert body into a printable format
        for value in body:
            # If null or empty string found, we can add some dots in center
            if not value:
                print_content += RemotePrintService.heading("-----------")
                continue

            # If the element is the last value of the list and the timestamp flag is on
            if include_timestamp and value == body[-1]:
                # Print timestamp in small font
                print_content += RemotePrintService.center(value)
                continue

            # We use large font for all the values except timestamp
            print_content += RemotePrintService.heading(value)

        return print_content

    def send_printing_request(self,
                              heading: str,
                              qr: str,
                              include_timestamp: bool = True,
                              body: typing.Optional[typing.List[str]] = None,
                              times=1) -> typing.Optional[str]:
        if not self.enabled:
            return

        if not self.sn or not self.key:
            flask.current_app.logger.info(f"No printer serial number has been provided")
            return

        params = {
            'sn': self.sn,
            'printContent': RemotePrintService.generate_printable_content(heading=heading,
                                                                          qr=qr,
                                                                          body=body,
                                                                          include_timestamp=include_timestamp),
            'key': self.key,
            'times': times
        }

        url = f"{self.base_url}/FPServer/printOrderAction"

        try:
            r = requests.post(url, data=params, timeout=RemotePrintService.DEFAULT_TIMEOUT)
        except Exception as e:
            flask.current_app.logger.warning(
                f"Unable to send printing request - {e}",
                exc_info=e,
                extra={'context': {
                    'url': url,
                    'payload': params
                }})
            raise

        RemotePrintService.__generic_failure(r)

        # A valid response
        # {"ret":0,"msg":"ok","data":"62944f7ff4b4ae46db963a89","serverExecutedTime":0} "data" is the order id
        res = r.json()
        return res['data'] if 'data' in res else None
