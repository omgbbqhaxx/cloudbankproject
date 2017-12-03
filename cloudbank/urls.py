#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
import cloudbank.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', cloudbank.views.landing),
    url(r'^transactions', cloudbank.views.ws),
    url(r'^login', cloudbank.views.login),
    url(r'^logout', cloudbank.views.logout),
    url(r'^sendcloudcoin', cloudbank.views.sendcloudcoin),
    url(r'^createnewwallet/', cloudbank.views.createnewwallet),
    url(r'^checkwallet/', cloudbank.views.checkwallet),
    url(r'^alltransactions/', cloudbank.views.alltransactions),
    url(r'^gettransaction/(?P<tid>\w+)/$', cloudbank.views.gettransaction)


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
