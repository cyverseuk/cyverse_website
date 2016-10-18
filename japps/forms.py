from django import forms
from parsley.decorators import parsleyfy


@parsleyfy
class ParameterForm(forms.Form):

    def __init__(self, *args, **kwargs) :
        super(ParameterForm,self).__init__(*args,**kwargs)
