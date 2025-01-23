from django.conf import settings
from importlib import import_module


def get_dao(dao_name):
    dao_path = settings.DAO[dao_name]
    module_name, class_name = dao_path.rsplit(".", 1)
    module = import_module(module_name)
    dao_class = getattr(module, class_name)
    return dao_class()
