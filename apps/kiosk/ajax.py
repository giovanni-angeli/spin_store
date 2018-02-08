# -*- coding: utf-8 -*-
import json
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.db import models

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.conf import settings
# ~ from constance import config
from apps.kiosk import config

import devices
from devices import errors

# ~ from alfalib.recipes.models import Recipe
# ~ from alfalib.customizations.models import Customization
# ~ from alfalib.recipes.utils import adjusted_color_code


class JSONResponse(HttpResponse):
    """ An HttpResponse that renders its content into JSON
    """
    def __init__(self, data, **kwargs):
        
        if isinstance(data, bytes):
            data = data.decode()
        
        content = json.dumps(data)
        super(JSONResponse, self).__init__(
            content=content,
            content_type='application/json',
            **kwargs
        )


# PAGES

def color_available(request):
    """
    Returns available = True iff `recipe` can be dispensed

    :param request:
    :return:
    """

    if request.method != 'POST':
        return HttpResponseBadRequest()

    available = True

    try:
        from alfalib.recipes.models import Recipe
        from apps.kiosk.machine.levels import api as levels
        from apps.kiosk.devices.models import Device

        recipe = Recipe.objects.get(id=request.POST['recipe'])
        components = recipe.split_components(size=100)  # size does not really matter ;-)

        machine = Device.objects.get_default_machine()
        machine.agent.map_components_to_pipes(components, fail_silently=False)

        # DEBUG DEBUG DEBUG
        # PROBABILMENTE e perche la non ho una vera machine,
        # attivare il "simulatore" per continuare a debuggare

        for c in components:
            if not levels.can_dispense(c['pipe']):
                logging.warning('Recipe {recipe} can not be dispensed. Notifying the user...')
                available = False
                break

    # ~ except Exception, e:
    except Exception as e:
        logging.error(unicode(e))
        pass

    return JSONResponse(data=dict(
        available=available
    ))


def payment_credit(request):
    """
    Payment related polling view.

    :param request: (GET method)
    :return: refer to the comments below
    """
    from apps.kiosk.utils import is_payment_enabled, format_currency

    if request.method != 'GET':
        return HttpResponseBadRequest()

    if not is_payment_enabled():
        return JSONResponse(data=dict(
            credit='',
            granted=True
        ))

    sts = devices.get_device_status('payment')
    try:
        value = float(sts['credit'] or "0.00")
    except:
        logging.error('No credit information available. Defaulting to 0.00')
        value = 0.00

    return JSONResponse(data=dict(

        # The credit as a locale-aware currency representation
        credit=format_currency(config.UI_LOCALE, value),

        # True iff dispensation is granted
        granted=value >= float(config.PRICE_TAG or "0.00")
    ))


def payment_charge(request):
    """
    Charges the amount corresponding to PRICE_TAG

    :param request: (POST method)
    :return:
    """
    from apps.kiosk.queues.command.payment import send_charge
    from apps.kiosk.queues.reply import rrr
    from apps.kiosk.utils import is_payment_enabled

    if request.method != 'POST':
        return HttpResponseBadRequest()

    if is_payment_enabled():

        try:
            price = float(config.PRICE_TAG)

        # ~ except ValueError, e:
        except ValueError as e:
            logging.error('Invalid price tag configuration! Defaulting to 0.00 (i.e. free sample)')
            price = 0.00

        reply = rrr(send_charge, price)
        if reply is None or reply['status_code'] != 0:
            return HttpResponseServerError()

    return JSONResponse(data={})  # ok


def payment_collect(request):
    """
    Flush current credit

    :param request:
    :return:
    """
    from apps.kiosk.queues.command.payment import send_collect
    from apps.kiosk.queues.reply import rrr
    from apps.kiosk.utils import is_payment_enabled

    if request.method != 'POST':
        return HttpResponseBadRequest()

    if is_payment_enabled():

        reply = rrr(send_collect)
        if reply is None or reply['status_code'] != 0:
            return HttpResponseServerError()

    return JSONResponse(data={})  # ok


