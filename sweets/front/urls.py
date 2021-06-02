from django.urls import include, path
from rest_framework import routers
# from . import views


# router = routers.DefaultRouter()
# router.register('', views.CouriersView)
from .views import signin,signup

urlpatterns = [
    # path('', include(router.urls)),
    path('signin', signin),
    path('signup', signup),
    # path('orders/$<int:pk>', views.assign),
    # path('couriers', views.CourierView)
]
