from collections import OrderedDict

from django import forms
from parsley.decorators import parsleyfy
from django.core.validators import RegexValidator

@parsleyfy
class ParameterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ParameterForm, self).__init__(*args, **kwargs)

class AppForm(forms.Form):

    def additional_features(self,field):
        """
        this function helps to create a form with the rigth attributes specified in
        the app. Will be called by create_form() to add properties to the form
        fields.
        """
        self.fields[field["id"]].label=field["details"].get("label", field["id"])
        self.fields[field["id"]].help_text=field["details"].get("description", "")
        if field["value"].get("default",None) is not None:
            self.fields[field["id"]].initial=field["value"]["default"]
        if field["value"].get("validator", None) is not None:
            my_validator=RegexValidator(regex=field["value"]["validator"], message="Enter a valid value.")
            self.fields[field["id"]].validators=[my_validator]
        if field["value"].get("required")!=True:
            self.fields[field["id"]].required=False
        else:
            self.fields[field["id"]].label=field["details"].get("label", field["id"])+"*"

    def widget_features(self,field):
        """
        same as above to make the widget for multiple files work accordingly.
        """
        #global fields
        attributes={'multiple': True}
        if field["value"].get("required")==True:
            attributes['required']=True
        return attributes

    def __init__(self, *args, **kwargs):
        ex_json=kwargs.pop("ex_json")
        token=kwargs.pop("token")
        job_time=kwargs.pop("job_time")
        super(AppForm, self).__init__(*args, **kwargs)
        self.fields["user_token"]=forms.CharField(initial=token)
        self.fields["name_job"]=forms.CharField(initial=ex_json["result"]["name"]+"-"+job_time)
        self.fields["email"]=forms.EmailField(required=False, help_text="insert if you wish yo receive notifications about the job")
        for field in ex_json["result"]["inputs"]:
            #####
            #ideally here i want to have mutually exclusive options for the user to give URL for the file or to upload the file. additional problem with the url option is that apparently the widget doens't have an option to allows multiple entries.
            #####
            if field.get("semantics")!=None:
                if field["semantics"].get("maxCardinality")>1 or field["semantics"].get("maxCardinality")==-1:
                    attributes=self.widget_features(field)
                    self.fields[field["id"]]=forms.FileField(widget=forms.ClearableFileInput(attrs=attributes))
                    #self.fields[field["id"]]=forms.URLField()
                else:
                    self.fields[field["id"]]=forms.FileField()
                    #self.fields[field["id"]]=forms.URLField()
            else:
                self.fields[field["id"]]=forms.FileField()
                #self.fields[field["id"]]=forms.URLField()
            self.additional_features(field)
        for field in ex_json["result"]["parameters"]:
            if field["value"].get("type")==None:
                #should never be here as this check is done by agave, add a test
                return "error, the app seems to be invalid. please contact us to report the error."
            else:
                if field["value"]["type"]=="string":
                    self.fields[field["id"]]=forms.CharField(max_length=50)
                elif field["value"]["type"]=="number":
                    self.fields[field["id"]]=forms.FloatField()
                elif field["value"]["type"]=="bool" or field["value"]["type"]=="flag":
                    self.fields[field["id"]]=forms.BooleanField()
                elif field["value"]["type"]=="enumeration":
                    choices=[]
                    for pos in field["value"]["enum_values"]:
                        #####add a test here to check that this dictionary length is always 1
                        choices.append((pos.keys()[0],pos.keys()[0]))
                    self.fields[field["id"]]=forms.ChoiceField(choices=choices)
            self.additional_features(field)
