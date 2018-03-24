# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task



@shared_task
def givereward(x, y):
    from cloudbank.utils import checkreward
    print("im here bro")
    return checkreward()

@shared_task
def add(x, y):
    print("im here bro")
    return x + y
