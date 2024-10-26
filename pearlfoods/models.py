from django.db import models
import uuid
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

STATUS_CHOICES = [
    #('pending', 'Pending'),
    ('received', 'Received'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('pickedup', 'Picked Up'),
    ('on_hold', 'On Hold'),
    ('processed', 'Processed'),
]

# Create your models here.
class Contact(models.Model):
    contact_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    mobile = models.CharField(max_length=15, blank=True, null=True)  # New field for mobile number
    desc = models.TextField(max_length=300)
    date = models.DateField()

    def __str__(self):
        return str(self.contact_id)

class Order(models.Model):
    PAYMENT_STATUS = [
        ('COD', 'COD'),
        ('selfpickup', 'Self Pickup'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    date = models.DateField()
    date_confirmed = models.DateField(null=True, blank=True)
    date_processed = models.DateField(null=True, blank=True)
    date_shipped = models.DateField(null=True, blank=True)
    date_delivered = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=11)
    delivery_address = models.TextField(max_length=300)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='received')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='COD')
    date_pickup = models.DateField(null=True, blank=True)
    time_pickup = models.TimeField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    flavor = models.CharField(max_length=100)
    quantity = models.IntegerField()
    
class Product(models.Model):
    MASALA = 'Masala'
    ATTA = 'Atta'
    HOME_REMEDIES = 'Home Remedies'
    HONEY = 'Honey'
    OIL = 'Oil'
    RECIPES = 'Recipes'

    CATEGORY_CHOICES = [
        (MASALA, 'Masala'),
        (ATTA, 'Atta'),
        (HOME_REMEDIES, 'Home Remedies'),
        (HONEY, 'Honey'),
        (OIL, 'Oil'),
        (RECIPES, 'Recipes')
    ]

    UNIT_GRAMS = 'Grams'
    UNIT_KGS = 'Kgs'
    UNIT_PACKET = 'Packet'
    UNIT_LITRE = 'mL'

    UNIT_CHOICES = [
        (UNIT_GRAMS, 'Grams'),
        (UNIT_KGS, 'Kgs'),
        (UNIT_PACKET, 'Packet'),
        (UNIT_LITRE, 'mL'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='icecream_flavors/Upload')
    price_per_unit = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=MASALA)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_GRAMS)  # New field for units

    def __str__(self):
        return f"{self.name} - {self.unit}"

    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# Ensure UserProfile is created for every new user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

models.signals.post_save.connect(create_user_profile, sender=User)

class Cart(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_cart', condition=models.Q(user__isnull=False)),
            models.UniqueConstraint(fields=['session_key'], name='unique_session_key_cart', condition=models.Q(session_key__isnull=False))
        ]

    def __str__(self):
        if self.user:
            return f"Cart {self.id} for {self.user}"
        return f"Cart {self.session_key} for Anonymous User"

    def total_price(self):
        # Ensure total_price is accessed as an attribute
        return sum(item.total_price for item in self.cartitem_set.all())



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    flavor = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Storing it

    def __str__(self):
        return f"{self.quantity} of {self.flavor.name} ({self.flavor.unit})"

        
class Feedback(models.Model):
    STATUS = [
    ('pending', 'Pending'),
    ('active', 'active'),
]
    name = models.CharField(max_length=100)
    feedback = models.TextField()
    rating = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.rating}"
    

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        now = timezone.now()  # This is timezone-aware
        # Ensure created_at is also timezone-aware by using timezone-aware datetime comparison
        return (now - self.created_at).total_seconds() < 3600
    

