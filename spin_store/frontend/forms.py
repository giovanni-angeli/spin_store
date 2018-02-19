import logging
import datetime 

from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
    
class ExampleForm(forms.Form):
    
    pid = forms.IntegerField()
    name = forms.CharField(label='name', max_length=100, help_text="Enter a name.")

    # ~ def __init__(self, initial={}):
        # ~ super(ExampleForm, self).__init__(initial=initial)
        
    def is_valid(self):
        
        ret = super(ExampleForm, self).is_valid()

        logging.warning("is_valid() ret:{}".format(ret))
        logging.warning("is_valid() self.data:{}".format(self.data))
        # ~ logging.warning("is_valid() self.cleaned_data:{}".format(self.cleaned_data))

        example_date = self.cleaned_data.get('example_date')
        if example_date:
            #Check date is not in past. 
            if example_date < datetime.date.today():
                raise ValidationError(_('Invalid example date in past'))

            #Check date is in range librarian allowed to change (+4 weeks).
            if example_date > datetime.date.today() + datetime.timedelta(weeks=4):
                raise ValidationError(_('Invalid example date: more than 4 weeks ahead'))
        else:
            pass
            # ~ raise ValidationError(_('Invalid example date format'))
            
        return ret
        
