from abc import ABC, abstractmethod

class CustomersDaoInterface(ABC):

    @abstractmethod
    def get_customer_name(self, customer_uuid):
        pass