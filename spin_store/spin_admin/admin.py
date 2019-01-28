
import logging
import traceback
import json

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib import messages

from django import forms

from orm.models import GaugeBoson, ScalarBoson, Lepton, Quark, Command
from orm.jsonschemas import QUANTUMFIELD_JSONSCHEMAS, COMMAND_JSONSCHEMAS, validate

from spin_store.settings import ugettext_lazy as _


class ParamsHtmlForm(object):

    def __init__(self, schema_container, schema_name, defaults=None):

        self.schema_container = schema_container
        self.schema_name = schema_name
        self.defaults = defaults

        logging.warning("schema_name:{}, defaults:{}".format(schema_name, defaults))

    def handle_input(self, form):

        _params = {}

        logging.warning("form.data.items():{}.".format([(k, v) for k, v in form.data.items()]))
        logging.warning("self.schema_name:{}.".format(self.schema_name))

        parameters_schema_name = form.data.get('parameters_schema_name')
        if self.schema_name != parameters_schema_name:
            self.schema_name = parameters_schema_name
            _schema = self.schema_container.get(self.schema_name, {}).get('jsonschema', {})
            _params = _schema.get('defaults', {})

        else:

            _schema = self.schema_container.get(self.schema_name, {}).get('jsonschema', {})
            properties = _schema.get('properties', {})

            for k, v in form.data.items():
                if k.startswith('params::'):
                    key = k.split('::')[1]
                    # ~ logging.warning("v({}):{}, properties[{}]:{}.".format(type(v), v, key, properties[key]))
                    if properties[key].get('type', 'string') == 'string':
                        _params[key] = v  
                    else:
                        _params[key] = json.loads(v)
                    # ~ logging.warning("_params[{}]({}):{}.".format(key, type(_params[key]), _params[key]))
            validate(_params, _schema)

        return parameters_schema_name, _params

    def _render_select(self, k, v, choices, descr, req):

        html_ = """
                <td><label class="col-sm-2 col-form-label {req}" for="id_{key}">{key}:</label></td>
                
                <td><select name="params::{key}" class="custom-select form-control" {req} id="id_{key}">
              """.format(key=k, req=req)

        for i, c in choices:
            sel = ''
            if i == v:
                sel = ' selected'
            html_ += """ 
                    <option value="{}"{}>{}</option>
            """.format(i, sel, c)

        html_ += """
                </select></td>
                <td><label class="col-sm-1 col-form-label">{description}</label></td>
        """.format(description=descr)
        return html_

    def _render_item(self, k, v, type, descr, req):

        type_map = {
            'string': 'TextField',
            'number': 'TextField',
            'array': 'TextArea',
            'object': 'TextArea',
        }

        html_ = """
        <td><label class="col-form-label {req}" for="id_{key}">{key} ({type}):</label></td>
        <td><input type="{mapped_type}" name="params::{key}" value='{val}' class="form-control" maxlength="10000" {req} id="id_{key}"></input></td>
        <td><label class="col-form-label">{description}</label></td>
        """.format(key=k, val=v, type=type, description=descr, req=req, mapped_type=type_map.get(type, 'TextField'))
        return html_

    def _render_schema(self, wide=True):

        if wide:
            html_ = """
            <tr bgcolor="#FFEEEE" width="100%">                                                                                  
                <td><label class="col-sm-2 col-form-label required" for="id_param_schema_name">{}:</label><p>{}</p></td>
                <td colspan="2"><select name="parameters_schema_name" class="custom-select form-control" required id="id_param_schema_name">
            """.format(_("jsonschema name"), _("ATTENTION: when you change the name of the scheme, all the fields are reset to the original values."))
        else:
            html_ = """<select name="parameters_schema_name" class="custom-select form-control" required id="id_param_schema_name">
            """.format(_("jsonschema name"))

        for i in self.schema_container:
            sel = ''
            if i == self.schema_name:
                sel = ' selected'
            html_ += """
                <option value="{i}"{sel}>{i}</option>""".format(i=i, sel=sel)

        html_ += """</select>"""
        
        if wide:
            html_ += """</td></tr>"""
        
        return html_

    def render(self):
        html_head = """
        <div class="alert alert-success" role="alert">
          <h4 class="alert-heading">Parameters</h4>
        </div>
        <table bgcolor="#FFFFEE" width="100%">
        <thead><tr><th>{}</th><th>{}</th><th>{}</th></tr></thead>
        <tbody>
        """.format(_("name"), _("value"), _("description"), )

        html_foot = """
        </tbody>
        </table>"""

        html_body = ""

        _schema = self.schema_container.get(self.schema_name, {}).get('jsonschema', {})
        properties = _schema.get('properties', {})
        required = _schema.get('required', {})

        if self.defaults is None:
            self.defaults = _schema.get('defaults', {})

        for k, v in properties.items():
            val_ = self.defaults.get(k)
            val_ = val_ if isinstance(val_, str) else json.dumps(val_)
            req_ = 'required' if k in required else ''

            if v.get('enum'):
                choices = [(i, i) for i in v.get('enum')]
                html_item = self._render_select(k, val_, choices, v.get('description', ''), req_)
            elif v.get('type') == 'boolean':
                choices = (('true', 'true'), ('false', 'false'))
                html_item = self._render_select(k, val_, choices, v.get('description', ''), req_)
            else:
                html_item = self._render_item(k, val_, v.get('type'), v.get('description', ''), req_)

            html_body += """<tr class="form-group row"> {}</tr>""".format(html_item)

        html_body += self._render_schema()

        html_ = html_head + html_body + html_foot

        return mark_safe(html_)




