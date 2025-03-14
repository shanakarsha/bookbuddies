from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.
class UserProfile(models.Model):
    name = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, default='No Phone Number')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


    def __str__(self):
        return self.name.username
        
    @property
    def email(self):
        return self.name.email     

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensure names are unique
    image = models.ImageField(upload_to='genre_images/', null=True, blank=True) 
    def __str__(self):
        return self.name  
        
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_pic = models.ImageField(upload_to='book_covers/')
    description = models.TextField()
    book_file = models.FileField(upload_to='book_files/')
    genres = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books')  

    def __str__(self):
        return self.title   
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0
    def get_partial_price(self):
        """Returns 20% of the book price"""
        return self.price * 0.2

class PurchasedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    full_purchase = models.BooleanField(default=False)
    partial_purchase = models.BooleanField(default=False)  # True when user pays 20%
    timestamp = models.DateTimeField(default=now)


class Rating(models.Model):
    book = models.ForeignKey(Book, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)] ,default=1)  # 1 to 5 stars

    class Meta:
        unique_together = ('book', 'user') 

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Automatically filled
    stripe_payment_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} (${self.amount})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} - {self.quantity}"
    def total_price(self):
        return self.quantity * self.book.price     