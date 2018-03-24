# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from cloudbank.utils import checkreward


@shared_task
def givereward(x, y):
    print("im here bro")
    return checkreward()
