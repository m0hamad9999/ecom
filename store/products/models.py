from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE, null=True, blank=True)
    name = models.TextField(max_length=200, null=True)
    email = models.TextField(max_length=200, null=True)

    def __str__(self):
        return self.name

    @property
    def sum_order(self):
        orders = Order.objects.all()
        return len([o for o in orders if o.customer.name == self.name])

    @property
    def sum_cart(self):
        return sum([o.get_total for o in Order.objects.all() if o.customer.name == self.name])


class Product(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=False, default=0)
    image = models.ImageField(null=True, blank=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.FloatField(null=False, default=0)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url =''
        return url

    @property
    def sum_comment(self):
        comments = Comments.objects.all()
        return len([c for c in comments if c.product.name == self.name])

    @property
    def rate(self):
        Rates = [r.rate for r in Rate.objects.all() if r.product.name == self.name]
        return sum(Rates)/len(Rates) if len(Rates) != 0 else 0.0


class Comments(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.text)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=100, null=False)
    city = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    zipcode = models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    shipping = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_total(self):
        return self.product.price * self.quantity


class Rate(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.FloatField(null=False)

    def __str__(self):
        return str(self.rate)