def payment_refund(request):
    """
    Prints a refund label using `labeler` device.

    :param request:
    :return:
    """
    from apps.kiosk.queues.command.labeler import send_refund
    from apps.kiosk.queues.reply import rrr

    from apps.kiosk.utils import is_payment_enabled

    if request.method != 'POST':
        return HttpResponseBadRequest()

    if is_payment_enabled():
        sts = devices.get_device_status('payment')
        value = float(sts['credit'] or "0.00")

        # TODO: make this message configurable
        explanation0 = _('You are eligible for a')
        explanation1 = _('refund. Ask the clerks.')

        kwargs = {
            'locale': config.UI_LOCALE,
            'amount': '%.02f' % value,  # it's up to the client to properly localize the representation
            'explanation0': unicode(explanation0),  # force evaluation
            'explanation1': unicode(explanation1),  # force evaluation
        }
        reply = rrr(send_refund, **kwargs)

        if reply is None or reply['status_code'] != 0:
            return HttpResponseServerError()

    return JSONResponse(data={})  # ok


def payment_enable(request):
    """
    Enables payment devices.
    Note: Currently one device only is supported.

    :param request:
    :return: 200 successful, 500 failed.
    """
    from apps.kiosk.queues.command.payment import send_enable
    from apps.kiosk.utils import is_payment_enabled
    from apps.kiosk.queues.reply import rrr

    if request.method != 'POST':
        return HttpResponseBadRequest()

    # A temporary hack for Farbe. Prevent enable the coin acceptor
    return JSONResponse(data={})  # ok

    if is_payment_enabled():
        reply = rrr(send_enable)
        if reply is None or reply['status_code']  != 0:
            return HttpResponseServerError()

    return JSONResponse(data={})  # ok


def payment_disable(request):
    """
    Disables payment devices.
    Note: Currently one device only is supported.

    :param request:
    :return: 200 successful, 500 failed.
    """
    from apps.kiosk.queues.command.payment import send_disable
    from apps.kiosk.utils import is_payment_enabled
    from apps.kiosk.queues.reply import rrr

    if request.method != 'POST':
        return HttpResponseBadRequest()

    if is_payment_enabled():
        reply = rrr(send_disable)
        if reply is None or reply['status_code']  != 0:
            return HttpResponseServerError()

    return JSONResponse(data={})  # ok


def status(request):
    """
    Returns the error, if present.

    :param request:
    :return:
    """
    code, device, message = errors.get_error()
    return JSONResponse(data=dict(
        code=code,
        device=device,
        message=message
    ))


def status_dismiss(request):
    """
    Dismisses the error.

    :param request:
    :return:
    """
    errors.dismiss_user_error()
    return HttpResponse()

# values for code-list-display customization item
CODE_LIST_DISPLAY_DEFAULT = 'default'
CODE_LIST_DISPLAY_DESCRIPTION = 'description'
CODE_LIST_DISPLAY_SHORT_DESCRIPTION = 'short-description'

# values for code-list-orderby customization item
CODE_LIST_ORDERBY_DEFAULT = 'default'

CODE_LIST_ORDERBY_CODE_ASC = 'code-asc'
CODE_LIST_ORDERBY_CODE_DESC = 'code-desc'

CODE_LIST_ORDERBY_SAT_ASC = 'sat-asc'
CODE_LIST_ORDERBY_SAT_DESC = 'sat-desc'

PAGE_SIZE = 7  # tailored on the UI HTML. It's ok to hard-code here. Must be >= 2


# a few helpers
def aux_code_list_display_default(recipe):
    return {
        'id': str(recipe['id']),  # fix UUID json serialization issue
        'code': recipe['code'],
        'description': '',
        'color': recipe['adjusted_color_code']
    }


def aux_code_list_display_description(recipe):
    return {
        'id': str(recipe['id']),  # fix UUID json serialization issue
        'code': recipe['code'],
        'description': recipe['description'],
        'color': recipe['adjusted_color_code']
    }


def aux_code_list_display_short_description(recipe):
    return {
        'id': str(recipe['id']),  # fix UUID json serialization issue
        'code': recipe['code'],
        'description': recipe['short_description'],
        'color': recipe['adjusted_color_code']
    }


