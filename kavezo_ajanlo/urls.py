from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('kavezok.urls', 'kavezok'), namespace='kavezok')),

    path('accounts/', include('django.contrib.auth.urls')),
]