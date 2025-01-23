from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from django.conf import settings as cred
settings = BotFrameworkAdapterSettings(
    app_id=cred.APP_ID,
    app_password=cred.APP_PASSWORD
)

adapter = BotFrameworkAdapter(settings)
