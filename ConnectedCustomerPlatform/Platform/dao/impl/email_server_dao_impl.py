from django.db.models import Value

from DatabaseApp.models import EmailServer
from EmailApp.constant.constants import ServerType
from Platform.dao.interface.email_server_dao_interface import IEmailServerDao
import logging
logger=logging.getLogger(__name__)
class EmailServerDaoImpl(IEmailServerDao):

    # Filters email servers by the given UUIDs, ensuring they are marked as default and not deleted.
    def get_default_email_servers_by_ids(self, email_server_uuids):
        return EmailServer.objects.filter(email_server_uuid__in=email_server_uuids, is_default=True, is_deleted=False)

    # Retrieves email servers, excluding the ones specified by the provided UUIDs.
    def get_default_email_servers_by_ids_excluded(self, email_server_uuids):
        return (EmailServer.objects.filter(is_default=True, is_deleted=False,server_type__in=[ServerType.SMTP.value,ServerType.IMAP.value]).exclude(email_server_uuid__in=email_server_uuids)
                .values('email_server_uuid', 'server_type', 'server_url', 'email_provider_name',
                        'port', 'is_default', is_ssl_enabled=Value(True)))

    def get_default_msal_server(self):
        logger.info("In EmailServerDaoImpl :: get_default_msal_server")
        return EmailServer.objects.filter(
            is_default=True,
            is_deleted=False,
            server_type=ServerType.MSAL.value
        ).first()
