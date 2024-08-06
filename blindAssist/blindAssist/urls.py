from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blindapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('blindapp.urls')),
]


if settings.DEBUG:  # This is only for development; remove or adjust for production
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
