from ce_shared_services.data_streaming.azure_eventhub.impl.azure_eventhub_service import AzureEventHubService
from ce_shared_services.factory.scope.singleton import Singleton

class QueuingServiceFactory(Singleton):
    CLASSNAME_CLASS_MAP = {
        AzureEventHubService.__name__: AzureEventHubService
    }