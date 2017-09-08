from functools import wraps
from utils import InvalidData
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

def exceptions_to_http_status(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except InvalidData as e:
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            return HttpResponseServerError(str(e))
    return inner

