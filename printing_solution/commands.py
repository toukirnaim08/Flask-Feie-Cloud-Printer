# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call

import click

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
def test():
    """Run the tests."""
    import pytest

    # https://docs.pytest.org/en/6.2.x/reference.html#command-line-flags
    rv = pytest.main([TEST_PATH, "--verbose", "--pdb"])
    exit(rv)