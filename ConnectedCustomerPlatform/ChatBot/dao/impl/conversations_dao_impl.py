import logging

from django.db.models.expressions import RawSQL

from DatabaseApp.models import ChatConversation, Applications, Customers
from ChatBot.dao.interface.conversations_dao import IConversationsDao

logger = logging.getLogger(__name__)


class ConversationsDaoImpl(IConversationsDao):
    """
    DAO class responsible for interactions with the Conversations database model.
    """

    @staticmethod
    def get_conversation_by_uuid(conversation_uuid):
        """
        Fetches a conversation from the database by its UUID.
        
        Args:
            conversation_uuid (str): The UUID of the conversation.
        
        Returns:
            Conversation object if found, otherwise None.
        """
        return ChatConversation.objects.filter(chat_conversation_uuid=conversation_uuid,is_deleted=False).first()

    @staticmethod
    def get_conversation_by_ticket_uuid(ticket_uuid):
        """
        Fetches a conversation from the database by its UUID.

        Args:
            ticket_uuid (str): The UUID of the conversation.

        Returns:
            Conversation object if found, otherwise None.
        """
        return ChatConversation.objects.filter(ticket_uuid=ticket_uuid,is_deleted=False).first()

    @staticmethod
    def update_csr_info(conversation, csr_info):
        """
        Updates the csr_info_json field of the conversation in the database.
        
        Args:
            conversation (Conversations): The conversation object.
            csr_info (list): The updated csr info data.
        """
        conversation.csr_info_json = csr_info
        conversation.save()

    def save_conversation(self, conversation_data ):
        """Save the conversation data to the database."""
        try:
            # Fetching the foreign key instances from the database
            application_instance = Applications.objects.get(application_uuid=conversation_data.get('application_uuid'))
            customer_instance = Customers.objects.get(cust_uuid=conversation_data.get('customer_uuid'))
            # Preparing the data for model creation
            conversation = ChatConversation(
                chat_conversation_uuid=conversation_data.get('chat_conversation_uuid'),
                user_details_json=conversation_data.get('user_details_json'),
                conversation_status=conversation_data.get('conversation_status'),
                csr_info_json=conversation_data.get('csr_info_json'),
                csr_hand_off=conversation_data.get('csr_hand_off'),
                conversation_stats_json=conversation_data.get('conversation_stats_json'),
                conversation_feedback_transaction_json=conversation_data.get('conversation_feedback_transaction_json'),
                summary=conversation_data.get('summary'),
                application_uuid=application_instance,  # ForeignKey instance
                customer_uuid=customer_instance,  # ForeignKey instance
                message_details_json=conversation_data.get('message_details_json'),
                inserted_ts=conversation_data.get('inserted_ts'),
                updated_ts=conversation_data.get('updated_ts')
            )
            # Saving the conversation to the database
            conversation.save()

        except Applications.DoesNotExist:
            logger.error("Application does not exist")
            return
        except Customers.DoesNotExist:
            logger.error("Customer does not exist")
            return
        except Exception as e:
            logger.error(f"Unable to store the conversation with UUID {conversation_data.get('chat_conversation_uuid')} into the DB: {str(e)}")
            
    def get_user_chats(self, customer_uuid: str, user_id: str) -> list[dict]:
        
        chat_sessions = ChatConversation.objects.filter(
            customer_uuid=customer_uuid,
            user_details_json__user_uuid=user_id,is_deleted=False
        ).annotate(
            last_user_message=RawSQL(
                """
                    (SELECT message->>'message_text'
                    FROM jsonb_array_elements(message_details_json) AS message
                    WHERE message->>'source' = 'bot'
                    ORDER BY (message->>'created_at')::timestamp DESC
                    LIMIT 1)
                """,
                ()
            )
        ).filter(
            last_user_message__isnull=False
        ).values(
            'application_uuid',
            'chat_conversation_uuid',
            'last_user_message',
            'updated_ts',
            'inserted_ts'
        )
        
        chat_sessions = list(chat_sessions)
        return chat_sessions

    def save_chat_conversation_instance(self,chat_conversation):
        chat_conversation.save()

    def get_latest_conversation_uuid(self,primary_conversation_uuid,secondary_conversation_uuid):
        # primary_time = ChatConversation.objects.filter(chat_conversation_uuid=primary_conversation_uuid).
        primary_time = self.get_latest_message_time(primary_conversation_uuid)

        secondary_time = self.get_latest_message_time(secondary_conversation_uuid)
        if primary_time and secondary_time:
            return primary_conversation_uuid if primary_time>secondary_time else secondary_conversation_uuid
        else:
            return primary_conversation_uuid


    def get_latest_message_time(self,conversation_uuid):
        messages = ChatConversation.objects.filter(chat_conversation_uuid=conversation_uuid).values_list('message_details_json', flat=True).first()
        if len(messages) != 0:
            return messages[-1]['created_at']
        else:
            return None