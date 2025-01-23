from abc import ABC, abstractmethod


class IKeyVault(ABC):

    @abstractmethod
    def get_secret(self, secret_name: str):
        """
        Fetch a secret from Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The value of the secret.
        """
        pass

    @abstractmethod
    def get_secret_as_json(self, secret_name: str):
        """
        Fetch a secret in json from Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The json value of the secret.
        """
        pass

    @abstractmethod
    def set_secret(self, secret_name: str, secret_value: str, expires_on):
        """
        Store a secret in Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to set.
            secret_value (str): The value of the secret to set.
            expires_on (datetime): The value when the secret will expire.

        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_secret(self, secret_name: str):
        """
        Delete a secret from Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to delete.

        Returns:
            None
        """
        pass
