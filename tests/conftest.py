# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import logging
import pytest

from webtest import TestApp

from tests.test_helper import clear_queues
from printing_solution.app import create_app


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp_no_auth(app):
    """Create Webtest app."""
    # To clean up fake redis queues
    clear_queues()
    return TestApp(app)


