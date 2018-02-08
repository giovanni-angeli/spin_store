from django.apps import AppConfig
from alfalib.navigator.models import Navigator
from .pages import Navi


class KioskAppConfig(AppConfig):

    name = 'alfakiosk.kiosk'
    verbose_name = "kiosk"

    def ready(self):
        Navigator.add_navi(Navi())
