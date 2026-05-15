import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order
from item.models import Item 

def sslcommerz_payment(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user
    
    # পেমেন্টের ক্রেডেনশিয়ালস (settings.py থেকে আসছে)
    store_id = settings.SSLC_STORE_ID
    store_pass = settings.SSLC_STORE_PASS
    mypayment_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

    # ট্রানজ্যাকশন আইডি তৈরি করা
    tran_id = str(uuid.uuid4())[:10]

    # ডাটাবেসে নতুন অর্ডার অবজেক্ট তৈরি করা
    order = Order.objects.create(
        user=user,
        amount=item.price, 
        transaction_id=tran_id,
    )
    order.items.add(item)
    order.save()

    # SSLCommerz এ পাঠানোর জন্য ডাটা পে-লোড
    post_data = {
        'store_id': store_id,
        'store_passwd': store_pass,
        'total_amount': item.price,
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': "http://127.0.0.1:8000/payment/success/",
        'fail_url': "http://127.0.0.1:8000/payment/fail/",
        'cancel_url': "http://127.0.0.1:8000/payment/cancel/",
        'emi_option': 0,
        'cus_name': user.username,
        'cus_email': user.email if user.email else "test@test.com",
        'cus_phone': '01700000000',
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'multi_card_name': 'mastercard,visacard,amexcard',
        'product_name': item.name,
        'product_category': 'General',
        'product_profile': 'general',
    }

    response = requests.post(mypayment_url, data=post_data)
    response_data = response.json()

    if response_data.get('status') == 'SUCCESS':
        return redirect(response_data['GatewayPageURL'])
    
    return redirect('core:index')

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')
        val_id = payment_data.get('val_id') 
        
        try:
            
            order = Order.objects.get(transaction_id=tran_id)
            
            
            order.payment_status = True
            order.val_id = val_id
            order.status = 'Processing' 
            order.save()
            
            return render(request, 'payment/success.html')
            
        except Order.DoesNotExist:
            
            return redirect('core:index') 

    return redirect('core:index')

@csrf_exempt
def payment_fail(request):
    
    return render(request, 'payment/fail.html')

@csrf_exempt
def payment_cancel(request):
    
    return render(request, 'payment/cancel.html')