from django.shortcuts import render, redirect
from .models import Product, Commande
from django.core.paginator import Paginator
# Create your views here.
def index(request):
    product_object = Product.objects.all()
    item_name = request.GET.get('item-name')
    if item_name !='' and item_name is not None:
        product_object = Product.objects.filter(name__icontains=item_name)
    paginator = Paginator(product_object, 12)
    # On récupère le numéro de page depuis l'URL (ex: site.com/boutique/?page=2)
    page_number = request.GET.get('page')
    # On récupère les produits de la page demandée
    product_object = paginator.get_page(page_number)
    return render(request, 'Mboa_ecom/index.html', {'product_object':product_object})

# id pour urls
def detail_view(request, my_id):
    # dictionary for initial data with field names as keys
    context ={}
    context["data"] = Product.objects.get(id = my_id)
    return render(request, "Mboa_ecom/detail.html", context)

def commander_view(request):
    if request.method == "POST":
        items = request.POST.get('items')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        adresse= request.POST.get('adresse')
        ville = request.POST.get('ville')
        region = request.POST.get('region')
        zip = request.POST.get('zip')
        total = request.POST.get('total')
        com = Commande(items=items,nom=nom, email=email, adresse=adresse, total=total, ville=ville, region=region, zip=zip)
        com.save()
        return redirect('confirmation')

    return render(request, "Mboa_ecom/commander.html")

def confirmation_view(request):
    # Récupère la toute dernière commande enregistrée
    derniere_commande = Commande.objects.order_by('-id').first()
    if derniere_commande:
        nom = derniere_commande.nom
    else:
        nom = "Client"
    return render(request, "Mboa_ecom/confirmation.html", {'name': nom})