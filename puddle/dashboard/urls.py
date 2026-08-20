from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('buyer/', views.buyer_dashboard, name='buyer'),
    path('admin-panel/', views.admin_dashboard, name='admin'),
    path('orders/', views.orders, name='orders'),
    path('orders/<uuid:order_number>/update/', views.update_order_status, name='update_order_status'),
]