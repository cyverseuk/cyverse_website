from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator


@python_2_unicode_compatible
class Application(models.Model):
    name=models.CharField(max_length=200)
    version=models.CharField(max_length=200)
    author=models.CharField(max_length=200)
    description=models.CharField(max_length=200)
    more=models.TextField()
    uri=models.CharField(max_length=200)

    def __str__(self):
        return self.name()+" "+self.version()

@python_2_unicode_compatible
class Input(models.Model):
    app=models.ForeignKey(Application, on_delete=models.CASCADE, related_name="app")
    name=models.CharField(max_length=200)
    requirement=models.BooleanField(default=False)
    value=models.CharField(max_length=200)
    label=models.CharField(max_length=200)
    max_values=models.IntegerField(default=1)

    def __str__(self):
        return self.name()+ " "+self.label()

@python_2_unicode_compatible
class Parameter(models.Model):
    """
    abstract base class as base for the different types of
    parammeters.
    """
    app=models.ForeignKey(Application, on_delete=models.CASCADE)
    name=models.CharField(max_length=200) ###change this to FileField in future
    visibility=models.BooleanField(default=True)
    label=models.CharField(max_length=200)
    re_validation=models.CharField(max_length=200) ####here the validator expression from the json
    max_values=models.IntegerField(default=1)

    def __str__(self):
        return self.name()+" "+self.label()

    class Meta:
        abstract=True

class NumericalParameter(Parameter):
    """
    this class will be used for any number, including
    integers. The discrimination will work accordingly to
    the regex re_validation.
    """
    value=models.FloatField(default=0)

class BooleanParameter(Parameter):
    value=models.BooleanField(default=False)

class TextParameter(Parameter):
    value=models.CharField(max_length=200)

####eliminated ChoiceParameter as that is dealt with somewhere else?
