from . import config
from django.utils.translation import ugettext as _

from django.core.serializers.json import Serializer as JSONSerializer
from orm.models import Device, Table, Pipe

import contextlib
import locale
import logging

@contextlib.contextmanager
def safe_setlocale(loc):
    """
    This context manager can be used in conjunction with the `with` statement to
    run a block of code in a specific locale. The current locale is restored when
    leaving the inner block.

    E.g.:

    [CODE]
    with safe_setlocale(loc):
        out = locale.currency(value, grouping=True)
    [/CODE]

    :param loc:
    :return:
    """
    loc = str(loc)  # locale module does not play well with unicode
    saved = locale.setlocale(locale.LC_ALL)

    try:
        locale.setlocale(locale.LC_ALL, loc)

    except Exception as e:
        # fallback to a supported locale if given one isn't
        logging.warning('Locale `{loc}` not available, falling back to `en_US.utf8` ({msg})'.format(
            loc=loc,
            msg=unicode(e)
        ))
        locale.setlocale(locale.LC_ALL, "en_US.utf8")

    yield

    locale.setlocale(locale.LC_ALL, saved)


def format_currency(loc, value):
    """
    Uses the safe_setlocale context manager to format a currency value according
    to the selected locale

    :param loc: the locale (e.g. 'en_US.utf8')
    :return:
    """
    with safe_setlocale(loc):
        out = locale.currency(value, grouping=True)

    return out


def is_payment_enabled():
    """
    Payment enabled?

    :return: true iff payment is enabled
    """
    try:
        price_tag = float(config.PRICE_TAG)

    except:
        price_tag = 0.00

    return 0.00 < price_tag


def dump_kiosk(out):
    """
    Dump a fixture of specified System and all related objects
    """

    # list models to be dumped
    models = [
        Device,
        Table,
        Pipe,
    ]

    # collect all objects from every model
    collected = []
    for m in models:
        for r in m.objects.all():
            collected.append(r)

    serializer = JSONSerializer()
    out.write(serializer.serialize(collected, indent=4))


def schedule_autopurge():
    """
    Schedule an autopurge, using the dispensation queue daemon
    """
    # Append a new dispensation job to the queue
    from alfalib.client.models import DispensationQueueBase, DispensationQueue
    from alfalib.client.models import Event

    def aux(p):
        return p, p.purge_volume

    recipe = map(aux, filter(lambda o: o.pigment is not None, Pipe.objects.all()))
    DispensationQueue.objects.create_from_custom_recipe(
        config.DEFAULT_SYSTEM_ID,
        [(pipe.pigment.id, qty) for pipe, qty in recipe],
        100, type=DispensationQueueBase.TYPE_PURGE)  # FIXME: hardcoded size

    evt = Event.objects.create(
        event_type=Event.EVENT_PURGE,
        message=_('Automatic purge initialized'))
    evt.save()


def get_referer_view(request, default=None):
    """
    Return the referer view of the current request

    Example:

        def some_view(request):
            ...
            referer_view = get_referer_view(request)
            return HttpResponseRedirect(referer_view, '/accounts/login/')
    """
    import re

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    # if referer[0] != request.META.get('SERVER_NAME'):
    #     return default

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer

def create_initial_admin_user():

    from django.contrib.auth.hashers import make_password
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    if 0 < user_model.objects.count():
        return

    admin = user_model(
        id=1,
        username='alfakiosk',
        email='alfakiosk@alfadispenser.com',
        password=make_password('alfakiosk'),
        is_superuser=True,
        is_staff=True
    )
    admin.save()
    logging.warning( '*** default superuser created !' )

