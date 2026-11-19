from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/approve/<str:property_id>/', views.admin_approve_property, name='admin_approve_property'),
    path('admin-panel/reject/<str:property_id>/', views.admin_reject_property, name='admin_reject_property'),
    path('admin-panel/delete-user/<str:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]
