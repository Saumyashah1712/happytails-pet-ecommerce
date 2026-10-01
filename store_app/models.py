import datetime
from django.db import models

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=150)

    def __str__(self):
        return self.name

class Sub_Category(models.Model):
    name=models.CharField(max_length=150)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=False,default='')
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE, null=False, default='')
    image = models.ImageField(upload_to='ecommerce/pimg')
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email_address = models.EmailField()
    password = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=10)


    @staticmethod
    def get_all_customer():
        return Customer.objects.all()

    def __str__(self):
        return self.first_name

    def isExists(self):
        if Customer.objects.filter(email_address=self.email_address):
            return True

        return False

class Order(models.Model):
    image=models.ImageField(upload_to='ecommerce/order/pimg')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity=models.CharField(max_length=5)
    price=models.IntegerField()
    total_price = models.IntegerField(default=0)    # New Field
    address=models.TextField()
    phone=models.CharField(max_length=10)
    pincode=models.CharField(max_length=10)
    date=models.DateField(default=datetime.datetime.today)

    def __str__(self):
        return self.product.name

    @staticmethod
    def get_order_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id)

