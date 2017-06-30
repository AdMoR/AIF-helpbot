# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from functools import wraps
from config import Config as config
from . import LOG, sentry, login_manager
import os
import requests
from . import app

api_v1 = Blueprint('helpbot', __name__)

#
# API calls handling tools
#


def format_response(response, status_code=200):
    response = Response(json.dumps(response), status=status_code,
                        mimetype='application/json')
    return response


@api_v1.route("/helpbot", methods=['POST', 'GET'])
def main():

    question = request.form.get('text')
    name = request.form.get('user_name')

    first_sentence = "Hello {}, I took your question to the admins.".format(name)
    second_sentence = "'{}' is a really nice question !".format(question)

    code, response = 200, {"text": first_sentence + second_sentence}

    return jsonify(response), code


@api_v1.route('/oauth', methods=['GET'])
def info():
    """Display API basic informations. Useful for Healthcheck."""

    arg_code = request.args.get('code')

    url = 'https://slack.com/api/oauth.access'
    qs = {"code": arg_code, "client_id": config.get('client_id'),
          "client_secret": config.get('client_secret')}
    response = requests.get(url, query=qs)
    print(response.__dict__)

    return jsonify(response), 200

