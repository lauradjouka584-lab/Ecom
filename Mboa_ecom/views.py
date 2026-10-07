from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Commande, Category

def index(request, category_id=None):
    # On récupère TOUTES les catégories pour que le menu déroulant fonctionne
    categories = Category.objects.all()
    selected_category = None
    #  On récupère tous les produits au départ
    products_list = Product.objects.all()
    # SI L'UTILISATEUR CLIQUE SUR UNE CATÉGORIE dans le menu déroulant
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products_list = products_list.filter(category=selected_category)

    #SI L'UTILISATEUR TAPE QUELQUE CHOSE DANS LA BARRE DE RECHERCHE (ex: "lunettes", "ballon")
    item_name = request.GET.get('item-name')
    if item_name and item_name.strip() != '':
        products_list = products_list.filter(name__icontains=item_name)

    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    product_object = paginator.get_page(page_number)

    context = {
        'product_object': product_object,       # Pour votre boucle de produits et pagination
        'categories': categories,               # Pour afficher la liste dans le menu déroulant
        'selected_category': selected_category, # Pour savoir quelle catégorie est active
    }
    return render(request, 'Mboa_ecom/index.html', context)


def detail_view(request, my_id):
    context = {}
    context["data"] = Product.objects.get(id=my_id)
    return render(request, "Mboa_ecom/detail.html", context)

def commander_view(request):
    if request.method == "POST":
        items = request.POST.get('items')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        ville = request.POST.get('ville')
        region = request.POST.get('region')
        zip = request.POST.get('zip')
        total = request.POST.get('total')
        com = Commande(items=items, nom=nom, email=email, adresse=adresse, total=total, ville=ville, region=region, zip=zip)
        com.save()
        return redirect('confirmation')

    return render(request, "Mboa_ecom/commander.html")

def confirmation_view(request):
    derniere_commande = Commande.objects.order_by('-id').first()
    if derniere_commande:
        nom = derniere_commande.nom
    else:
        nom = "Client"
    return render(request, "Mboa_ecom/confirmation.html", {'name': nom})