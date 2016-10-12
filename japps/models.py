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

class Input(models.Model):
    app=models.ForeignKey(Application, on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    requirement=models.BooleanField(default=False)
    value=models.CharField(max_length=200)
    label=models.CharField(max_length=200)
    max_values=models.IntegerField(default=1)

    def __str__(self):
        return self.name()+ " "+self.label()

class Parameter(models.Model):
    app=models.ForeignKey(Application, on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    visibility=models.BooleanField(default=True)
    label=models.CharField(max_length=200)
    re_validation=models.CharField(max_length=200) ####here the validator expression from the json
    value="" ######i think this depends on type_accepted and the validator, i should make a check function somewhere(not sure where is the appropriate place)
    max_values=models.IntegerField(default=1)

    def __str__(self):
        return self.name()+" "+self.label()
