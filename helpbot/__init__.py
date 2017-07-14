# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from flask import Flask
from flask_cors import CORS
import logging
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix
from config import Config as config
from flask_login import LoginManager

__title__ = 'helpbot'
__version__ = '1.0'

#
# Creating Flask app object
#
app = Flask(__name__)
CORS(app)
login_manager = LoginManager()
app.config.from_object('config.Config')
app.wsgi_app = ProxyFix(app.wsgi_app)
login_manager.init_app(app)


@app.before_first_request
def init_logger():
    #
    # Customize app logger
    #
    # Modify the format of the default debug handler
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

    fmt = logging.Formatter(fmt=config.LOG_FORMAT)
    for h in app.logger.handlers:
        h.setFormatter(fmt)

    from .flask_utils.request_context_logger import ContextualFilter
    app.logger.addFilter(ContextualFilter())


# Export the app.logger to LOG
LOG = app.logger

#
# Init Sentry Service
#
sentry = Sentry(app, dsn=config.get('monitoring')['sentry_dsn'])

#
# Attach Blueprints
#
from .controller import api_v1
app.register_blueprint(api_v1, url_prefix='/helpbot')


LOG.info('Starting Server. Environment: %s', config.get('environment'))
