'''
Copyright 2014-2023 Integrated Test Management Suite

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from http import HTTPStatus
from quart import Blueprint, request, Response
from shared.api_view import ApiView

def create_health_blueprint():
    view = View()

    blueprint = Blueprint('health_api', __name__)

    @blueprint.route('/health/status', methods=['GET'])
    async def health_status_request():
        return await view.health_status_handler(request)

    return blueprint

class View(ApiView):
    ''' View container class. '''

    async def health_status_handler(self, request : request):
        return Response("OK", status = HTTPStatus.OK)
