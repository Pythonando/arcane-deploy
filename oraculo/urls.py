from django.urls import path
from . import views

urlpatterns = [
    path('treinar_ia/', views.treinar_ia, name='treinar_ia'),
    path('chat/', views.chat, name='chat'),
    path('stream_response/', views.stream_response, name='stream_response'),
    path('ver_fontes/<int:id>', views.ver_fontes, name='ver_fontes'),
    path('webhook_whatsapp/', views.webhook_whatsapp, name='webhook_whatsapp')
]
