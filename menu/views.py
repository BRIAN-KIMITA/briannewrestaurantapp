from django.shortcuts import render,get_object_or_404,redirect
from .models import MenuItem,Order,OrderItem
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
import base64, requests
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
@login_required
def menu(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'menu.html', {'menu_items': menu_items})



@login_required
def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1  # Increment quantity
    request.session['cart'] = cart
    messages.success(request, "Item added to cart successfully!")
    return redirect('menu')  # Stay on menu so user can add more

# This decorator ensures only authenticated users can access the view.
# If the user is not logged in, they'll be redirected to the login page.
@login_required
def view_cart(request):
#     Retrieves the cart data from the session.
# cart is a dictionary: {item_id: quantity}.
# If no cart exists, it returns an empty dict.
    cart = request.session.get('cart', {})
# items: a list to hold item details (name, price, quantity, subtotal).
# total: keeps track of the grand total.
    items = []
    total = 0
#     Loops through each item in the cart.

# item_id is a string (because session data is stored as strings).

# quantity is the number of that item added.
    for item_id, quantity in cart.items():
#  Fetches the MenuItem from the database by its primary key (pk).
# Converts the item_id string to the correct DB record.
        menu_item = MenuItem.objects.get(pk=item_id)
# Builds a dictionary for each item, with:
# item:the MenuItem object (e.g., name, description, image).
# quantity: number of units.
# subtotal: price × quantity.
        items.append({
            'item': menu_item,
            'quantity': quantity,
            'subtotal': menu_item.price * quantity
        })
    #Adds the item's subtotal to the total cart cost.
        total += menu_item.price * quantity
# Sends the data to the cart.html template.
# Template can now loop through items and display total.
    return render(request, 'cart.html', {'items': items, 'total': total})


#Fetches the shopping cart from the user's session, retrieves each product, calculates subtotal and total,
# and returns structured data.
def get_cart_items(request):
    #Looks for 'cart' in the user's session.
    #If not found, it defaults to an empty dictionary {}.
    cart = request.session.get('cart', {})
   # Prepares an empty list to hold item details and Initializes the total cost to be 0.
    items = []
    total = 0
    #Loops through each item in the cart.
    #item_id = product ID, quantity = how many units were added.
    for item_id, quantity in cart.items():
        #Retrieves the actual product (MenuItem) from the database.
        item = MenuItem.objects.get(id=item_id)
        #Calculates cost for that item.
        #adds it to the running total.
        subtotal = item.price * quantity
        total += subtotal
    #     Stores a dictionary for each item with:
    # product details,
    # quantity,
    # subtotal.
        items.append({'item': item, 'quantity': quantity, 'subtotal': subtotal})
    # Returns:
    # items: a list of cart items with details.
    # total: total price of the entire cart.
    return items, total
#Takes an HTML template and data context, renders it to HTML, and converts it to a PDF file.
def generate_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None
#authorized users must be logged in to access this view
@login_required
#the naming and declaration of the view and its structure
def checkout(request):
#This gets the items currently in the user's cart and their total price.
#get_cart_items() is a custom utility function that pulls data from the session (e.g., request.session['cart']).
    items, total = get_cart_items(request)
#This block runs when the user submits the checkout form.
    if request.method == 'POST':
#Collects the customer details from the HTML form.
        customer_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        notes = request.POST.get('notes', '')
# Save Order
#Creates a new Order object in the database with the submitted customer information.
        order = Order.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            notes=notes,
        )
#Loops through each cart item and saves it to the OrderItem model, linking it to the newly created order.
# Save Order Items
        for entry in items:
            OrderItem.objects.create(
                order=order,
                item=entry['item'],
                quantity=entry['quantity']
            )

        order_items = order.items.all()

        # Generate PDF receipt
        pdf_context = {
            'order': order,
            'items': order_items,
            'total': order.total_price()
        }
#A PDF receipt is generated using an HTML template (order_receipt.html) and context data.
#generate_pdf() is likely a custom function that renders the template and converts it to a PDF.
        pdf = generate_pdf('pdfs/order_receipt.html', pdf_context)

        # Send confirmation email with PDF
        # Composes an email with a thank-you message.
        #If PDF was successfully created, it's attached to the email.
        #The email is then sent to the customer's email address.
        email_message = EmailMessage(
            subject=f"Order Confirmation #{order.id}",
            body="Thank you for your order. Please find the attached receipt.",
            from_email='briankimita21@gmail.com',
            to=[email],
        )

        if pdf:
            email_message.attach(f"Receipt_Order_{order.id}.pdf", pdf, 'application/pdf')

        email_message.send()
# Empties the user's cart in the session.
# Displays a success message.
# Redirects to a success page.
# Clear cart and notify user
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully! You will pay by Cash or M-Pesa upon delivery. A receipt has been sent to your email.")


        return redirect('order_success', order_id=order.id)

#If the request is not a POST (i.e., user is just viewing the checkout page), it renders the checkout.html template, passing in the cart items and total price.
    return render(request, 'checkout.html', {'items': items, 'total': total, 'enable_mpesa': False }) # control visibility )

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})


def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        auth=(consumer_key, consumer_secret)
    )

    if response.status_code != 200:
        return None

    return response.json().get('access_token')



@login_required
def lipa_na_mpesa_online(request, order_id):
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({'error': 'Access token not obtained'}, status=500)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    # Ensure phone is in 2547XXXXXXXX format
    phone_number = order.phone
    if phone_number.startswith('07'):
        phone_number = '254' + phone_number[1:]

    amount = int(order.total_price())

    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"Order{order.id}",
        "TransactionDesc": "Feane order payment"
    }

    print("Sending STK Push payload:", payload)

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )

    print("STK Push Response:", response.status_code, response.text)

    return render(request, 'mpesa_payment_sent.html', {
    'order': order,
    'message': 'A payment request has been sent to your M-Pesa. Please complete it to confirm your order.'
})


@login_required
def update_cart_quantity(request, item_id):
    # Makes sure the request is a form submission.
    if request.method == 'POST':
        #Gets the new quantity from the form. Defaults to 1 if not given.
        quantity = int(request.POST.get('quantity', 1))
        #Retrieves the cart from session.
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[str(item_id)] = quantity
        else:
            cart.pop(str(item_id), None)
        request.session['cart'] = cart
    return redirect('view_cart')
@login_required
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    cart.pop(str(item_id), None)
    request.session['cart'] = cart
    return redirect('view_cart')



