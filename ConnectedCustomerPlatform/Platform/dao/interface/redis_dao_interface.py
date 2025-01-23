from abc import ABC, abstractmethod

class IRedisDao(ABC):
    """
        Service layer for handling redis logic such as fetching, storing etc.
    """
    @abstractmethod
    def get_data_by_key(self, key: str):
        """
            Method to fetch data by key
            Parameters:
                key (str): key to fetch data from redis.
            Returns:
                Json string: returns json string representation of data
        """

    @abstractmethod
    def set_data_by_key(self, key: str, data:str)->bool:
        """
            Method to set data by key
            Parameters:
                key (str): key to set data.
                data (Any) : data to set with key in redis
            Returns:
                - True: if the operation is successful.
                - False: if the operation fails
        """

    @abstractmethod
    def set_data_by_key_with_expiry(self, key: str, data:str,expiry:int)->bool:
        """
            Method to set data by key
            Parameters:
                key (str): key to set data.
                expiry (int): expiration time in seconds
                data (Any) : data to set with key in redis
            Returns:
                - True: if the operation is successful.
                - False: if the operation fails
        """
