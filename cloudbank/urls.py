#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
import cloudbank.views, cloudbank.apilist

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', cloudbank.views.landing),
    url(r'^login', cloudbank.views.login),
    url(r'^logout', cloudbank.views.logout),
    url(r'^transactions', cloudbank.views.ws),


    #REST API
    url(r'^api/v1/checkwallet/', cloudbank.views.checkwallet),
    url(r'^api/v1/sendcloudcoin', cloudbank.views.sendcloudcoin),
    url(r'^api/v1/createnewwallet/', cloudbank.views.createnewwallet),
    url(r'^api/v1/alltransactions/', cloudbank.apilist.alltransactions),
    url(r'^api/v1/gettransaction/(?P<tid>\w+)/$', cloudbank.apilist.gettransaction,  name='gettransaction'),
    url(r'^api/v1/getwalletfrompkey/(?P<pkey>\w+)/$', cloudbank.apilist.getwalletfrompkey, name='getwalletfrompkey'),
    url(r'^api/v1/getpublickeyfromprikey/(?P<private_key>\w+)/$', cloudbank.apilist.getpublickeyfromprikey, name='getpublickeyfromprikey'),
    url(r'^api/v1/getbalancefromwallet/(?P<wallet>\w+)/$', cloudbank.apilist.getbalancefromwallet, name='getbalancefromwallet'),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
