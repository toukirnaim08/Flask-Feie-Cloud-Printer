import typing
import requests
import flask


class APIException(Exception):
    """We use this to indicate a generic issue with a remote API. Generates a 400 if not caught"""
    def __init__(self, message):
        super().__init__(message)


class FeiePrintService:
    """Two types of printing formats found "Ticket Print Format" and
    "Label Print Format". We will use "Ticket Print Format" only. see
     https://github.com/stark-tech-space/feieyun-node/packages/524242#ticket-print-format"""
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
    def generate_printable_content(ticket_number: str,
                                   qr: str) -> str:
        # Add name and qr code in large font and center position
        print_content = FeiePrintService.heading(ticket_number)
        print_content += FeiePrintService.qr(qr)
        return print_content

    def send_printing_request(self,
                              ticket_number: str,
                              qr: str,
                              times=1) -> typing.Optional[str]:
        if not self.enabled:
            return

        if not self.sn or not self.key:
            flask.current_app.logger.info(f"No printer serial number has been provided")
            return

        params = {
            'sn': self.sn,
            'printContent': FeiePrintService.generate_printable_content(ticket_number=ticket_number,
                                                                        qr=qr),
            'key': self.key,
            'times': times
        }

        url = f"{self.base_url}/FPServer/printOrderAction"

        try:
            r = requests.post(url, data=params, timeout=FeiePrintService.DEFAULT_TIMEOUT)
        except Exception as e:
            flask.current_app.logger.warning(
                f"Unable to send printing request - {e}",
                exc_info=e,
                extra={'context': {
                    'url': url,
                    'payload': params
                }})
            raise

        FeiePrintService.__generic_failure(r)

        # A valid response
        # {"ret":0,"msg":"ok","data":"62944f7ff4b4ae46db963a89","serverExecutedTime":0} "data" is the order id
        res = r.json()
        return res['data'] if 'data' in res else None
