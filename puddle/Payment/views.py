import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_lib import SSLCommerzPython
from django.conf import settings
from .models import Order
from item.models import Item

def initiate_payment(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user
    
    # SSLCommerz সেটিংস (আপনার settings.py থেকে নিবে)
    sslcz = SSLCommerzPython({
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_pass': settings.SSLCOMMERZ_STORE_PASS,
        'issandbox': settings.SSLCOMMERZ_IS_SANDBOX,
    })

    transaction_id = str(uuid.uuid4())[:10]
    
    # পেমেন্ট ডাটা প্রস্তুত করা
    post_body = {
        'total_amount': item.price,
        'currency': "BDT",
        'tran_id': transaction_id,
        'success_url': request.build_absolute_uri(f'/payment/success/{transaction_id}/{item.id}/'),
        'fail_url': request.build_absolute_uri('/payment/fail/'),
        'cancel_url': request.build_absolute_uri('/payment/cancel/'),
        'emi_option': 0,
        'cus_name': user.username,
        'cus_email': user.email,
        'cus_phone': '01700000000', 
        'cus_add1': 'Customer Address',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': "NO",
        'product_name': item.name,
        'product_category': item.category.name,
        'product_profile': "general",
    }

    
    Order.objects.create(
        user=user,
        item=item,
        transaction_id=transaction_id,
        total_amount=item.price,
        status='Pending'
    )

    response = sslcz.init_payment(post_body)
    return redirect(response['GatewayPageURL'])

@csrf_exempt
def payment_success(request, tran_id, item_id):
    # ট্রানজ্যাকশন আইডি দিয়ে অর্ডার খুঁজে বের করা
    order = get_object_or_404(Order, transaction_id=tran_id)
    item = get_object_or_404(Item, id=item_id)

    if order.status == 'Pending':
        order.status = 'Completed'
        order.save()
        
        # আইটেমটি বিক্রি হয়ে গেছে হিসেবে মার্ক করা (স্লো-নেস ও লজিক সমাধান)
        item.is_sold = True
        item.save()

    return render(request, 'payment/success.html', {'tran_id': tran_id})

@csrf_exempt
def payment_fail(request):
    return render(request, 'payment/fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'payment/cancel.html')