from flask import request, session
import logging
from datetime import datetime


class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """ Provide some extra variables to give our logs some
        better info """

        log_record.url = request.path
        log_record.method = request.method
        log_record.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        log_record.member_id = session.get('babel_member_id') or 'undefined'
        log_record.session_code = session.get('babel_session_code') or 'undefined'

        return True
