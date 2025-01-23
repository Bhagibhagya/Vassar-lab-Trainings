from django.conf import settings
from importlib import import_module


def get_service(service_name):
    service_path = settings.SERVICES[service_name]
    module_name, class_name = service_path.rsplit(".", 1)
    module = import_module(module_name)
    service_class = getattr(module, class_name)
    return service_class()
