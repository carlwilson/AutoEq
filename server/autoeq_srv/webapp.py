#!/usr/bin/python
# coding=UTF-8
#
# Auto EQ Server
#
# Copyright © 2021 Carl Wilson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Initialisation module for package, kicks of the flask app."""
import logging
__version__ = '0.1.0'
# Load the application
from flask import Flask
from .config import configure_app # pylint: disable-msg=C0413

def get_app():
    """Return the initialised Flask application."""
    app = Flask(__name__)
    # Get the appropriate config
    configure_app(app)

    # Configure logging across all modules
    logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG,
                        format=app.config['LOG_FORMAT'])
    logging.info("Started AutoEQ web.")
    logging.debug("Configured logging.")
    logging.info("Setting up application routes")
    return app
