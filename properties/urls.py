from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.find_rooms, name='find_rooms'),
    path('add/new/', views.add_property, name='add_property'),
    path('<str:property_id>/', views.property_detail, name='property_detail'),
    path('<str:property_id>/edit/', views.edit_property, name='edit_property'),
    path('<str:property_id>/delete/', views.delete_property, name='delete_property'),
    path('<str:property_id>/toggle-availability/', views.toggle_availability, name='toggle_availability'),
]
