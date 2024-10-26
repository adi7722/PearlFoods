from django.shortcuts import render, redirect

from pearlfoods.models import *
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import *
from django.urls import reverse
import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string



logger = logging.getLogger(__name__)


# def index(request):
#     context = {
#         'owner': "Adnaan Ashraf",
#         'year': "2024"
#     }
#     return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

import datetime
def contacts(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            desc = request.POST.get('desc')
            contact = Contact(name=name, email=email, desc=desc, mobile = mobile , date= datetime.now())
            contact.save()
            logger.info(f"Saved contact: {contact}")
            return redirect('contacts')
        except Exception as e:
            logger.error(f"Error saving contact: {e}")
            return render(request, 'contacts.html', {'error_message': 'There was an error saving your contact information. Please try again.'})
    return render(request, 'contacts.html')



def order_view(request):
    if request.method == 'POST':
        flavor_name = request.POST['flavor']
        quantity = request.POST['quantity']
        flavor = Product.objects.get(name=flavor_name)
        
        # Add to cart instead of processing directly
        return redirect('add_to_cart', flavor_id=flavor.id)
        
    return render(request, 'order_form.html')

def order_confirmation(request, context=None):
    if request.method == 'POST' or context:
        if not context:
            context = {
                'flavor': request.POST.get('flavor'),
                'quantity': request.POST.get('quantity'),
                'price': request.POST.get('price'),
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address')
            }

        order = Order(
            name=context['name'],
            email=context['email'],
            flavor=context['flavor'],
            quantity=context['quantity'],
            phone=context['phone'],
            date=datetime.today(),
            delivery_address=context['address'],
            price=context['price']
        )
        order.save()
        logger.info(f"Order saved: {order}")

        return render(request, 'order_confirmation.html', context)

    return redirect('order_view')

def masala_flavors(request):
    flavors = Product.objects.filter(category='Masala')
    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit * 250
        flavor.price_500g = flavor.price_per_unit * 500
        flavor.price_1kg = flavor.price_per_unit * 1000
        
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'masala_flavors.html', {'flavors': flavors, 'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request,"Your profile have been created successfully!!!")
            return redirect('home')  # Redirect to a success page or home
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request,"Your have been logged in successfully!!!")
            return redirect('home')  # Redirect to a success page or home
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request,"Your have been logged out successfully!!")
        return redirect('home')  # Redirect to home page or another page after logout
    return redirect('home')



logger = logging.getLogger(__name__)

from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import Product, Cart, CartItem

def add_to_cart(request, flavor_id):
    # Get the flavor being added to the cart
    flavor = get_object_or_404(Product, id=flavor_id)

    # Get or create the cart for the current user or session
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, flavor=flavor)

    # Initialize the quantity variable
    selected_quantity = 0

    # Get predefined quantity or custom quantity from POST data
    predefined_quantity = request.POST.get('quantity', None)  # The selected radio button (250g, 500g, etc.)
    custom_quantity = request.POST.get('custom_quantity', None)  # The custom quantity input by user
    
    print("This is predefined_quantity: ",predefined_quantity)
    print("This is custom_quantity: ",custom_quantity)
    # Handle predefined quantity cases
    if predefined_quantity:
        selected_quantity = int(predefined_quantity)  # 250 grams
        print("This is selected quantity: ",selected_quantity)
        print("This is the type of selected_quantity: ", type(selected_quantity))
    
    # Handle custom quantity input
    elif custom_quantity:
        # Validate minimum custom quantity (50 grams)
        selected_quantity = int(custom_quantity)

    else:
        # Validate minimum custom quantity (50 grams)
        selected_quantity = int(custom_quantity) + int(predefined_quantity)
            

    # Calculate the total price based on the selected quantity and price per unit
    price_per_unit = flavor.price_per_unit  # Assuming the price is per gram
    total_price = Decimal(selected_quantity) * Decimal(price_per_unit)

    # Update the cart item with the selected quantity and total price
    cart_item.quantity += selected_quantity  # Add the selected quantity (in grams)
    cart_item.total_price = Decimal(cart_item.total_price) + total_price  # Correctly update the total price

    cart_item.save()

    return redirect('cart_detail')  # Redirect to the cart detail page



def cart_detail(request):
    if request.user.is_authenticated:
        # Get or create a cart for the authenticated user
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, use session key
        session_key = request.session.session_key
        if not session_key:
            # Create a session if one doesn't exist
            request.session.create()
            session_key = request.session.session_key
        
        # Get or create a cart for the anonymous user (session-based)
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    # Retrieve all cart items and calculate total price
    cart_items = cart.cartitem_set.all()
    total_price = cart.total_price()

    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})


