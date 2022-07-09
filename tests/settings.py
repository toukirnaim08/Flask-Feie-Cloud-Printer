"""Settings module for test app."""
ENV = "development"
TESTING = True

RQ_CONNECTION_CLASS = "fakeredis.FakeStrictRedis"

# Printer Configuration
PRINTER_ENABLED = True
PRINTER_URL = "http://fake-printer-com"
PRINTER_SN = "FAKESN"
PRINTER_KEY = "FAKEKEY"
