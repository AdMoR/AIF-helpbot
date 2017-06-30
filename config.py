# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import json


class Config(object):
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    INFRA_CONFIG_FILE_PATH = os.path.join(PROJECT_PATH, 'config.json')

    with open(INFRA_CONFIG_FILE_PATH) as CONFIG_FILE:
        INFRA = json.load(CONFIG_FILE)

    CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    SECRET_KEY = 'Riri fifi loulou'
    LOG_FORMAT = '%(ip)s %(asctime)s [%(url)s] [%(levelname)s] [%(session_code)s] [%(module)s:%(lineno)d] %(message)s'

    @classmethod
    def get(cls, key):
        return os.environ.get(key) or cls.INFRA.get(key)
