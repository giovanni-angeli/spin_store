
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class Interaction(models.Model):
    
    class Meta:
        abstract = True
    
    id = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, primary_key=True, unique=True, null=False, blank=False, editable=False)
    
class Field(models.Model):

    class Meta:
        abstract = True
    
    id = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, primary_key=True, unique=True, null=False, blank=False, editable=False)
    particle_name = models.CharField(max_length=200)
    
    creation_date = models.DateTimeField(default=timezone.now)
    deletion_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.particle_name

class Boson(Field):
    
    class Meta:
        abstract = True

class Fermion(Field):
    
    class Meta:
        abstract = True

class Lepton(Fermion):
    pass

class Quark(Fermion):
    pass

class GaugeBoson(Boson):
    pass

class ScalarBoson(Boson):
    pass

class Pipe(models.Model):
    pass

class Table(models.Model):
    pass

class Device(models.Model):

    # ~ objects = DeviceManager()

    (FAMILY_UNKNOWN,
     FAMILY_MACHINE,
     FAMILY_LABELER,
     FAMILY_SCALE,
     FAMILY_PAYMENT,
     ) = range(5)

    FAMILY_CHOICES = (
        (FAMILY_UNKNOWN, _('Unknown')),
        (FAMILY_MACHINE, _('Machine')),
        (FAMILY_LABELER, _('Labeler')),
        (FAMILY_SCALE, _('Scale')),
        (FAMILY_PAYMENT, _('Payment')),
    )

    # this list is the *single* source of information for models
    MODEL_CATALOG = [[
        ("unknown", "Unknown Device")

    ], [
        ("color_tester", "Color Tester"),
        ("color_lab", "Color Lab"),
        ("desk_tinting","Desk Tinting")
    ], [
        ("bt_ur056", "BT-UR056"),

    ], [
        ("mettler_toledo", "Mettler Toledo"),

    ], [
        ("alberici_coin_acceptor_eur", "Alberici AL5x/6x (EUR)"),
        ("alberici_coin_acceptor_mxn", "Alberici AL5x/6x (MXN)"),
    ]]

    # build choices as a reduction of MODEL_CATALOG (keep it dry)
    # ~ MODEL_CHOICES = reduce(lambda a, b: a + b, MODEL_CATALOG)
    MODEL_CHOICES = []
    for i in MODEL_CATALOG:
        MODEL_CHOICES += i    


    PORT_CHOICES = (
        ('/dev/ttyS0', 'COM1'),
        ('/dev/ttyS1', 'COM2'),
        ('/dev/ttyS2', 'COM3'),
        ('/dev/ttyS3', 'COM4'),
        ('/dev/ttyS4', 'COM5'),
        ('/dev/ttyS5', 'COM6'),
        ('/dev/ttyS6', 'COM7'),
        ('/dev/ttyS7', 'COM8'),
    )

    # TODO: rename as "channel"
    name = models.CharField(_(u'channel'), max_length=256, null=False, blank=True)
    description = models.CharField(_(u'description'), max_length=256, null=False, blank=True)
    serial_number = models.CharField(_(u'serial number'), max_length=256, null=False, blank=True)
    family = models.IntegerField(choices=FAMILY_CHOICES, default=FAMILY_UNKNOWN)
    model = models.CharField(choices=MODEL_CHOICES, default="unknown", max_length=80, )
    enabled = models.BooleanField(default=True, null=False, blank=False)
    port = models.CharField(choices=PORT_CHOICES, null=True, blank=True, max_length=40, )

    # TODO: add 'channel' as configurable device attribute
    #channel = models.CharField(null=False, blank=True, max_length=40, )

    # parameters: device dependant opaque settings
    # + getter yields a pretty printed JSON unicode representation.
    # + setter takes a valid JSON representation (either string or unicode) OR a dictionary.
    _parameters = models.TextField(_(u'parameters'), null=False, blank=True, db_column='parameters')

    def get_parameters(self):
        return self._parameters

    def set_parameters(self, value):
        import json

        # can be either a string (-> needs validation) or a dict
        if isinstance(value, basestring):
            obj = json.loads(value)
        elif isinstance(value, dict):
            obj = value
        else:
            raise TypeError('Only strings and dictionaries supported')

        self._parameters = json.dumps(obj, indent=4)
    parameters = property(get_parameters, set_parameters)

    poll_interval = models.IntegerField(null=False, default=0)

    def _is_machine(self):
        return self.family == Device.FAMILY_MACHINE
    is_machine = property(_is_machine)

    def _is_colortester(self):
        return self.model == 'color_tester'
    is_colortester = property(_is_colortester)

    def _is_colorlab(self):
        return self.model == 'color_lab'
    is_colorlab = property(_is_colorlab)

    def _is_desk(self):
        return self.model == 'desk_tinting'
    is_desk = property(_is_desk)

    def _is_scale(self):
        return self.family == Device.FAMILY_SCALE
    is_scale = property(_is_scale)

    def _is_labeler(self):
        return self.family == Device.FAMILY_LABELER
    is_labeler = property(_is_labeler)

    def _is_payment(self):
        return self.family == Device.FAMILY_PAYMENT
    is_payment = property(_is_payment)


    def get_agent(self):
        """
        Supplies the agent responsible to interact with the physical device
        """
        if self.is_machine:
            return DeviceMachineAgent(self)
        else:
            raise DeviceError(_('Unknown device family'))
    agent = property(get_agent)


    def get_default_channel(self):
        """
        Supplies a suitable default value for 'channel' attribute
        """
        from alfakiosk.queues import queue
        if self.is_machine:
            return queue.CHANNEL_MACHINE
        elif self.is_scale:
            return queue.CHANNEL_SCALE
        elif self.is_labeler:
            return queue.CHANNEL_LABELER
        elif self.is_payment:
            return queue.CHANNEL_LABELER

        raise DeviceError(_('Unknown device family'))

    def get_channel(self):
        """
        The channel to be used to communicatie with the physical device.

        TODO: should be a specific property for the device;
        for now, we simply infer it from device family
        """
        return self.get_default_channel()
    channel = property(get_channel)


    def __str__(self):
        return self.name if len(self.name) > 0 else "%s / %s" % (self.get_family_display(), self.get_model_display())

