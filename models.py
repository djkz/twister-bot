import re

from django.db import models


class Define(models.Model):
    tag = models.SlugField(blank=True, null=True)
    text = models.TextField()
    
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=30)

    locked = models.BooleanField(default=False)
    locked_by = models.CharField(max_length=30,null=True,blank=True)
    
    index = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'%s[%i]: %s' % (self.tag,self.index, self.text)
        
class Quote(models.Model):
    text = models.TextField()
    
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=30)
    
    index = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'[%i]: %s' % (self.index, self.text)