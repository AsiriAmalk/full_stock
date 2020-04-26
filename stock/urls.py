from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('all_stock', views.all_stock, name="all_stock"),
    path('open_browser', views.open_browser, name="open_browser")
]