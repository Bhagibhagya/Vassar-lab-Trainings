from abc import ABC, abstractmethod


class Factory(ABC):

    """
    Factory Interface
    """
    
    @abstractmethod
    def instantiate(self, *args, **kwargs) -> ABC:
        """
        Method to get an instance of a Interface based on a configuration
        on a singleton basis
        """
        pass