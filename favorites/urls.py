from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle/<str:property_id>/', views.toggle_favorite, name='toggle'),
    path('my/', views.my_favorites, name='my_favorites'),
]
