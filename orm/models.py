
import logging
import traceback
import uuid
import json
import datetime

from django.db import models
from django.utils import timezone

from spin_store.settings import ugettext_lazy as _


class BaseModel(models.Model):

    class Meta:
        abstract = True
    
    id = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, primary_key=True, unique=True, null=False, blank=False, editable=False)
    ui_name = models.CharField(verbose_name=_('name'), max_length=200)
    tenant_id = models.UUIDField(verbose_name=_('tenant\'s uuid'), null=True, blank=True, editable=False)
    _parameters = models.TextField(_('parameters'), null=False, blank=True, db_column='parameters', default="{}")
    parameters_schema_name = models.CharField(verbose_name=_('jsonschema name'), max_length=200, default='Generic')
    
    creation_date = models.DateTimeField(default=timezone.now)
    deletion_date = models.DateTimeField(default=timezone.now() + datetime.timedelta(days=365*10+2))

    def __str__(self):
        return self.ui_name

    def get_parameters(self):
        _parameters = json.loads(self._parameters)
        return _parameters
    
    def set_parameters(self, params):
        if isinstance(params, str):
            params = json.loads(params)
        assert isinstance(params, dict)
        self._parameters = json.dumps(params, indent=4)
        
    parameters = property(get_parameters, set_parameters)
 
    
class Boson(BaseModel):
    
    class Meta:
        abstract = True

class Fermion(BaseModel):
    
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

    pass


class Command(BaseModel):

    pass
