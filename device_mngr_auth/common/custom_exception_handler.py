from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):

    handlers = {
        'ValidationError': handle_validation_error,
        'NotAuthenticated': handle_authentication_error,
        'NotFound': handle_not_found_error,
        'InvalidToken': handle_invalidtoken_error,
    }

    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def handle_invalidtoken_error(exc, context, response):
    response.data = {
        'status': 401,
        'message': "Token is invalid or expired",
        'error': response.data['messages'][0]
    }
    return response


def handle_authentication_error(exc, context, response):

    response.data = {
        'status': 401,
        'message': 'Please Login To Process!!'
    }
    return response


def handle_not_found_error(exc, context, response):

    response.data = {
        'status': 404,
        'message': response.data['detail']
    }
    return response


def handle_validation_error(exc, context, response):
    data = {}
    res = check_dict_error(response.data, data)
    response.data = {
        'status': 400,
        'message': 'Invalid data',
        'error': res
    }
    return response


def check_dict_error(list_error, data):
    for key, value in list_error.items():
        if isinstance(value, dict):
            check_dict_error(value, data)
        else:
            result = {key: value[0]}
            data.update(result)
    return data
