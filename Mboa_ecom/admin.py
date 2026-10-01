from django.contrib import admin
from .models import Category, Product, Commande
# Register your models here.
admin.site.site_header = "MboaShop"
admin.site.site_title = "E-Commerce"

class AdminCategory(admin.ModelAdmin):
    list_display = ('name', 'date_added')
    search_fields = ['name']
admin.site.register(Category, AdminCategory)

class AdminProduct(admin.ModelAdmin):
    list_display = ('name', 'date_added', 'price', 'category')
    search_fields = ('name', 'categrory')
    list_editable = ('price', 'category')
admin.site.register(Product, AdminProduct)

class AdminCommande(admin.ModelAdmin):
    list_display = ('items', 'nom', 'email', 'ville', 'total', 'region', 'adresse')
    search_fields = ('nom', 'email', 'ville')
    list_filter = ('ville', 'region')
admin.site.register(Commande, AdminCommande)