from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Attachment, ChannelAccount, HeroCard, CardAction, ActionTypes
import logging
from ChatBot.constant.constants import Constants
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.constant.error_messages import ErrorMessages
from .utils import get_template_by_bot_id
from rest_framework import status
logger = logging.getLogger(__name__)


class MyBot(ActivityHandler):
    def __init__(self):
        super().__init__()

    async def on_message_activity(self, turn_context: TurnContext, response):
        """Handles incoming message activities and sends appropriate responses."""

        try:
            logger.info(f"Response: {response}")
            # Extract message_text
            try:
                message_text = response.get("message_text", None)
                specifications = response.get("specifications", {})
                bot_id = response.get("bot_id", None)

                if bot_id and message_text.lower() == Constants.START_CONVO:
                    # Await the asynchronous function to retrieve the template
                    template = await get_template_by_bot_id(bot_id)

                    # Extract the message and suggestions from the template
                    message = template.get("template", {}).get("message", "")
                    suggestions = template.get("template", {}).get("suggestions", [])

                    if suggestions:
                        # Dynamically create buttons based on the number of suggestions
                        buttons = [
                            CardAction(
                                type=ActionTypes.im_back,
                                title=suggestion,
                                value=suggestion
                            ) for suggestion in suggestions
                        ]

                        card = HeroCard(
                            text=message,
                            buttons=buttons
                        )
                        attachment = Attachment(
                            content_type="application/vnd.microsoft.card.hero",
                            content=card
                        )

                        # Send the hero card with dynamic suggestions
                        await turn_context.send_activity(MessageFactory.attachment(attachment))
                elif specifications:
                    suggestion_text = specifications.get("suggestion_text", None)
                    suggestions = specifications.get("suggestions", [])
                    buttons = []
                    if suggestions:
                        for suggestion in suggestions:
                            button_options = suggestion.get("button", {}).get("options", [])
                            for option in button_options:
                                buttons.append(
                                    CardAction(
                                        type=ActionTypes.im_back,
                                        title=option,
                                        value=option
                                    )
                                )
                    card = HeroCard(
                        text=suggestion_text if suggestion_text else message_text,
                        buttons=buttons
                    )
                    attachment = Attachment(
                        content_type="application/vnd.microsoft.card.hero",
                        content=card
                    )
                    await turn_context.send_activity(MessageFactory.attachment(attachment))
                else:
                    await turn_context.send_activity(MessageFactory.text(message_text))
            except CustomException as ce:
                # Handle custom exceptions with specific messages and status codes
                logger.error(f"{ErrorMessages.RESPONSE_PROCESSING_ERROR}: {ce.detail}")
                raise CustomException(ErrorMessages.RESPONSE_PROCESSING_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Handle unexpected exceptions
            logging.error(f"{ErrorMessages.RESPONSE_PROCESSING_ERROR}: {e}")
            raise CustomException(ErrorMessages.RESPONSE_PROCESSING_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
    #     try:
    #         for member in members_added:
    #             if member.id != turn_context.activity.recipient.id:
    #                 card = HeroCard(
    #                     text="Hello! How can I assist you today?",
    #                     buttons=[
    #                         CardAction(
    #                             type=ActionTypes.im_back,
    #                             title="Order Status",
    #                             value="Order Status"
    #                         ),
    #                         CardAction(
    #                             type=ActionTypes.im_back,
    #                             title="Returns",
    #                             value="Returns"
    #                         ),
    #                         CardAction(
    #                             type=ActionTypes.im_back,
    #                             title="Payments",
    #                             value="Payments"
    #                         ),
    #                         CardAction(
    #                             type=ActionTypes.im_back,
    #                             title="Product Information",
    #                             value="Product Information"
    #                         ),
    #                     ]
    #                 )
    #                 attachment = Attachment(
    #                     content_type="application/vnd.microsoft.card.hero",
    #                     content=card
    #                 )
    #                 # Send the hero card with suggestions
    #                 await turn_context.send_activity(MessageFactory.attachment(attachment))
    #     except Exception as e:
    #         logging.error(f"Error in on_members_added_activity: {e}")
    #         raise e
