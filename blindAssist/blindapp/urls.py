from django.urls import path
from .views import home, upload_image,get_speech_text

urlpatterns = [
    path("",home,name='home'),

    path('get_speech_text/', get_speech_text, name='get_speech_text'),

    path('upload_image/', upload_image, name='upload_image'),
]
