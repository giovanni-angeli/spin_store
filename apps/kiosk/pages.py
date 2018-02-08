import json
from django.http import HttpResponseBadRequest
from alfalib.navigator.page import Page, Pages
from constance import config
from alfakiosk.devices import devices
import alfalib.navigator.models as navigator


class Navi(navigator.Navi):

    app_name = 'kiosk'

    # noinspection PyMissingConstructor
    def __init__(self):
        # home | select_color | confirm_selection |
        # progress_bar | dispensed

        self.home = 'kiosk.home'

        self.table = {
            'kiosk.home': {
                'previous': '',
                'next': 'kiosk.select_color',
                'content': 'kiosk.select_color',
            },
            'kiosk.select_color': {
                'previous': 'kiosk.home',
                'next': '!kiosk.confirm_selection',
            },
            'kiosk.confirm_selection': {
                'previous': 'kiosk.select_color',
                'next': 'kiosk.progress_bar',
            },
            'kiosk.progress_bar': {
                'previous': '',
                # 'next': '',
                'continue': '',
                'next': '',
            },
            'kiosk.dispensed': {
                'previous': 'kiosk.select_color',
                'next': 'kiosk.home',
                'left-bar': 'kiosk.select_color',  # no here means yes, see js
            },
        }

    def get_nav(self, page_name):
        return super(Navi, self).get_nav(page_name)


class KioskPage(Page):

    def build_response(self, request):
        self.context.update({
            'keyboard_layout': config.KEYBOARD_LAYOUT,
        })
        ret = super(KioskPage, self).build_response(request)
        return ret


class ConfirmSelectionPage(KioskPage):

    def build_response(self, request):
        from alfakiosk.utils import is_payment_enabled

        available = json.loads(request.POST.get('available', 'false'))
        granted = json.loads(request.POST.get('granted', 'false'))
        payment = is_payment_enabled()  # Should we use payment?

        if payment:
            sts = devices.get_device_status('payment')
            try:
                value = float(sts['credit'] or '0.00')
            except:
                value = 0.00
        else:
            value = 0.00

        if available and not granted:
            granted = not payment or value >= float(config.PRICE_TAG or '0.00')

        elif not available:
            payment = False

        elif available and granted:
            payment = True

        else:
            return HttpResponseBadRequest()

        self.context.update({
            'available': available,
            'granted': granted,
            'payment': payment,
        })
        ret = super(ConfirmSelectionPage, self).build_response(request)
        return ret

Pages.pages['kiosk'] = {}
Pages.pages['kiosk']['home'] = KioskPage('kiosk', 'home')
Pages.pages['kiosk']['select_color'] = KioskPage('kiosk', 'select_color')
Pages.pages['kiosk']['confirm_selection'] = ConfirmSelectionPage('kiosk', 'confirm_selection')
Pages.pages['kiosk']['progress_bar'] = KioskPage('kiosk', 'progress_bar')
Pages.pages['kiosk']['dispensed'] = KioskPage('kiosk', 'dispensed')
