from django.urls import include, path
from rest_framework import routers
# from . import views


# router = routers.DefaultRouter()
# router.register('', views.CouriersView)
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('', include(router.urls)),
    path('signin', signin, name='signin'),
    path('signup', signup, name='signup'),
    path('', start, name='start'),
    # path('create',country_page ),
    path('home', home, name='home'),
    path('work', work, name='work'),
    path('edit', edit, name='edit'),
    path('contacts', contacts),
    path('add_order', add_order),
    # path('orders/$<int:pk>', views.assign),
    # path('couriers', views.CourierView)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
