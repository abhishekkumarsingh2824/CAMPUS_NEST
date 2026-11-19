from django.urls import path
from . import views

app_name = 'inquiries'

urlpatterns = [
    path('send/<str:property_id>/', views.send_inquiry, name='send_inquiry'),
    path('my/', views.my_inquiries, name='my_inquiries'),
    path('manage/', views.owner_inquiries, name='owner_inquiries'),
    path('update/<str:inquiry_id>/', views.update_inquiry_status, name='update_status'),
]
