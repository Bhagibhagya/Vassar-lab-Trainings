from abc import ABC, abstractmethod
from typing import Any


class ICaching(ABC):
    """
    Abstract base class for caching services.

    This interface ensures that any caching service (e.g., Redis, Memcached, etc.)
    implements a consistent set of methods.
    """

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache by key.

        Args:
            key (str): The key to retrieve.

        Returns:
            Any: The value associated with the key or None if the key doesn't exist.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key (str): The key to set.
            value (Any): The value to store.
            expire (int | None): Optional expiration time in seconds.

        Returns:
            bool: True if the value was set successfully, False otherwise.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Remove a key from the cache.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if the key was deleted, False otherwise.
        """
        pass