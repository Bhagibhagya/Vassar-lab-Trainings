from abc import abstractmethod, ABC

class IIntentClassificationHandlerService(ABC):

    def identify_intent_sub_intent(self,customer_uuid:str, application_uuid:str,validated_payload:dict,selected_intents,variables):
        """
        This method identifies the intent and sub-intent based on the provided input data. It fetches necessary details
        such as intent and sub-intent configurations, prompts, and then performs classification.

        Args:
            customer_uuid (str): The UUID of the customer.
            application_uuid (str): The UUID of the application.
            validated_payload (dict): The validated input data containing relevant information for classification.
            selected_intents: A list of selected intents for classification.
            variables: Additional variables that might be used in the classification process.

        Returns:
            The identified intent and sub-intent variable.
        """
        pass