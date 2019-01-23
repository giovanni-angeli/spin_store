
import logging
import json

from django.utils.safestring import mark_safe
from django.contrib import admin

from orm.models import GaugeBoson, ScalarBoson, Lepton, Quark
from orm.jsonschemas import validate

from spin_store.settings import ugettext_lazy as _

from django import forms

class ParamsForm(object):

    def __init__(self, schema_properties, defaults=None):

        self.schema_properties = schema_properties
        self.defaults = defaults

    def handle_input(self, form):
        _params = {}
        for k, v in form.data.items():
            if k.startswith('_params_'):
                
                key = "_".join(k.split('_')[2:])

                self.schema_properties[key]

                try:
                    _params[key] = json.loads(v)
                except:
                    _params[key] = v
        return _params
        
    def render(self):
        html_head = """
        <div class="form-row field-params">
        """ 

        html_foot = """
        </div>
        """

        html_body = ""
        for k, v in self.schema_properties.items():
            val = self.defaults.get(k)
            html_body += """
            <div class="fieldBox field-{key}">
                <label class="required" for="id_{key}">{key} {type}:</label>
                <input type="text" name="_params_{key}" value={val} class="TextField" maxlength="200" required id="id_{key}"></input>
            </div>
            """.format(key=k, val=json.dumps(val), type=v.get('type'))

        html_ = html_head + html_body + html_foot
        return mark_safe(html_)

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

        properties = _schema.get('properties', {})
        params_form = ParamsForm(properties)
        _params = params_form.handle_input(form)

        logging.warning("save_model() request:{}, obj:{}, change:{}, form.data:{}, _params:{}".format(request, obj, change, form.data, _params))

        validate(_params, _schema)
        obj.set_parameters(_params)

        return super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        _schema = self._get_parameters_jsonschema()

        if object_id is not None and self._get_object(object_id):
            defaults = self._get_object(object_id).get_parameters()
        else:
            defaults = _schema.get('defaults', {})

        properties = _schema.get('properties', {})
        params_form = ParamsForm(properties, defaults)

        logging.warning("changeform_view() properties:{}, defaults:{}".format(properties, defaults))

        if extra_context is None:
            extra_context = {}
        extra_context.update({
            'params_form_html': params_form.render(),
            'editor_section_title': _(self.__class__.__name__)
        })
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

