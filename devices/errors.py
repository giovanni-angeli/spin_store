# -*- coding: utf-8 -*-
import json
import logging
from . import get_connection


def get_error():
    """
    Gets the error descriptor
    :return: a triple (err_code [int], device [string], message [*])
    """
    
    logging.warning("errors.get_error() ")
    
    redis = get_connection()
    
    logging.warning("errors.get_error()  redis:{}".format(redis))

    result = redis.get('user:error')
    if result is None:
        return None, None, None

    logging.warning("errors.get_error()  result:{}".format(result))
    
    if isinstance(result, bytes):
        result = result.decode()

    return json.loads(result)


def set_error(code, device, message):
    """
    Sets the error descriptor
    :param code:
    :param device:
    :param message:
    :return:
    """
    redis = get_connection()
    redis.set('user:error', json.dumps([code, device, unicode(message)]))


def dismiss_error():
    """
    Clears the error descriptor
    :return:
    """
    redis = get_connection()
    redis.delete('user:error')