def colors(request):
    """Return the HTML color list filtering by the search string if available."""

    try:
        customization = Customization.objects.get(uid=config.CUSTOMIZATION)

        # ordering selection
        code_list_orderby = customization.get_item_value('code-list-orderby',
                                                         default=CODE_LIST_ORDERBY_DEFAULT)

        if code_list_orderby == CODE_LIST_ORDERBY_CODE_ASC:
            orderby = 'code'

        elif code_list_orderby == CODE_LIST_ORDERBY_CODE_DESC:
            orderby = '-code'

        elif code_list_orderby == CODE_LIST_ORDERBY_SAT_ASC:
            orderby = 's'

        elif code_list_orderby == CODE_LIST_ORDERBY_SAT_DESC:
           orderby = '-s'

        # if no ordering has been selected, default ordering is (code, ASC)
        else:
            orderby = 'code'

        # additional field display selection
        code_list_display = customization.get_item_value('code-list-display',
                                                         default=CODE_LIST_DISPLAY_DEFAULT)

        if code_list_display == CODE_LIST_DISPLAY_DESCRIPTION:
            aux = aux_code_list_display_description

        elif code_list_display == CODE_LIST_DISPLAY_SHORT_DESCRIPTION:
            aux = aux_code_list_display_short_description

        # if no display helper has been selected, select the default one (pigment code only
        else:
            aux = aux_code_list_display_default

        # Search fields
        searchby = customization.get_item_value('color-list-searchby', default='code')

    # no customization object found, use defaults
    except Customization.DoesNotExist:
        orderby = 'code'
        searchby = 'code'
        aux = aux_code_list_display_default
        code_list_display = None

    if searchby:
        searchby = [x.strip() for x in searchby.split(';')]
    else:
        searchby = 'code'
        if code_list_display == CODE_LIST_DISPLAY_DESCRIPTION:
            searchby += ';description'

        elif code_list_display == CODE_LIST_DISPLAY_SHORT_DESCRIPTION:
            searchby += ';short_description'

        searchby = [x.strip() for x in searchby.split(';')]

    query = unicode(request.GET.get('q', ''))\
        .replace(unichr(160), ' ')  # Fix the &nbsp; char

    qs = Recipe.objects.published().filter(products__in=[config.KIOSK_DEFAULT_PRODUCT_ID])

    recipes = []
    Q = models.Q()
    if 'code' in searchby:
        try:
            # if there is a exact Code match, it goes first
            recipes.append(qs.filter(code__iexact=query)\
                .values('id', 'code', 'description', 'short_description', 'r', 'g', 'b')[0])
        except IndexError:
            pass
        Q |= models.Q(code__icontains=query)

    if 'description' in searchby:
        try:
            # if there is an exact Description match, it goes next
            recipes.append(qs.filter(description__iexact=query)\
                .values('id', 'code', 'description', 'short_description', 'r', 'g', 'b')[0])
        except IndexError:
            pass
        Q |= models.Q(description__icontains=query)

    if 'short_description' in searchby:
        try:
            # if there is an exact Description match, it goes next
            recipes.append(qs.filter(short_description__iexact=query)\
                .values('id', 'code', 'description', 'short_description', 'r', 'g', 'b')[0])
        except IndexError:
            pass
        Q |= models.Q(description__icontains=query)

    # than get all other that match partially
    recipes_ = qs.filter(Q).exclude(id__in=[r['id'] for r in recipes]).distinct()\
        .order_by(orderby).values('id', 'code', 'description', 'short_description', 'r', 'g', 'b')

    recipes += list(recipes_)

    # pagination
    page = int(request.GET.get('p', 0))
    recipes = recipes[PAGE_SIZE * page:PAGE_SIZE * (1 + page)]

    # supply adjusted colors FIXME: this should be precalculated upon S_percentage and V_percentage change (performance)
    adj_S_percentage = config.UI_ADJUST_COLOR_S
    adj_V_percentage = config.UI_ADJUST_COLOR_V
    for recipe in recipes:
        recipe['adjusted_color_code'] = adjusted_color_code(recipe['r'], recipe['g'], recipe['b'],
                                                            adj_S_percentage, adj_V_percentage)

    return JSONResponse(data={
        'recipes': map(aux, recipes)
    })


def set_language(request, lang_code):

    def check_for_language(lang_code):
        return lang_code in [item[0] for item in settings.LANGUAGES]

    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        # else:
        #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        translation.activate(lang_code)
    else:
        raise Http404
    return HttpResponse()


def shutter_message(request):
    """
    Returns a shutter message if applicable, an empty string otherwise

    :param request:
    :return:
    {
        'message': <shutter message>
    }
    """
    from devices import get_connection
    
    return JSONResponse(data={
        'message': get_connection().get(
            'ui:shutter-message'
        ) or ''
    })


def label_busy(request):
    """
    Returns True iff the ui:label-busy key exists

    :param request:
    :return:
    {
        'busy': True or False
    }
    """
    from devices import get_connection
    
    return JSONResponse(data={
        'label_busy': get_connection().get(
            'ui:label-busy'
        ) and 1 or 0
    })
