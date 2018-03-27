# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task



@shared_task
def givereward():
    from cloudbank.utils import checkreward
    print("im here bro")
    return checkreward()
