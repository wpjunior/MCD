# -*- coding: utf-8 -*

__all__ = ('json_response',)

from MCD.produto.responses import JSONResponse

def json_response(f):
    """
    Decorator para fornecer uma função que retorna uma resposta em JSON
    """
    def func(*args, **kwargs):
        return JSONResponse(f(*args, **kwargs))

    func.__name__ = f.__name__
    func.__doc__ = f.__doc__

    return func
