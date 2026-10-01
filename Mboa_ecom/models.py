from django.db import models
from django.db.models import ForeignKey

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)   
    category = ForeignKey(Category, related_name="categorie", on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
            return self.name

class Commande(models.Model):
    total = models.CharField(max_length=300)
    items = models.CharField(max_length=300)
    nom= models.CharField(max_length=300)
    email = models.EmailField()
    adresse = models.CharField(max_length=200)
    ville = models.CharField(max_length=150)
    region = models.CharField(max_length=300)
    zip = models.CharField(max_length=300)
    date_commande = models.DateTimeField(auto_now=True)

    class  Meta:
        ordering = ['-date_commande']

    def __str__(self):
         return self.nom