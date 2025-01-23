import asyncio
from botbuilder.core import TurnContext
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from botbuilder.schema import Activity
from .teamsbot import MyBot
from django.utils.decorators import method_decorator
import json
import logging
from .client_server import WebSocketClient

bot = MyBot()

logger = logging.getLogger(__name__)
client = WebSocketClient()


@method_decorator(csrf_exempt, name='dispatch')
class MessagesView(View):
    _initialized = False
    _client = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize WebSocketClient only once when the view is instantiated
        if not MessagesView._initialized:
            MessagesView._client = WebSocketClient()
            asyncio.create_task(MessagesView._client.periodic_cleanup())
            MessagesView._initialized = True

    async def post(self, request, *args, **kwargs):
        try:
            body = request.body.decode("utf-8")
            activity = Activity().deserialize(json.loads(body))
            auth_header = request.headers.get('Authorization', '')

            logger.info(f"Body: {body}")
            logger.info(f"Authorization header: {auth_header}")

            teams_id = activity.from_property.id
            bot_id = activity.recipient.id
            if activity.type == "message":
                client = self.__class__._client
                if client:
                    await client.fetch_from_websocket(body, teams_id, bot_id,activity, auth_header, client)
            # elif activity.type == "conversationUpdate" and activity.members_added:
            #     await self.handle_members_added_activity(activity, auth_header)
            return JsonResponse({}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Server error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    # async def handle_members_added_activity(self, activity, auth_header):
    #     async def turn_call(turn_context: TurnContext):
    #         try:
    #             await bot.on_members_added_activity(activity.members_added, turn_context)
    #         except Exception as e:
    #             logger.error(f"Error in on_members_added_activity: {e}")
    #
    #     await adapter.process_activity(activity, auth_header, turn_call)
    #     logger.debug("Members added activity processed successfully")
