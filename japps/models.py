from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


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
