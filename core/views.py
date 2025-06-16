from django.shortcuts import render, get_object_or_404, redirect
from .models import Product,  Brand, Order, OrderItem, ContactMessage, Feedback
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils.dateparse import parse_date
from .forms import ProductForm
from .forms import UserProfileForm
from .forms import ContactForm
from .forms import FeedbackForm

def home(request):
    # Handle brand search query
    query = request.GET.get('q', '')
    if query:
        brands = Brand.objects.filter(name__icontains=query)
    else:
        brands = Brand.objects.all()

    # Handle feedback form submission
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback_form.save()  # Save the feedback to the database
            return redirect('home')  # Redirect to the home page after submission
    else:
        feedback_form = FeedbackForm()

    return render(request, 'index.html', {
        'brands': brands,
        'query': query,
        'form': feedback_form,
    })


# About page
def about(request):
    return render(request, 'about.html')


def brand_profile(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)  # Fetch the brand using brand_id
    query = request.GET.get('q', '')  # Get search query parameter

    # Fetch products associated with the brand and filter by the search query if present
    products = Product.objects.filter(brand=brand)
    if query:
        products = products.filter(name__icontains=query)

    # Handle contact form submission (no email sending, just save to the database)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message to the database without sending email
            contact_message = form.save(commit=False)
            contact_message.brand = brand
            contact_message.user = request.user if request.user.is_authenticated else None
            contact_message.save()

            # Show a success message to the user
            return render(request, 'brand_profile.html', {
                'brand': brand,
                'products': products,
                'query': query,
                'form': form,
                'success_message': 'Thank you for contacting us! We will get back to you shortly.'
            })
    else:
        form = ContactForm()

    return render(request, 'brand_profile.html', {
        'brand': brand,
        'products': products,
        'query': query,
        'form': form,  # Pass the form to the template
    })


# Product detail page with add to cart functionality
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_id_str = str(product_id)  # Session keys must be strings

    if request.method == "POST":
        cart = request.session.get('cart', {})

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {'quantity': 1}

        request.session['cart'] = cart
        return redirect('cart')

    return render(request, 'product_detail.html', {'product': product})


# View cart and calculate total
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id_str, item in cart.items():
        product = Product.objects.get(id=int(product_id_str))
        item_total = product.price * item['quantity']
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'item_total': item_total
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# Update quantity of a product in the cart
def update_cart(request, product_id):
    if request.method == "POST":
        product_id_str = str(product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})

        if product_id_str in cart:
            cart[product_id_str]['quantity'] = quantity

        request.session['cart'] = cart
        return redirect('cart')
    else:
        return redirect('cart')


# Remove product from the cart
def remove_from_cart(request, product_id):
    product_id_str = str(product_id)
    cart = request.session.get('cart', {})

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart

    return redirect('cart')


# Checkout process (requires login)
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    cart_items = []
    total = 0
    for product_id_str, item in cart.items():
        product = Product.objects.get(id=int(product_id_str))
        quantity = item['quantity']
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        order = Order.objects.create(user=request.user, total_price=total, phone_number=phone_number)
        for entry in cart_items:
            OrderItem.objects.create(
                order=order,
                product=entry['product'],
                quantity=entry['quantity']
            )
        request.session['cart'] = {}
        return render(request, 'order_success.html', {'order': order})

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })

# Register new users
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



# Add a product to the cart
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {'quantity': 1}

    request.session['cart'] = cart
    return redirect('cart')


@login_required
def brand_dashboard(request):
    user = request.user

    # Determine the correct brand based on the user type
    if user.is_superuser:
        brand = Brand.objects.first()  # Superuser fallback
    elif hasattr(user, 'brandowner'):
        brand = user.brandowner.brand
    else:
        return redirect('home')

    # Get products related to the brand
    products = Product.objects.filter(brand=brand)

    # Get contact messages for the brand
    contact_messages = ContactMessage.objects.filter(brand=brand)

    # Get order items where the product is linked to this brand
    order_items = OrderItem.objects.filter(product__brand=brand).select_related(
        'order', 'product', 'order__user'
    )

    # Filter by date if provided in GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        order_items = order_items.filter(order__created_at__gte=parse_date(start_date))
    if end_date:
        order_items = order_items.filter(order__created_at__lte=parse_date(end_date))

    # Order by most recent orders
    order_items = order_items.order_by('-order__created_at')

    return render(request, 'brand_dashboard.html', {
        'brand': brand,
        'products': products,
        'contact_messages': contact_messages,
        'order_items': order_items,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def add_product(request):
    brand = Brand.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.brand = brand
            product.save()
            return redirect('brand_dashboard')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


@login_required
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if product.brand.user != request.user:
        return redirect('brand_dashboard')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('brand_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})


@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if product.brand.user == request.user:
        product.delete()
    return redirect('brand_dashboard')


@login_required
def brand_orders(request):
    # Get all order items that belong to products owned by this brand
    order_items = OrderItem.objects.filter(product__brand__user=request.user).select_related('order', 'product')

    return render(request, 'brand_orders.html', {'order_items': order_items})


@login_required
def user_dashboard(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')

    for order in orders:
        order.total_price = sum(item.product.price * item.quantity for item in order.items.all())

    return render(request, 'dashboard.html', {'orders': orders})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('update_profile')  # Redirect to the profile update page after saving
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': form})

