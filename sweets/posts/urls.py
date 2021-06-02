from django.urls import include, path
from rest_framework import routers
from . import views
from .serializer import *

# router = routers.DefaultRouter()
# router.register('', views.CouriersView)


urlpatterns = [
    # path('', include(router.urls)),
    path('couriers', views.couriers_list),
    path('orders', views.order_list),
    path('couriers/<int:pk>', views.change),
    path('orders/complete', views.complete),
    path('orders/assign', views.assign),
    # path('orders/$<int:pk>', views.assign),
    # path('couriers', views.CourierView)
]
