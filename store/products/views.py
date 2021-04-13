from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from .models import *
from django.contrib.auth.models import User


def register(request):

    if request.method == 'POST':
        username = request.POST['user_name']
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            note = "username is already taken"
            context = {'note': note}
            return render(request, 'html/Registration.html', context=context)
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname,
                                            last_name=lastname, is_staff=True)
            customer = Customer.objects.create(user=user, email=email, name=username)
            user.save()
            customer.save()
            note = "Register Done"
            context = {'note': note}

            return render(request, 'html/Registration.html', context=context)

    else:
        return render(request, 'html/Registration.html')


def product_view(request, pk):

    product = Product.objects.get(id=pk)
    owner = product.owner.name
    comments = [c for c in Comments.objects.all() if c.product == product]

    return render(request, 'html/product_show.html', context={'comments': comments, 'product': product, 'owner': owner})


def add_item(request, pk):
    if request.user.is_authenticated:
        user = request.user.customer
        product = Product.objects.get(id=pk)
        orders = Order.objects.all()
        if request.method == 'GET':
            b = False
            for o in orders:
                if o.customer == user:
                    if o.product == product:
                        if product.quantity > 0:
                            o.quantity += 1
                            product.quantity -= 1
                            o.save()
                            product.save()
                        b = True

            if not b:
                order = Order.objects.create(customer=user, product=product, quantity=1)
                product.quantity -= 1
                order.save()
                product.save()
        return cart(request)
    else:
        return render(request, 'html/Registration.html')


def remove(request, pk):
    items = []
    if request.user.is_authenticated:
        user = request.user.customer
        product = Product.objects.get(id=pk)
        orders = Order.objects.all()
        if request.method == 'GET':

            for o in orders:
                if o.customer == user:
                    items.append(o)
                    if o.product == product:
                        if o.quantity > 1:
                            o.quantity -= 1
                            product.quantity += 1
                            o.save()
                            product.save()
                        else:
                            delete(request, pk)
                            product.quantity += 1
                            items.remove(o)
        return cart(request)

    else:
        return render(request, 'html/Registration.html')


def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return store(request)
        else:
            return render(request, 'html/login.html')
    else:
        return render(request, 'html/login.html')


def log_out(request):
    if request.method == 'GET':
        logout(request)

        return store(request)


def add_product(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            p_name = request.POST['product_name']
            price = request.POST['price']
            description = request.POST['description']
            quantity = request.POST['quantity']
            image = request.POST['image']

            if float(request.POST['price']) > 0 and float(request.POST['quantity']) > 0 :
                product = Product.objects.create(name=p_name, price=price, description=description, quantity=quantity,
                                                 owner=request.user.customer, image=image)
                product.save()
                return store(request)
            else:
                note = "Price added incorrectly"
                context = {'note': note}
                return render(request, 'html/add.html', context)
        return render(request, 'html/add.html')
    else:
        return render(request, 'html/Registration.html')


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'html/Store.html', context)


def cart(request):
    items = []
    if request.user.is_authenticated:
        items = [o for o in Order.objects.all() if o.customer == request.user.customer]
    return render(request, 'html/Cart.html', context={'items': items})


def check_out(request):

    if request.user.is_authenticated:
        custom = request.user.customer
        if request.method == 'GET':
            items = [o for o in Order.objects.all() if o.customer == custom]
            return render(request, 'html/CheckOut.html', context={'items': items})
        else:
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zipcode = request.POST.get('zipcode')

            shipping_data = ShippingAddress.objects.create(customer=custom, address=address, city=city,
                                                           state=state, zipcode=zipcode)
            shipping_data.save()
            orders = Order.objects.all()
            for o in orders:
                if o.customer.name == custom.name:
                    o.shipping = shipping_data
                    o.save()
            context = {'note': "your information saved and send to delivery department"}
            return render(request, 'html/CheckOut.html', context)
    else:
        return render(request, 'html/CheckOut.html')


def add_comment(request, pk):

    if request.user.is_authenticated:
        if request.method == 'POST':
            user = request.user.customer
            product = Product.objects.get(id=pk)
            text = request.POST['comment']
            comment = Comments.objects.create(customer=user, product=product, text=text)
            comment.save()

        return product_view(request, pk)
    else:
        return product_view(request, pk)


def delete(request, pk):
    items = []
    orders = Order.objects.all()
    product = Product.objects.get(id=pk)

    for o in orders:
        if o.product == product:
            product.quantity += o.quantity
            o.delete()
            product.save()
        else:
            items.append(o)

    return cart(request)


def rate(request, pk, r):
    if request.method == 'GET':
        if request.user.is_authenticated:

            user = request.user.customer
            product = Product.objects.get(id=pk)
            if Rate.objects.filter(customer = user).exists():
                return product_view(request, pk)
            else:
                new_rate = Rate.objects.create(customer=user, product=product, rate=r)
                new_rate.save()
                return product_view(request, pk)

        else:
            return product_view(request, pk)


def delete_product(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return store(request)


def show(request):

    products = [p for p in Product.objects.all() if p.owner.name == request.user.customer.name]

    return render(request, 'html/Store.html', context={'products': products})


def search(request):
    if request.method == 'POST':

        s_date = request.POST.get('start_date')
        f_date = request.POST.get('finish_date')
        s_price = int(request.POST.get('start_price'))
        f_price = int(request.POST.get('finish_price'))

        products = Product.objects.all().filter(date__range=[s_date, f_date]).filter(price__range=[s_price, f_price])

        context = {'products': products}
        return render(request, 'html/Store.html', context)
    else:
        return render(request, 'html/search.html')
