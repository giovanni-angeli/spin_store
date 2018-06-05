
import logging
import json

from django.utils.safestring import mark_safe
from django.contrib import admin

from orm.models import GaugeBoson, ScalarBoson, Lepton, Quark
from orm.jsonschemas import validate

from spin_store.settings import ugettext_lazy as _

class BaseModelAdmin(admin.ModelAdmin):
    
    list_display = ('ui_name', 'creation_date', 'deletion_date', 'parameters', 'tenant_id')
    readonly_fields = ('id', 'tenant_id', 'parameters', )
    
    fieldsets = (
        # ~ ('Main section', {'fields': (('ui_name', 'id'), 'creation_date', 'deletion_date')}),
        ('Main section', {'fields': (('ui_name', 'id'), 'tenant_id')}),
    )

    # these templates will be {implicit-django-shit} used by super().change_view and super().add_view:
    change_form_template = 'BaseModelAdmin_change_form.html'
    add_form_template = 'BaseModelAdmin_change_form.html'

    def save_model(self, request, obj, form, change):

        _schema = self._get_parameters_jsonschema()
        params_content = request.POST.get('params_content', "{}")
        _params = json.loads(params_content)
        logging.warning("save_model() obj:{}, _params({}):{}, _schema:{}".format(obj, type(_params), _params, _schema))

        validate(params_content, _schema)

        obj.set_parameters(_params)

        return super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        _schema = self._get_parameters_jsonschema()

        if object_id is not None and self._get_object(object_id):
            _parameters = self._get_object(object_id).get_parameters()
        else:
            _parameters = _schema.get('defaults', {})
            
        _schema     = json.dumps(_schema)
        _parameters = json.dumps(_parameters)
        if extra_context is None:
            extra_context = {}
        extra_context.update({
            'jsonschema': mark_safe(_schema),
            'params': mark_safe(_parameters),
            'editor_section_title': _(self.__class__.__name__)
        })
        logging.warning("changeform_view() extra_context:{}".format(extra_context))

        return super().changeform_view(request, object_id, form_url, extra_context)

    def _get_object(self, object_id): # virtual protected
        raise NotImplementedError
        
    def _get_parameters_jsonschema(self, object_id): # virtual protected
        raise NotImplementedError


@admin.register(GaugeBoson)
class GaugeBosonAdmin(BaseModelAdmin):
    def _get_object(self, object_id):
        return GaugeBoson.objects.get(id=object_id)
    def _get_parameters_jsonschema(self):
        return GaugeBoson.get_parameters_jsonschema()

@admin.register(ScalarBoson)
class ScalarBosonAdmin(BaseModelAdmin):
    def _get_object(self, object_id):
        return ScalarBoson.objects.get(id=object_id)
    def _get_parameters_jsonschema(self):
        return ScalarBoson.get_parameters_jsonschema()

@admin.register(Lepton)
class LeptonAdmin(BaseModelAdmin):
    def _get_object(self, object_id):
        return Lepton.objects.get(id=object_id)
    def _get_parameters_jsonschema(self):
        return Lepton.get_parameters_jsonschema()
        
@admin.register(Quark)
class QuarkAdmin(BaseModelAdmin):
    def _get_object(self, object_id):
        return Quark.objects.get(id=object_id)
    def _get_parameters_jsonschema(self):
        return Quark.get_parameters_jsonschema()

