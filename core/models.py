# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import pytz, datetime

# Create your models here.



class transaction(models.Model):
    sender = models.CharField(max_length=5000,null=False) #Sender's PUBLIC KEY.
    receiver = models.CharField(max_length=5000,null=False) #Receivers's PUBLIC KEY.
    prevblockhash = models.CharField(max_length=5000,null=False)
    blockhash = models.CharField(max_length=5000,null=False)
    amount = models.IntegerField(null=False)
    nonce = models.IntegerField(null=False)
    first_timestamp = models.IntegerField(null=False)
    saved_timestamp = models.DateTimeField(auto_now_add=True)
    P2PKH = models.CharField(max_length=5000,null=False)
    verification = models.BooleanField(blank=True)
    def __str__(self):
        return("BlockHash : %s "% (self.blockhash))
