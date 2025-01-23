import logging
import json
import uuid
import time
import asyncio

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.viewsets import ViewSet
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ChatBot.views.websocket_client import WebSocketClient
from DBServices.models import ChatConfiguration

from ChatBot.constant.constants import Constants
from ChatBot.constant.error_messages import ErrorMessages

from ChatBot.views.websocket_client import get_text_message_input, send_whatsapp_message, get_template_message
from django.conf import settings
client = WebSocketClient()

logger = logging.getLogger(__name__)

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_message_json(wa_id, message_body,message_type):
    return {
            "message": json.dumps({
                "id": str(uuid.uuid4()),
                "csr_id": None,
                "source": "user",
                "wa_id":wa_id,
                "message_marker": "LOGGED",
                "dimension_action_json": {},
                "message_text": message_body,
                "media_url": None,
                "parent_message_uuid": None,
                "created_at": int(time.time() * 1000),
                "message_type" :message_type
            })
    }


async def process_template_status_update(body):
    business_id = body['entry'][0]['id']
    template_id = body['entry'][0]['changes'][0]['value']['message_template_id']
    event_status = body['entry'][0]['changes'][0]['value']['event']
    status_reason = body['entry'][0]['changes'][0]['value']['reason']
    try:
        chat_config = await sync_to_async(ChatConfiguration.objects.get)(
            chat_details_json__whatsApp__businessId=business_id
        )
        chat_details_json = chat_config.chat_details_json
        templates = chat_details_json.get('templates', [])

        template_found = False
        for template in templates:
            if template.get('templateUUID') == str(template_id):
                if event_status == Constants.PENDING_DELETION:
                    templates.remove(template)
                else:
                    template['templateStatus'] = event_status
                    template["templateStatusReason"] = status_reason
                template_found = True
                break

        if not template_found:
            logging.error(ErrorMessages.TEMPLATE_NOT_FOUND)
        chat_config.chat_details_json['templates'] = templates
        await sync_to_async(chat_config.save)()

    except ChatConfiguration.DoesNotExist:
        logging.error(ErrorMessages.CONFIGURATION_NOT_EXIST)
    except Exception as e:
        logging.error(ErrorMessages.CANNOT_PROCESS_TEMPLATE.format(reason = str(e)))


async def process_whatsapp_message(body):

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    messages = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = None
    message_type = messages["type"]
    if message_type == "text":
        message_body = messages["text"]["body"]

    elif message_type == "button":
        message_body = messages["button"]["text"]

    # AI Integration
    try:
        await client.send_message_to_socket(message = json.dumps(get_message_json(wa_id, message_body,message_type)), wa_id = wa_id, message_type=message_type)
    except Exception as e:
        logging.error(f"Error in WebSocket communication: {e}")

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def is_template_status_update(body):
    """
       Check if the incoming webhook event has a valid WhatsApp template status structure.
       """
    return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("field") == "message_template_status_update"
    )

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    _initialized = False
    _client = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize WebSocketClient only once when the view is instantiated
        if not WhatsAppWebhookView._initialized:
            WhatsAppWebhookView._client = WebSocketClient()
            asyncio.create_task(WhatsAppWebhookView._client.periodic_cleanup())
            WhatsAppWebhookView._initialized = True

    async def get(self, request, *args, **kwargs):
        return self.verify(request)

    async def post(self, request, *args, **kwargs):
        return await self.handle_message(request)

    def verify(self, request):
        # Verification
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode and token:
            if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
                logging.info("WEBHOOK_VERIFIED")
                return HttpResponse(challenge, status=200)
            else:
                logging.info("VERIFICATION_FAILED")
                return JsonResponse({"status": "error", "message": "Verification failed"}, status=403)
        else:
            logging.info("MISSING_PARAMETER")
            return JsonResponse({"status": "error", "message": "Missing parameters"}, status=400)

    async def handle_message(self, request):
        # Handle incoming webhook events from the WhatsApp API
        body = json.loads(request.body.decode('utf-8'))
        logging.info(f"request body: {body}")

        # Check if it's a WhatsApp status update
        if (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        ):
            logging.info("Received a WhatsApp status update.")
            return JsonResponse({"status": "ok"}, status=200)

        try:
            if is_template_status_update(body):
                await process_template_status_update(body)
                return JsonResponse({"status": "ok"}, status=200)

            if is_valid_whatsapp_message(body):
                await self.process_whatsapp_message(body)
                return JsonResponse({"status": "ok"}, status=200)
            else:
                # if the request is not a WhatsApp API event, return an error
                return JsonResponse({"status": "error", "message": "Not a WhatsApp API event"}, status=404)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON provided"}, status=400)

    
    async def process_whatsapp_message(self, body):
        value = body["entry"][0]["changes"][0]["value"]
        whatsapp_business_account_id = body["entry"][0]["id"]
        phone_number_id = value['metadata']['phone_number_id']
        wa_id = value["contacts"][0]["wa_id"]
        user_name = value["contacts"][0]["profile"]["name"]
        messages = value["messages"][0]
        message_body = None
        message_type = messages["type"]
        if message_type == "text":
            message_body = messages["text"]["body"]

        elif message_type == "button":
            message_body = messages["button"]["text"]

        elif message_type == "request_welcome":
            data = get_template_message(wa_id, "welcome_message")
            send_whatsapp_message(data)
            return

        else:
            message_text = "Sorry, I can only process text messages at the moment. Please send your query as a text message."
            data = get_text_message_input(wa_id, message_text)
            send_whatsapp_message(data)
            return

        # AI Integration
        client = self.__class__._client
        if client:
            try:
                await client.send_message_to_socket(message = json.dumps(get_message_json(wa_id, message_body, message_type)), wa_id = wa_id, user_name=user_name, phone_number_id=phone_number_id, whatsapp_business_account_id=whatsapp_business_account_id)
            except Exception as e:
                logging.error(f"******Error in WebSocket communication:***** {e}")
        else:
            logging.error("******Client is not initialized******")
