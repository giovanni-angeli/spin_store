
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

