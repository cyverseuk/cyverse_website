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
        if field["value"].get("required")!=True:
            self.fields[field["id"]].required=False
        else:
            self.fields[field["id"]].label=field["details"].get("label", field["id"])+"*"
            if field["value"].get("default",None) is not None:
                self.fields[field["id"]].initial=field["value"]["default"]

    def choice_field(self,field):
        """
        give a default value if is set despite the field being required or not.
        I'll call this method after additional_feature() to override the defaut
        behaviour for a generic field.
        """
        if field["value"].get("default",None) is not None:
            self.fields[field["id"]].initial=field["value"]["default"]

    def number_field(self,field):
        """
        this is a super ugly workaround to get the AGAVE API json file and the
        django validation to work toghether, as the regex is screwing up the
        number validation treating it as string. But i Agave doesn't have a
        difference between float and integers, that i need for python validation
        """
        if field["value"].get("default",None) is not None:
            if "." in field["value"]["validator"] or "," in field["value"]["validator"]:
                self.fields[field["id"]]=forms.FloatField()
            else:
                self.fields[field["id"]]=forms.IntegerField()
        else:
            self.fields[field["id"]]=forms.FloatField()

    def choice_feature(self,choices,field):
        """
        function that define initial even if the value is not required, or add
        a default empty option if default is not set in the agave api and the
        field is not required.
        """
        if field["value"].get("required")!=True and field["value"].get("default", None) is None:
            choices.insert(0, ('', ''))
        return choices

    def widget_features(self,field):
        """
        same as above to make the widget for multiple files work accordingly.
        """
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
                print "#"*50
                print "error, the app seems to be invalid. please contact us to report the error."
                print "#"*50
            else:
                if field["value"]["type"]=="enumeration":
                    choices=[]
                    for pos in field["value"]["enum_values"]:
                        #####add a test here to check that this dictionary length is always 1
                        if len(pos.keys())!=1:
                            print "#"*50
                            print "the app seems to be in an unexpected format!"
                            print "#"*50
                        choices.append((pos.keys()[0],pos.keys()[0]))
                    choices=self.choice_feature(choices,field)
                    self.fields[field["id"]]=forms.ChoiceField(choices=choices)
                    self.additional_features(field)
                    self.choice_field(field)
                else:
                    if field["value"]["type"]=="number":
                        self.number_field(field)
                    elif field["value"]["type"]=="string":
                            self.fields[field["id"]]=forms.CharField(max_length=50)
                            if field["value"].get("validator", None) is not None:
                                my_validator=RegexValidator(regex=field["value"]["validator"], message="Enter a valid value.")
                                self.fields[field["id"]].validators=[my_validator]
                    elif field["value"]["type"]=="bool" or field["value"]["type"]=="flag":
                        self.fields[field["id"]]=forms.BooleanField()
                    self.additional_features(field)
