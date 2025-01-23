from typing import Dict, Any, Optional

from django.db.models import Q, Case, When, Value, IntegerField

from DatabaseApp.models import Prompt

import logging

from EmailApp.DataClasses.response.prompt_dimension_details import PromptDimensionDetails
from WiseFlow.dao.interface.prompt_dao_interface import IPromptDao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class PromptDaoImpl(IPromptDao):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PromptDaoImpl, cls).__new__(cls)
        return cls._instance

    def fetch_prompt_by_category_filter_json(self, customer_uuid: str, application_uuid: str,
                                             filter_json: Dict[str, Any]= {}, category_name: str = None) -> Optional[dict]:
        """
        fetches prompt based on filters
        Args:
            customer_uuid:
            application_uuid:
            filter_json:
            category_name:

        Returns:
        return prompt
        """
        logger.info("In fetch_prompt_for_services")

        # Parse filter_json into an instance of PromptDimensionDetails
        if filter_json is not None:
            filter_json = PromptDimensionDetails(**filter_json)


        # Start with the base filters
        prompt_fetching_filters = Q(status=True, customer_uuid=customer_uuid,
                                    application_uuid=application_uuid, is_deleted=False)

        # Add category name filter if provided
        if category_name:
            prompt_fetching_filters &= Q(prompt_category_uuid__prompt_category_name=category_name)
        customer_client = None
        if filter_json is not None:

            if filter_json.intent.uuid:
                prompt_fetching_filters &= Q(prompt_dimension_details_json__intent__uuid=filter_json.intent.uuid)
            if filter_json.intent.sub_intent.uuid:
                prompt_fetching_filters &= Q(prompt_dimension_details_json__intent__sub_intent__uuid=filter_json.intent.sub_intent.uuid)

                customer_client = filter_json.customer_client.uuid


        try:
            # Single query to handle both cases
            query = prompt_fetching_filters

            # Use Case-When to prioritize rows where customer_client.uuid matches, and fallback otherwise
            prompt = Prompt.objects.annotate(
                priority=Case(
                    When(prompt_dimension_details_json__customer_client__uuid=customer_client, then=Value(0)),
                    default=Value(1),  # Other cases
                    output_field=IntegerField(),
                )
            ).filter(query).order_by('priority').values_list('prompt_details_json',flat=True).first()

            # If no prompt is found, log an error and return None
            if not prompt:
                logger.error(f"{category_name} prompt does not exist with filter {filter_json}")
                return None

            logger.info(f"{category_name} prompt fetched successfully.")
            return prompt

        except Prompt.DoesNotExist:
            logger.error(f"{category_name} prompt does not exist.")
            return None