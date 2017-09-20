from flask import Blueprint
from flask import jsonify

errors=Blueprint('errors',__name__)
@errors.app_errorhandler(404)
def handler_404(e):
    import logging
    logging.exception('404 NOT FOUND\n')
    error_msg="404 NOT FOUND"
    return jsonify(msg=str(error_msg)),404


#@errors.app_errorhandler(Exception)
#def all_exception_handler(e):
#    return jsonify(msg=str(e)),500
