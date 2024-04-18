import logging
from quart import Blueprint, request, Response
import requests
from shared.api_view import ApiResponse, ApiView

def create_configuration_blueprint(logger : logging.Logger):
    view = View(logger)

    blueprint = Blueprint('handshake_api', __name__)

    @blueprint.route('/configuration/add_library', methods=['POST'])
    async def add_library_request():
        return await view.add_library_handler(request)

    return blueprint

class View(ApiView):
    ''' View container class. '''

    def __init__(self, logger : logging.Logger):
        self._logger : logging.Logger = logger.getChild(__name__)

    async def add_library_handler(self, request : request):
        print("def add_library_handler(self, request : request)")

        return Response("~~PLACEHOLDEr~~", status = 500)