class BaseModelAdmin(admin.ModelAdmin):
    
    schema_container = QUANTUMFIELD_JSONSCHEMAS

    list_display = ('ui_name', 'creation_date', 'deletion_date', 'parameters', 'tenant_id', '_render_parameters_schema_name')
    readonly_fields = ('id', 'tenant_id', 'parameters', )

    fieldsets = (
        # ~ ('Main section', {'fields': (('ui_name', 'id'), 'creation_date', 'deletion_date')}),
        ('Main section', {'fields': (('ui_name', 'id'), 'tenant_id')}),
    )

    # these templates will be {implicit-django-shit} used by super().change_view and super().add_view:
    change_form_template = 'BaseModelAdmin_change_form.html'
    add_form_template = 'BaseModelAdmin_change_form.html'
    
    # ~ change_list_template = 'BaseModelAdmin_change_list.html'
    
    def _render_parameters_schema_name(self, obj):
        params_form = ParamsHtmlForm(self.schema_container, obj.parameters_schema_name)
        html_ = """
        """
        html_ += """<form method="post" action="/admin/orm/scalarboson/{}/change/" id="change_schema_name_inline">
        """.format(obj.id)
        # ~ html_ += """<form id="changelist-form" method="post" novalidate>"""
        # ~ html_ += """<input type="hidden" name="csrfmiddlewaretoken" value="XB5XHnlEHy3uvZKLqm296ahFsA5fb9YTPXVASyPuXUfywBC1OSQY21C2SCz1BSlO">"""
        html_ += """{}
        """.format(params_form._render_schema(wide=False))
        html_ += """<input type="submit" name="submit" value="submit"></input>
        """
        html_ += """</form>
        """
        return mark_safe(html_)

    def save_model(self, request, obj, form, change):

        logging.warning("request:{}, obj:{}".format(request, obj))

        params_form = ParamsHtmlForm(self.schema_container, obj.parameters_schema_name)
        parameters_schema_name, _params = params_form.handle_input(form)

        if parameters_schema_name != obj.parameters_schema_name:
            obj.parameters_schema_name = parameters_schema_name

        obj.set_parameters(_params)

        return super().save_model(request, obj, form, change)

    def change_view(self, request, object_id, form_url='', extra_context=None):

        logging.warning("request:{}, object_id:{}".format(request, object_id))

        try:
            return super(BaseModelAdmin, self).change_view(request, object_id, form_url, extra_context)
        except Exception as e:
            messages.error(request, e)
            logging.error(traceback.format_exc())
            return HttpResponseRedirect(request.path)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        logging.warning("request:{}, object_id:{}, form_url:{}, extra_context:{}".format(request, object_id, form_url, extra_context))
        try:
            if object_id is not None and self._get_object(object_id):
                obj = self._get_object(object_id)
                defaults = obj.get_parameters()
                _schema_name = obj.parameters_schema_name
            else:
                _schema_name = "Generic"
                defaults = None
                
            params_form = ParamsHtmlForm(self.schema_container, _schema_name, defaults)

            if extra_context is None:
                extra_context = {}
            extra_context.update({
                'params_form_html': params_form.render(),
                'editor_section_title': _(self.__class__.__name__)
            })
        except:
            logging.error(traceback.format_exc())
        return super().changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, *args, **kwargs):

        resp = super().changelist_view(*args, **kwargs)
        
        # ~ logging.warning("args:{}, kwargs:{} resp.context_data['cl']:{}.".format(args, kwargs, resp.context_data['cl']))
        logging.warning("dir(resp.context_data['cl']):{}.".format(dir(resp.context_data['cl'])))

        return resp



    def _get_object(self, object_id):
        return self.Meta.model.objects.get(id=object_id)

@admin.register(GaugeBoson)
class GaugeBosonAdmin(BaseModelAdmin):

    class Meta:
        model = GaugeBoson


@admin.register(ScalarBoson)
class ScalarBosonAdmin(BaseModelAdmin):

    class Meta:
        model = ScalarBoson


@admin.register(Lepton)
class LeptonAdmin(BaseModelAdmin):

    class Meta:
        model = Lepton


@admin.register(Quark)
class QuarkAdmin(BaseModelAdmin):

    class Meta:
        model = Quark

@admin.register(Command)
class CommandAdmin(BaseModelAdmin):

    class Meta:
        model = Command

    schema_container = COMMAND_JSONSCHEMAS
    for k, v in schema_container.items():
        v['jsonschema'] = v.get('in_params', {}).get('jsonschema', {})
    # ~ def _get_object(self, object_id):
        # ~ return Command.objects.get(id=object_id)

