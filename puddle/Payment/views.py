import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order
from item.models import Item

# ১. ইমপোর্ট এরর সমাধানের জন্য সবচেয়ে নিরাপদ পদ্ধতি
try:
    from sslcommerz_lib import SSLCommerz
except ImportError:
    try:
        from sslcommerz_lib import SSLCommerzPython as SSLCommerz
    except ImportError:
        # যদি উপরের কোনটিই কাজ না করে তবে সরাসরি মডিউল ট্রাই করবে
        import sslcommerz_lib as SSLCommerz

def initiate_payment(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user
    
    # ২. সেটিংস থেকে ক্রেডেনশিয়াল নেয়া
    settings_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_pass': settings.SSLCOMMERZ_STORE_PASS,
        'issandbox': settings.SSLCOMMERZ_IS_SANDBOX,
    }
    
    # ৩. অবজেক্ট তৈরি (সঠিক ক্লাস ব্যবহার করে)
    # যদি আপনার লাইব্রেরিটি ফাংশন বেসড হয় তবে শুধু SSLCommerz ব্যবহার হবে
    try:
        sslcz = SSLCommerz(settings_data)
    except TypeError:
        # কিছু ভার্সনে সরাসরি মডিউল কল করতে হয়
        from sslcommerz_lib import SSLCommerz
        sslcz = SSLCommerz(settings_data)

    transaction_id = str(uuid.uuid4())[:10]
    
    # ৪. পেমেন্ট ডাটা প্রস্তুত করা
    post_body = {
        'total_amount': float(item.price), # নিশ্চিত করতে float কনভার্ট করা হয়েছে
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

    # ৫. ডাটাবেসে পেন্ডিং অর্ডার তৈরি
    Order.objects.create(
        user=user,
        item=item,
        transaction_id=transaction_id,
        total_amount=item.price,
        status='Pending'
    )

    # ৬. পেমেন্ট গেটওয়ে কল করা
    response = sslcz.init_payment(post_body)
    
    # রেসপন্স চেক করে রিডাইরেক্ট করা
    if response and 'GatewayPageURL' in response:
        return redirect(response['GatewayPageURL'])
    else:
        # গেটওয়েতে সমস্যা হলে ফেইল পেজে যাবে
        return redirect('payment_fail')

@csrf_exempt
def payment_success(request, tran_id, item_id):
    order = get_object_or_404(Order, transaction_id=tran_id)
    item = get_object_or_404(Item, id=item_id)

    if order.status == 'Pending':
        order.status = 'Completed'
        order.save()
        
        # আইটেম সোল্ড মার্ক করা
        item.is_sold = True
        item.save()

    return render(request, 'payment/success.html', {'tran_id': tran_id})

@csrf_exempt
def payment_fail(request):
    return render(request, 'payment/fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'payment/cancel.html')

@csrf_exempt
def payment_success(request, tran_id, item_id):
    order = get_object_or_404(Order, transaction_id=tran_id)
    item = get_object_or_404(Item, id=item_id)

    if order.status == 'Pending':
        order.status = 'Completed'
        order.save()
        
       
        item.is_sold = True
        item.save()

    return render(request, 'payment/success.html', {'tran_id': tran_id})

@csrf_exempt
def payment_fail(request):
    return render(request, 'payment/fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'payment/cancel.html')