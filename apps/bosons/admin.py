from django.contrib import admin

# Register your models here.

from django.contrib import admin
from orm.models import GaugeBoson
from orm.models import ScalarBoson

admin.site.register(GaugeBoson)
admin.site.register(ScalarBoson)
