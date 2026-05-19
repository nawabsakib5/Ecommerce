import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Order
from item.models import Item

# পাইথন ৩.১৪+ এর জন্য শতভাগ ক্র্যাশ-প্রুফ সেফ ইম্পোর্ট মেথড
import sslcommerz_lib
SSLCommerzPython = getattr(sslcommerz_lib, 'SSLCommerzPython', None) or getattr(sslcommerz_lib, 'SSLCommerz', None)

@login_required
def initiate_payment(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user
    
    # ক্রেডেনশিয়াল ডিকশনারি তৈরি
    credentials = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_pass': settings.SSLCOMMERZ_STORE_PASS,
        'issandbox': settings.SSLCOMMERZ_IS_SANDBOX
    }
    
    # যদি কোনো কারণে ডাইরেক্ট ক্লাস না পাওয়া যায়, তবে ইন্টারনাল সাব-ফাইল অবজেক্ট নিয়ে আসা
    if SSLCommerzPython is None:
        try:
            from sslcommerz_lib.sslcommerz_lib import SSLCommerzPython
        except (ImportError, ModuleNotFoundError):
            # একদম ব্যাকআপ হিসেবে রুট মডিউলটিকেই ব্যবহার করা
            SSLCommerzPython = sslcommerz_lib

    # SSLCommerz অবজেক্ট তৈরি
    sslcz = SSLCommerzPython(credentials)

    # ১০ ডিজিটের ইউনিক ট্রানজেকশন আইডি তৈরি করা
    transaction_id = str(uuid.uuid4()).replace('-', '')[:10]
    
    # SSLCommerz পোস্ট বডি ডেটা
    post_body = {
        'total_amount': float(item.price), 
        'currency': "BDT",
        'tran_id': transaction_id,
        'success_url': request.build_absolute_uri(f'/payment/success/{transaction_id}/{item.id}/'),
        'fail_url': request.build_absolute_uri('/payment/fail/'),
        'cancel_url': request.build_absolute_uri('/payment/cancel/'),
        'emi_option': 0,
        'cus_name': user.username,
        'cus_email': user.email if user.email else "customer@example.com",
        'cus_phone': '01700000000', 
        'cus_add1': 'Customer Address',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': "NO",
        'product_name': item.name,
        'product_category': item.category.name if item.category else "General",
        'product_profile': "general",
    }

    # ডেটাবেজে পেন্ডিং অর্ডার ট্র্যাক করা
    Order.objects.create(
        user=user,
        item=item,
        transaction_id=transaction_id,
        total_amount=item.price,
        status='Pending'
    )

    # সেশন তৈরি করে গেটওয়ে রেসপন্স নেওয়া
    response = sslcz.createSession(post_body)
    
    # রেসপন্স চেক করে রিডাইরেক্ট করা
    if response and isinstance(response, dict) and 'GatewayPageURL' in response:
        return redirect(response['GatewayPageURL'])
    else:
        return redirect('payment:fail')


@csrf_exempt
def payment_success(request, tran_id, item_id):
    order = get_object_or_404(Order, transaction_id=tran_id)
    item = get_object_or_404(Item, id=item_id)

    if order.status == 'Pending':
        order.status = 'Completed'
        order.save()
        
        # আইটেমটি বিক্রি হয়ে গেছে হিসেবে মার্ক করা
        item.is_sold = True
        item.save()

    return render(request, 'payment/success.html', {'tran_id': tran_id})

@csrf_exempt
def payment_fail(request):
    return render(request, 'payment/fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'payment/cancel.html')