from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Checkout
    path('checkout/<int:item_pk>/', views.checkout, name='checkout'),
    path('initiate/<int:item_pk>/', views.initiate_payment, name='initiate'),

    # SSLCommerz
    path('sslcommerz/init/<uuid:transaction_id>/', views.sslcommerz_init, name='sslcommerz_init'),
    path('sslcommerz/success/<uuid:transaction_id>/', views.sslcommerz_success, name='sslcommerz_success'),
    path('sslcommerz/fail/<uuid:transaction_id>/', views.sslcommerz_fail, name='sslcommerz_fail'),
    path('sslcommerz/cancel/<uuid:transaction_id>/', views.sslcommerz_cancel, name='sslcommerz_cancel'),
    path('sslcommerz/ipn/', views.sslcommerz_ipn, name='sslcommerz_ipn'),

    # Mobile Banking
    path('mobile/<uuid:transaction_id>/', views.mobile_banking, name='mobile_banking'),

    # COD
    path('cod/<uuid:transaction_id>/', views.cod_confirm, name='cod_confirm'),

    # Status pages
    path('success/<uuid:transaction_id>/', views.success, name='success'),
    path('failed/<uuid:transaction_id>/', views.failed, name='failed'),
    path('pending/<uuid:transaction_id>/', views.pending, name='pending'),

    # Saved methods
    path('method/save/', views.save_payment_method, name='save_method'),
    path('method/delete/<int:pk>/', views.delete_payment_method, name='delete_method'),

    # STEADFAST
    path('track/<uuid:order_number>/', views.track_order, name='track'),

    # Coupon
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
]