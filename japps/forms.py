from django import forms
from parsley.decorators import parsleyfy


@parsleyfy
class ParameterForm(forms.Form):

    def __init__(self, *args, **kwargs) :
        super(ParameterForm,self).__init__(*args,**kwargs)

class ContactForm(forms.Form):
    name=forms.CharField()
    email=forms.EmailField()
    subject=forms.CharField()
    support_request=forms.CharField(widget=forms.Textarea)
