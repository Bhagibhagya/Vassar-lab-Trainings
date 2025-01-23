import json
import logging
import traceback
from collections import Counter

from ChatBot.constant.constants import Constants
from channels.layers import get_channel_layer

from ChatBot.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.redis_service = RedisService()
        pass

    async def notify_user_with_new_csr_data(self, csr_id, csr_name, channel_id, room_name, turn):
        try:
            """
                        Notifies a user about their assigned Csr_details

                        Parameters:
                        - csr_id: The identifier for the CSR  being notified.
                        - csr_name: The name of the CSR being notified.
            """
            logger.info("user_service.py :: UserService :: notify_user_with_new_csr_data")
            result = {
                Constants.CSR_UID: csr_id,
                Constants.NAME: csr_name,
                Constants.TURN: turn
            }
            channel_layer = get_channel_layer()
            logger.info(f"before notifying the user :: notifying data :: {result}")
            await channel_layer.group_send(
                    room_name,
                    {
                        'type': "notify_user_message",
                        Constants.CSR_INFO_JSON: result,
                        'exclude_channel': channel_id  # this channel_id is the current_csr channel_id
                    }
            )
            logger.info("notification to user is successful")
            return {"result": Constants.NOTIFY_USER_SUCCESS_MESSAGE, "status": True}
        except Exception as e:
            logger.info(f"got exception in notify_user_with_new_csr_data method of UserService class")
            logger.info(f"exception:: {str(e)}")
            # Get the traceback information
            tb_info = traceback.extract_tb(e.__traceback__)
            # Extract the line number from the traceback
            line_number = tb_info[-1].lineno
            # Print the line number
            logger.info(f"Exception occurred at line number: {line_number}")
            traceback.print_exc()
            return {"result": str(e), "status": False}
