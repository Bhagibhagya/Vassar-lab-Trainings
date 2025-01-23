import logging

from DBServices.models import ChatConfiguration
from channels.db import database_sync_to_async
from ConnectedCustomerPlatform.exceptions import CustomException
from ChatBot.constant.error_messages import ErrorMessages
from psycopg import DatabaseError
from rest_framework import status

logger = logging.getLogger(__name__)
@database_sync_to_async
def get_template_by_bot_id(bot_id):
    """Retrieve the templates from the database using the bot ID."""
    try:
        # Query the database for the chat configuration
        chat_config = ChatConfiguration.objects.filter(chat_details_json__contains={'bot_id': bot_id}).first()

        # Check if a valid chat configuration was found
        if chat_config:
            return chat_config.chat_details_json

        # Log and raise an exception if the bot ID was not found
        logging.error(f"Bot ID {bot_id} not found in chat configuration")
        raise CustomException(
            ErrorMessages.BOT_ID_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )

    except DatabaseError as e:
        # Log and raise an exception for database-related errors
        logging.error(f"****Error fetching conversation UUID from database****** {e}")
        raise CustomException(
            ErrorMessages.DATABASE_FETCH_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        # Log and raise a generic exception for other errors
        logging.error(f"****Unexpected error fetching conversation UUID****** {e}")
        raise CustomException(
            ErrorMessages.DATABASE_FETCH_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )