
import logging
import datetime

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError

from .forms import ExampleForm


def main(request):

    logging.warning("main() request:{}".format(request))

    import random
    processes = [
        {
            'pid': random.randint(1000, 50000),
            'name': "one",
            'cpu_p': 50,
            'mem_MB': 120,
            'mem_p': 340,
            'uptime': 20,
        },
        {
            'pid': random.randint(1000, 50000),
            'name': "two",
            'cpu_p': 60,
            'mem_MB': 130,
            'mem_p': 350,
            'uptime': 20,
        },
    ]
    if request.method == 'POST':
        rp_copy = request.POST.copy()
        rp_copy.pop('csrfmiddlewaretoken')
        logging.warning("main() rp_copy:{}".format(request.POST))
        ui_msgs = {
            'alert': "successfully handled request.POST:{}.".format(rp_copy), 
            'danger': 'ooooops...'
        }
    else:
        ui_msgs = {
            'alert': "let's start...", 
            'danger': ''
        }
    
    return render(request, 'main.html', {'processes': processes, 'ui_msgs': ui_msgs})

