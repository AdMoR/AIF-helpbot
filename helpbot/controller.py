# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from functools import wraps
from config import Config as config
from . import LOG, sentry, login_manager
import hashlib
import requests
from . import app
from redis import StrictRedis
import pickle

api_v1 = Blueprint('helpbot', __name__)
r = StrictRedis()
#
# API calls handling tools
#


def format_response(response, status_code=200):
    response = Response(json.dumps(response), status=status_code,
                        mimetype='application/json')
    return response


@api_v1.route("/question", methods=['POST', 'GET'])
def main():

    # Get the data
    question = request.form.get('text')
    name = request.form.get('user_name')
    ticket = hashlib.md5(name.encode('utf-8') + question.encode('utf-8') +\
                         config.get("salt").encode('utf-8')).hexdigest()

    print(request.form.__dict__)

    r.set(ticket, pickle.dumps((name, question)))

    first_sentence = "Hello {},\n I took your question to the admins.\n".format(name)
    second_sentence = "Here is you ticket number {}.\n An admin will answer your question soon.".format(ticket)

    # Post data to the room
    post_on_channel = {"text": "A new question from {} : {}\n. The ticket number is {}".\
                       format(name, question, ticket),
                       "channel": "#test_helpbot", "link_names": 1, "username": "help-bot"}
    room_post_url = config.get('room_post_url')

    requests.post(room_post_url,
                  data=json.dumps(post_on_channel))

    code, response = 200, {"text": first_sentence + second_sentence}

    return jsonify(response), code


@api_v1.route("/answer", methods=['POST', 'GET'])
def answer():

    req = request.form.get('text')
    name = request.form.get('user_name')

    params = req.split(" ")
    ticket = params[0]
    answer = ""
    for word in params[1:]:
        answer += " " + word

    data = r.get(ticket)
    if data is not None:
        question_name, question = pickle.loads(data)
    else:
        raise Exception

    first_sentence = "Bonjour à tous,\n {} a répondu à la question de @{}.\n".format(name, question_name)
    second_sentence = "La question : {}\n".format(question)
    third_sentence = "Et voici la réponse: {}\n".format(answer)

    answer_room_url = config.get("answer_post_url")
    requests.post(answer_room_url,
                  data=json.dumps({"text": first_sentence + second_sentence + third_sentence}))

    code, response = 200, {"text": first_sentence + second_sentence + third_sentence}

    return jsonify(response), code


@api_v1.route("/send_document", methods=['POST', 'GET'])
def save_document():

    req = request.form.get('text')
    name = request.form.get('user_name')

    doc_url = req

    first_sentence = "Bonjour à tous,\n {} a répondu à la question de @{}.\n".format(name, question_name)
    second_sentence = "La question : {}\n".format(question)
    third_sentence = "Et voici la réponse: {}\n".format(answer)

    answer_room_url = config.get("answer_post_url")
    requests.post(answer_room_url,
                  data=json.dumps({"text": first_sentence + second_sentence + third_sentence}))

    code, response = 200, {"text": first_sentence + second_sentence + third_sentence}

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


@api_v1.route('/warn_user', methods=['POST'])
def warn_user():

    data = request.get_json(force=True)
    email = data['email']
    user = get_user_id_by_email(email)
    if user is None:
        code, response = 400, {"status": "Could not found the email"}
        return jsonify(response), code
    name = user["real_name"]
    message = "Salut {}, quelqu'un souhaite rejoindre ton équipe sur le site du challenge. Consulte sa candidature sur http://www.jeunes-industrie-du-futur.fr/view_team"
    pers_message = message.format(name)
    resp = requests.post("https://slack.com/api/chat.postMessage",
                         {'channel': user['id'], 'text': pers_message,
                          "token": config.get('slack-invite-token')},
                         headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
    print(resp.text)
    code, response = 200, {"status": "Success", "message": pers_message}
    return jsonify(response), code

###################
#    HELPERS      #
###################


def get_user_list():
    response = requests.post("https://slack.com/api/users.list", {"token": config.get("slack-invite-token")},
                             headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
    return response


def get_user_id_by_email(email):
    response = get_user_list()
    all_members = json.loads(response.text)
    all_members = all_members['members']
    print(['email' in member['profile'].keys() for member in all_members])
    email_user = [member for member in all_members
                  if ('email' in member['profile'].keys() and member['profile']['email'] == email)]
    if len(email_user) == 1:
        return email_user[0]
    else:
        return None
