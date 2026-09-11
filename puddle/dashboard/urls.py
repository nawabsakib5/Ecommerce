from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('buyer/', views.buyer_dashboard, name='buyer'),
    path('admin-panel/', views.admin_dashboard, name='admin'),
    path('orders/', views.orders, name='orders'),
    path('orders/<uuid:order_number>/update/', views.update_order_status, name='update_order_status'),

    # ✅ User Management Actions — POST only, admin only
    path('users/<int:user_id>/freeze/', views.freeze_user, name='freeze_user'),
    path('users/<int:user_id>/unfreeze/', views.unfreeze_user, name='unfreeze_user'),
    path('users/<int:user_id>/spam/', views.mark_spam_user, name='mark_spam_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]