from functools import wraps
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from utils import InvalidDataError

def exceptions_to_http_status(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except InvalidDataError as e:
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            return HttpResponseServerError(str(e))
    return inner