def checkout(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        profile = get_object_or_404(UserProfile, user=request.user)
        initial_data = {
            'name': request.user.get_full_name(),
            'email': request.user.email,
            'phone_number': profile.phone_number,
            'delivery_address': profile.address
        }
        # Pass the user to the form to apply readonly attributes
        form = CheckoutForm(request.POST or None, user=request.user, initial=initial_data)
    else:
        session_key = request.session.session_key
        cart = get_object_or_404(Cart, session_key=session_key)
        initial_data = {}
        form = CheckoutForm(request.POST or None, user=None, initial=initial_data)

    if request.method == "POST":
        if form.is_valid():
            # Extract validated form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone_number']
            delivery_address = form.cleaned_data['delivery_address']
            payment_method = request.POST.get('payment_method')
            date_pickup = request.POST.get('pickup_date') or None
            time_pickup = request.POST.get('pickup_time') or None

            # Calculate total price for the entire cart
            total_price = Decimal(0)
            flavor_quantities = {}
            flavor_prices = {}

            for item in cart.cartitem_set.all():
                total_price += item.total_price
                flavor_quantities[item.flavor] = flavor_quantities.get(item.flavor, 0) + item.quantity
                flavor_prices[item.flavor] = flavor_prices.get(item.flavor, Decimal(0)) + item.total_price

            # Add delivery charges for COD
            delivery_charge = Decimal(250) if payment_method == 'COD' else Decimal(0)
            final_total_price = total_price + delivery_charge

            # Create the order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                delivery_address=delivery_address,
                price=final_total_price,
                payment_status=payment_method,
                date_pickup=date_pickup,
                time_pickup=time_pickup,
                date=timezone.now()
            )

            # Create OrderItems and store in order_items list for email
            order_items = []
            for flavor, quantity in flavor_quantities.items():
                item = OrderItem.objects.create(order=order, flavor=flavor, quantity=quantity)
                order_items.append({
                    'flavor': flavor,
                    'quantity': quantity,
                    'price': flavor_prices[flavor]  # Include the price for each flavor
                })

            # Send order confirmation email
            subject = 'Order Confirmation'
            html_message = render_to_string('order_confirmation_email.html', {
                'name': name,
                'order': order,
                'total_price': final_total_price,
                'delivery_address': delivery_address,
                'payment_method': payment_method,
                'date_pickup': date_pickup,
                'time_pickup': time_pickup,
                'order_items': order_items,  # Pass the order items with price and quantity
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,  # From email
                [email],  # To email
                html_message=html_message, 
                fail_silently=False,
            )

            # Clear the cart after checkout
            cart.cartitem_set.all().delete()

            # Redirect to success page
            return redirect('success', order_id=order.id)
    else:
        form = CheckoutForm(user=request.user if request.user.is_authenticated else None, initial=initial_data)

    logger.debug(f'Form initial data: {initial_data}')
    logger.debug(f'Form: {form}')

    # Calculate the price for display
    total_price = sum(item.total_price for item in cart.cartitem_set.all())
    
    return render(request, 'checkout.html', {
        'total_price': total_price,
        'form': form,
        'initial_data': initial_data,
    })

def success(request, order_id):
    # Fetch the order details based on the order ID
    order = get_object_or_404(Order, id=order_id)
    
    # Pass the order details to the template
    context = {
        'order': order
    }
    return render(request, 'success.html', context)



def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        session_key = request.session.session_key
        cart = get_object_or_404(Cart, session_key=session_key)
    cart_item = get_object_or_404(CartItem, cart=cart, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')

def index(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FeedbackForm()
    
    feedbacks = Feedback.objects.all().order_by('-created_at')
    active_feedbacks = feedbacks.filter(status='active').count()
    rating_range = [1, 2, 3, 4, 5]
    context = {
        'owner': "Adnaan Ashraf",
        'year': "2024",
        'feedbacks': feedbacks,
        'form': form,
        'rating_range': rating_range,
        'active_feedbacks': active_feedbacks,
    }
    
    return render(request, 'index.html', context)

def flour_flavors(request):
    flavors = Product.objects.filter(category='Atta')
    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit 
        flavor.price_500g = flavor.price_per_unit * 2
        flavor.price_1kg = flavor.price_per_unit * 5
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'flour_flavors.html', {'flavors': flavors, 'form': form})

def remedies(request):
    flavors = Product.objects.filter(category='Home Remedies')
    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit
        flavor.price_500g = flavor.price_per_unit * 2
        flavor.price_1kg = flavor.price_per_unit * 3
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'remedies.html', {'flavors': flavors, 'form': form})

def recipes(request):
    flavors = Product.objects.filter(category='Recipes')
    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit 
        flavor.price_500g = flavor.price_per_unit * 2
        flavor.price_1kg = flavor.price_per_unit * 3
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'recipes.html', {'flavors': flavors, 'form': form})

