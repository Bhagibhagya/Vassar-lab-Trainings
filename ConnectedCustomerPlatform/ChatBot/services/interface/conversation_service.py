from abc import ABC, abstractmethod

class IConversationService(ABC):

    @abstractmethod
    def update_conversation_status(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in either Redis or DB.
        """
        pass

    @abstractmethod
    def _update_csr_status_in_redis(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in Redis cache.
        """
        pass

    @abstractmethod
    def _update_csr_status_in_db(self, conversation_uuid, csr_uid, csr_status):
        """
        Update the CSR status in the database using ConversationsDAO.
        """
        pass

    @abstractmethod
    def get_ongoing_conversations(self, csr_uid):
        """
        Retrieve a list of ongoing conversations for a specific CSR.
        """
        pass

    @abstractmethod
    def get_conversation_history_details(self, conversation_uuid):
        """
        Retrieve the conversation history details.
        """
        pass

    @abstractmethod
    def _update_media_urls(self, message_details):
        """
        Update media URLs in the message details with presigned URLs.
        """
        pass


    @abstractmethod
    def get_total_conversation_information(self, conversation_uuid):
        """
        Retrieve total conversation information including summary, intents, and sentiment.
        """
        pass

    @abstractmethod
    def _prepare_conversation_summary(self, conversation_data):
        """
        Prepare the summary of a conversation.
        """
        pass

    @abstractmethod
    def _extract_intents_and_sentiment(self, message_details_json):
        """
        Extract intents and sentiment from message details.
        """
        pass

    @abstractmethod
    def process_conversations(self):
        """
        Process conversations to check if any have exceeded the threshold and need to be saved.
        This should fetch conversation keys from Redis, analyze them, and take action if the threshold is exceeded.
        """
        pass

    @abstractmethod
    def get_latest_message_time(self, message_details):
        """
        Get the creation time of the latest message in the conversation.
        
        :param message_details: List of message details as dictionaries
        :return: Datetime of the latest message or None if there are no messages.
        """
        pass

    @abstractmethod
    def is_threshold_exceeded(self, created_at, now):
        """
        Check if the message creation time has exceeded the defined threshold.
        
        :param created_at: Datetime of the latest message
        :param now: Current datetime
        :return: Boolean whether the threshold is exceeded.
        """
        pass

    @abstractmethod
    def save_conversation_to_db_and_remove_from_redis(self, conversation_data):
        """
        Saves the conversation data to the database and removes it from Redis after successful saving.
        
        :param conversation_data: Dictionary containing conversation data to be saved
        """
        pass

    # @abstractmethod
    # def get_active_conversation(self, application_uuid, customer_uuid, active_list, user_uuid, start_date, end_date):
    #     """
    #             Method to fetch active conversations in organization application
    #             Parameters:
    #                     application_uuid (str) : uuid of application
    #                     customer_uuid (str)    : uuid of customer
    #                     active_list (list)     : list of "CSR_ONGOING" or "BOT_ONGOING" keywords
    #                     user_uuid (str): unique identifier of user
    #                     start_date (date)      : datetime field
    #                     end_date (date)        : datetime field
    #             Returns :
    #                     List of UnifiedActivity objects
    #     """