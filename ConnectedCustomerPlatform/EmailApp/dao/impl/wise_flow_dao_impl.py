import logging

from DatabaseApp.models import Step, Wiseflow
from EmailApp.dao.interface.wise_flow_dao_interface import WiseFlowDaoInterface
from typing import Optional

logger = logging.getLogger(__name__)

class WiseFlowDaoImpl(WiseFlowDaoInterface):

    def get_wiseflow(self, customer_uuid, application_uuid, channel_uuid) -> Optional[Wiseflow]:
        # Fetch the wiseflow_uuid for the given customer, application, and channel UUIDs.
        # This query assumes there is only one matching Wiseflow record or that only the first match is needed.
        # If no match is found, it will return None.
        wiseflow = Wiseflow.objects.filter(
            customer_uuid=customer_uuid,
            application_uuid=application_uuid,
            channel_uuid=channel_uuid
        ).values_list('wiseflow_uuid',flat=True).first()
        
        return wiseflow
    
    def get_step_uuid(self, wise_flow_uuid, step_name) -> Optional[str]:
        # Fetch the step_uuid for the given wiseflow_uuid and step_name.
        # If no match is found, it will return None.
        step_uuid = Step.objects.filter(
            wiseflow_uuid=wise_flow_uuid,
            step_name=step_name
        ).values_list('step_uuid', flat=True).first()

        return step_uuid