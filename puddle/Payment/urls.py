from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('initiate/<int:item_id>/', views.initiate_payment, name='initiate'),
    path('success/<str:tran_id>/<int:item_id>/', views.payment_success, name='success'),
    path('fail/', views.payment_fail, name='fail'),    
    path('cancel/', views.payment_cancel, name='cancel'),
]