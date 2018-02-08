from django.contrib import admin

# Register your models here.

from django.contrib import admin
from orm.models import Lepton
from orm.models import Quark

admin.site.register(Lepton)
admin.site.register(Quark)
