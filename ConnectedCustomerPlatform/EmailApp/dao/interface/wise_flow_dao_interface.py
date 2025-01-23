from abc import ABC, abstractmethod

class WiseFlowDaoInterface(ABC):

    @abstractmethod
    def get_wiseflow(self, customer_uuid, application_uuid, channel_uuid):
        pass

    @abstractmethod
    def get_step_uuid(self, wise_flow_uuid, step_name):
        pass