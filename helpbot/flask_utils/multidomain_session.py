from flask.sessions import SecureCookieSessionInterface
from flask import request


class MultiDomainSession(SecureCookieSessionInterface):
    def get_cookie_domain(self, app):
        return request.host or None
