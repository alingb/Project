"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mydb.views import *
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'addmsg/', getChainMsg, name="getChainMsg"),
    url(r'transfer/', getTransferMsg, name="getChainMsg"),
    url(r'blockheight/request/', blockHeightList, name="blockHeightList"),
    url(r'transactionlist/request/', transactionList, name="transactionList"),
    url(r'homepage/request/', homepageData, name="homepageData"),
    url(r'address/request/', addressMsg, name="addressMsg"),
    url(r'transactionlistpage/request/', transactionListPage, name="transactionListPage"),
    url(r'detailsearch/request/', detailSearch, name="detailSearch"),
    url(r'blockdetail/request/', blockDetail, name="blockDetail"),
    url(r'transactiondetail/request/', transactionDetail, name="transactionDetail"),
]
