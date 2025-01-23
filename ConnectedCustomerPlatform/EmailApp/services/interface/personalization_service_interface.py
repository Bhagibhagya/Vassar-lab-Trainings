from abc import ABC, abstractmethod
from typing import List

class IPersonalizationServiceInterface(ABC):
    @abstractmethod
    def delete_response_configurations(self, customer_uuid: str, application_uuid: str, response_config_uuid: str) -> List[str]:
        """
        Delete email responses with response_config_uuid which is stored in metadata
        """
        pass

    @abstractmethod
    def fetch_intents_subintents_sentiment(self, customer_uuid: str, application_uuid: str) -> dict:
        """
        fetches intents, subintents and sentiments for given customer and application

        response format:
        {'intent_subintent':{intent1:[subintent1,subintent2]}
        'sentiment':[sentiment1,sentiment2]}
        """
        pass

    
    @abstractmethod
    def save_response_configurations(self, validated_data, headers, files) ->bool:
        """
        Saves response configurations by processing request data and uploaded files.
        :param : customer_uuid
        :param : application_uuid
        :param: user_uuid
        :param files: The uploaded excel file
        :param validated_data: The validated request data(intent,sub_intent,sentiment,response_config_uuid,is_default).
        :return: Success status
        """
        pass
    @abstractmethod
    def fetch_dimension_utterances_for_customer_application(self,params: dict,customer_uuid: str,application_uuid: str, user_uuid: str,dimension_names,parent_dimension_name):
        """
        This method is to fetch utterances of given intent with  specified collection(customer, application)

        :param params:
        :param customer_uuid:
        :param application_uuid:
        :param dimension_uuid:
        :param user_uuid:
        :return:  A dictionary containing paginated utterance data.
        """
        pass

    def delete_utterance_from_chroma_server(self, customer_uuid: str, application_uuid: str, utterance_id: str,mapping_uuid: str,child_dimension_names,parent_dimension_name):
        """
        Deletes a specific utterance from the Chroma DB for a given customer and application.

        :param customer_uuid:
        :param application_uuid:
        :param utterance_id:
        :return: The ID of the deleted utterance for tracking purposes
        """
        pass

    def download_template(self) -> dict :
        """
        Downloads the default template which is stored in azure and the url is stored in constants
        """
        pass
    def fetch_response_configurations(self,customer_uuid :str ,application_uuid: str ,user_uuid : str,is_default: str) -> List[dict]:

        """
        Fetch the saved response configuration with metadata_combination and excel file url.
        if is_default is True fetch configurations of csr_Admin
        else: fetch configurations uploaded by the csr user
        """
        pass