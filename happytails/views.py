from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from store_app.models import Category,Product,Customer,Order
from django.contrib.auth.hashers import make_password, check_password
from unicodedata import category
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import razorpay
from django.conf import settings
from django.urls import reverse
from django.contrib import messages


def Master(request):
    return render(request, 'master.html')

def Forgot(request):
    return render(request, 'forgot.html')

def Aboutus(request):
    return render(request, 'aboutus.html')

def Contactus(request):
    return render(request, 'contactus.html')

def Index(request):
    category=Category.objects.all()
    categoryId=request.GET.get('category')
    if categoryId:
        product=Product.objects.filter(category=categoryId)
    else:
       product=Product.objects.all()

    context={
        'category':category,
        'product':product,
    }
    return render(request, 'index.html',context)

def Signup (request):
    if request.method == 'GET':
        return render(request,'signup.html')
    else:
        postData=request.POST
        firstName=postData.get('firstName')
        lastName=postData.get('lastName')
        email=postData.get('email')
        password=postData.get('password')
        mobilenumber = postData.get('mobilenumber')

        value={
            'firstName':firstName,
            'lastName':lastName,
            'email':email,
            'mobilenumber':mobilenumber,
        }

        print(firstName,lastName,email,password,mobilenumber)

        error_message=None

        user = Customer(first_name=firstName,
                        last_name=lastName,
                        email_address=email,
                        password=password,
                        mobile_number=mobilenumber
                        )

        if not firstName:
            error_message="First Name Required"

        elif len(firstName) < 4:
            error_message ="First Name Should be More Than 4 Character"

        elif len(lastName) < 4:
            error_message = "Last Name Should be More Than 4 Character"

        elif len(email) < 4:
            error_message = "Enter Correct Email Address"

        elif len(password) < 4:
            error_message = "Password Should be More Than 4 Character"

        elif len(mobilenumber) < 4:
            error_message = "Mobile Number Should be More Than 4 Character"

        elif user.isExists():
            error_message = "Email Address already register"

        if not error_message:

            user.password=make_password(user.password)
            user.save()
            return redirect('index')

        else:
            data={
                'error':error_message,
                "values":value
            }

            return render(request, 'signup.html', data)

def Login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer = Customer.objects.get(email_address=email)  # Ensure you use the correct field name
        except Customer.DoesNotExist:  # Correct exception
            customer = None

        error_message = None

        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer_id'] = customer.id
                request.session['email'] = customer.email_address
                return redirect('index')
            else:
                error_message = 'Email or Password Invalid'
        else:
            error_message = 'Email or Password Invalid'

        return render(request, 'login.html', {'error': error_message})

#cart
#@login_required(login_url="/login/")
def cart_add(request, id):
    # Check if email is stored in session
    if "email" not in request.session:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect("login")    # Redirect to login page if not logged in

    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("index")


#@login_required(login_url="/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


#@login_required(login_url="/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


#@login_required(login_url="/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)

    # Check if the product exists in the cart before decrementing
    if str(product.id) in cart.cart:
        if cart.cart[str(product.id)]["quantity"] > 1:
            cart.decrement(product=product)
        else:
            cart.remove(product)    # Remove item from cart when quantity reaches 0

    return redirect("cart_detail")


#@login_required(login_url="/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


#@login_required(login_url="/login/")
def cart_detail(request):
    cart = Cart(request)
    cart_total_amount = sum(int(item['price']) * item['quantity'] for item in request.session.get('cart', {}).values())
    return render(request, 'cart/cart_detail.html', {'cart_total_amount': cart_total_amount})

def checkout(request):
    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')  # Ensure correct name
        cart = request.session.get('cart')
        customer_id = request.session.get('customer_id')

        print("Received Data:", address, pincode, phone, cart, customer_id)  # Debugging

        if not cart:
            return HttpResponse("Cart is empty", status=400)

        if not address or not phone or not pincode:
            return HttpResponse("All fields are required!", status=400)

        total_amount=0
        for key, value in cart.items():
            total_price = int(value['quantity']) * int(value['price'])
            total_amount += total_price
            order = Order(
                product_id=int(key),  # Convert key to integer
                customer_id=customer_id,  # Set customer correctly
                quantity=value['quantity'],
                price=value['price'],
                total_price=total_price,
                address=address,
                phone=phone,
                pincode=pincode,  # Make sure pincode is included
            )
            order.save()

        request.session['cart'] = {}  # Clear cart after checkout
        return redirect(reverse("payment_page") + f"?amount={total_amount}")

    return redirect("index")

def your_order(request):
    customer_id = request.session.get('customer_id')  # Get customer ID from session
    if not customer_id:
        return render(request, "order.html", {"orders": []})  # Return empty orders if no customer

    orders = Order.get_order_by_customer(customer_id)  # Fetch orders for the customer
    return render(request, "order.html", {"orders": orders})

# Razorpay

def payment_page(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Order amount in paise (INR 100 = 10000 paise)
    total_amount = request.GET.get('amount', 0)
    order_amount = int(float(total_amount) * 100)
    #order_amount = 5000  # ₹500
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'

    # Create an order
    order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'payment_capture': '1',  # Auto-capture payment
        'receipt': order_receipt
    })

    context = {
        'order_id': order['id'],
        'amount': order_amount / 100,  # Convert to INR
        'razorpay_key': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'payment.html', context)

def search_products(request):
    query = request.GET.get('q', '').strip()
    print("Search Query:", query)

    products = Product.objects.filter(name__icontains=query) if query else []
    print("Found products:", products)

    return render(request, 'search.html', {'products': products, 'query': query})
