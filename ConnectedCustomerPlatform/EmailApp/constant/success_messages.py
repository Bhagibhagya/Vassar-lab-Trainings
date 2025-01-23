from drf_yasg import openapi
from rest_framework import status

class SuccessMessages:
    DRAFT_MAIL_CREATED_SUCCESS = "Draft conversation created successfully."
    DRAFT_MAIL_DELETED_SUCCESS = "Draft conversation deleted successfully."

    EMAIL_SENT_SUCCESS = "Email sent successfully."
    PROCESS_COMPLETED="Process completed successfully"
    POST_ORDER_SUCCESS = "extracted_order_details_json successfully updated."

    HEALTH_CHECK_RESPONSE = "Backend Service is Up"
    DRAFT_MAIL_UPDATED_SUCCESS = "Draft conversation updated successfully."

    UTTERANCE_SUCCESSFULLY_DELETED = "Selected Training phrase has been successfully deleted."
    EXAMPLES_INSERTED_SUCCESSFULLY = "Successfully inserted examples into ChromaDB"
    EVENT_RAISED_SUCCESSFULLY = "Event raised successfully."

class PersonalizationSuccessMessages:
    RESPONSE_RECORD_DELETED="Responses record successfully deleted"
    UPLOADED_RESPONSES_AS_EXAMPLES="Successfully uploaded responses as examples"
