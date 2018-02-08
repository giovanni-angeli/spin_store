# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging 

# ~ from constance import config
from apps.kiosk import config
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from devices import errors, get_connection

# ~ from alfakiosk.machine.models import Pipe
# ~ from alfalib.customizations.models import Customization
# ~ from alfakiosk.redisdb import get_connection
# ~ from alfalib.navigator.models import Navigator


def main(request):
    """First and main page."""
    
    logging.warning("kiosk.views.main() request:{}".format(request))
    
    code, device, message = errors.get_error()

    logging.warning("kiosk.views.main() code, device, message :{}".format(code, device, message))

    conn = get_connection()

    #
    # UI Customization
    #
    # ~ try:
        # ~ customization = Customization.objects.get(uid=config.CUSTOMIZATION)
    # ~ except:
        # ~ customization = None

    background_color = '#FCAF3C'
    splash_url = "/static/kiosk/img/page-1-bg.jpg"
    logo_url = "/static/kiosk/img/logo.png"
    styles = ""

    # ~ if customization is not None:
        # ~ background_color = customization.get_item_value('background-color', background_color)
        # ~ styles = customization.get_item_value('styles', styles)
        # ~ splash_attachment = customization.get_item_attachment('splash')
        # ~ if splash_attachment is not None:
            # ~ splash_url = splash_attachment.url
        # ~ logo_attachment = customization.get_item_attachment('logo')
        # ~ if logo_attachment is not None:
            # ~ logo_url = logo_attachment.url

    # ~ from alfakiosk.devices.models import Device, DeviceManager
    # ~ labeler = DeviceManager.get_default_labeler(Device.objects)
    labeler = None

    return render(request, 'kiosk/main.html', {
        'check_interval':   config.DEVICES_DEFAULT_POLL_INTERVAL,
        'timeout':          config.KIOSK_TIMEOUT_INTERVAL,
        'diag_timeout':     config.KIOSK_DIAG_TIMEOUT_INTERVAL,
        'ooo': code is not None,
        'message': mark_safe(message),
        'shutter_message': conn.get('ui:shutter-message'),
        'label_busy': conn.get('ui:label-busy'),
        'use_labeler': labeler is not None and labeler.enabled,
        'background_color': background_color,
        'splash_url': splash_url,
        'logo_url': logo_url,
        'status_footer_message': status_footer(),
        # ~ 'Navigator': Navigator,
        'styles': styles,
    })


def status_footer():

    # http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib#24171358
    try:
        import netifaces

        PROTO = netifaces.AF_INET   # We want only IPv4, for now at least

        # Get list of network interfaces
        # Note: Can't filter for 'lo' here because Windows lacks it.
        ifaces = netifaces.interfaces()

        # Get all addresses (of all kinds) for each interface
        if_addrs = [netifaces.ifaddresses(iface) for iface in ifaces]

        # Filter for the desired address type
        if_inet_addrs = [addr[PROTO] for addr in if_addrs if PROTO in addr]

        iface_addrs = [s['addr'] for a in if_inet_addrs for s in a if 'addr' in s]
        # Can filter for '127.0.0.1' here.

        text = 'inet: ' + ', '.join(addr for addr in iface_addrs if not addr == '127.0.0.1')

    except:
        text = '...'
    return text


#@staff_member_required
@never_cache
def sample_table_circuit(request):
    """
    TODO: remove after "tableCircuit.csv removal" issue has been fixed
    """

    text = """
/dev/ttyS1
"""
    pipes = Pipe.objects.iterator()
    for pipe in pipes:
        try:
            text += '%d,%d\n' % (pipe.index, pipe.index)
        except:
            text += '???,???\n'
    return HttpResponse(text, content_type='text/plain')