def honey(request):
    flavors = Product.objects.filter(category='Honey')
    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit * 250
        flavor.price_500g = flavor.price_per_unit * 500
        flavor.price_1kg = flavor.price_per_unit * 1000
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'honey.html', {'flavors': flavors, 'form': form})

def oil(request):
    flavors = Product.objects.filter(category='Oil')

    for flavor in flavors:
        flavor.price_250g = flavor.price_per_unit *250
        flavor.price_500g = flavor.price_per_unit *500
        flavor.price_1kg = flavor.price_per_unit *1000
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the form data
            flavor = form.cleaned_data['flavor']
            quantity = form.cleaned_data['quantity']
            # Redirect to a confirmation page or perform other actions
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'oil.html', {'flavors': flavors, 'form': form})

@login_required
def my_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    
    total_orders = orders.count()
    orders_processed = orders.filter(status='processed').count()
    orders_shipped = orders.filter(status='shipped').count()
    orders_delivered = orders.filter(status='delivered').count()
    COD_orders = orders.filter(payment_status='COD')
    selfpickup_orders = orders.filter(payment_status='selfpickup')

    context = {
        'user': user,
        'orders': orders,
        'total_orders': total_orders,
        'orders_processed': orders_processed,
        'orders_shipped': orders_shipped,
        'orders_delivered': orders_delivered,
        'COD_orders': COD_orders,
        'selfpickup_orders': selfpickup_orders,
    }
    return render(request, 'my_orders.html', context)

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Define classes for each step based on the order status
    steps = {
        'received': 'completed' if order.status in ['Received', 'Confirmed', 'Processed', 'Delivered'] else 'incomplete',
        'confirmed': 'completed' if order.status in ['Confirmed', 'Processed', 'Delivered'] else 'incomplete',
        'processed': 'completed' if order.status in ['Processed', 'Delivered'] else 'incomplete',
        'delivered': 'completed' if order.status == 'Delivered' else 'incomplete',
    }

    # Add special handling for cancelled and on hold statuses
    if order.status == 'Cancelled':
        steps = {k: 'cancelled' for k in steps.keys()}
    elif order.status == 'On Hold':
        steps = {k: 'on-hold' if k != 'received' else 'completed' for k in steps.keys()}

    context = {
        'order': order,
        'steps': steps,
    }
    
    return render(request, 'order_details.html', context)

def testing(request):
    return render(request, 'carosel_testing.html')

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generate a random reset code and save it in the database
            reset_code = get_random_string(6, allowed_chars='0123456789')
            PasswordResetCode.objects.create(user=user, code=reset_code, created_at=datetime.datetime.now())

            # Send the reset code via email
            send_mail(
                'Password Reset Code',
                f'Hello,\n\nYour password reset code is **{reset_code}**.\n'
                f'Please note that this code will expire in **15 minutes** for your security.\n'
                f'If you did not request this reset, please disregard this message.\n\nThank you!',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'A password reset code has been sent to your email.')
            return redirect('password_reset_verify')  # Redirect to verify code page
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {'form': form})

def password_reset_verify(request):
    if request.method == 'POST':
        form = PasswordResetVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                reset_code = PasswordResetCode.objects.get(code=code)
                if reset_code.is_valid():  # Assuming you have an is_valid method to check validity
                    request.session['user_id'] = reset_code.user.id  # Store user ID in session to reset password later
                    return redirect('password_reset_confirm')  # Redirect to password reset confirmation page
                else:
                    messages.error(request, 'The reset code is invalid or has expired.')
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'Invalid reset code.')
    else:
        form = PasswordResetVerificationForm()  # Create a new instance of the form

    return render(request, 'password_reset_verify.html', {'form': form})

def password_reset_confirm(request):
    # Retrieve the user based on the session or token you set earlier
    user_id = request.session.get('user_id')  # Get user ID from the session
    User = get_user_model()  # This gets the User model (custom or default)

    try:
        user = User.objects.get(id=user_id)  # Fetch the user object
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('password_reset_request')  # Redirect to the request page if user not found

    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)  # Pass the user and POST data
        if form.is_valid():
            form.save()  # Save the new password
            email = user.email
            send_mail(
                'Password Changed Successfully',
                f'Hello,\n\nYour password has been changed successfully.\n'
                f'If you did not request this change, please contact our support team immediately.\n\n'
                f'Thank you for using our service!',
                'from@example.com',
                [email],
                fail_silently=False,
                )
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('login')  # Redirect to the login page
    else:
        form = CustomSetPasswordForm(user)  # Pass the user for GET request

    return render(request, 'password_reset_confirm.html', {'form': form})

