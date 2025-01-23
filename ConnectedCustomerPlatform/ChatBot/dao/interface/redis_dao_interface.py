from abc import ABC, abstractmethod
from typing import Optional


class IRedisDao(ABC):
    """
        It manages all redis operations like get data, set data, is_data_present, get all keys, get all data by list of keys
    """
    @abstractmethod
    def get_hash_field_value(self, key: str, field: str) -> Optional[str]:
        """
            Retrieves the value of a specified field for a given key.
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