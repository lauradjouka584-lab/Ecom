import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mboa_ecom.settings')
django.setup()

from Mboa_ecom.models import Category, Product

def run_seed():
    print("Début de l'insertion des données...")

    # 1. Création des Catégories
    categories_data = [
        "Électronique & Informatique",
        "Mode & Accessoires",
        "Smartphones & Tablettes",
        "Électricité & Éclairage",
        "Sports & Loisirs"
    ]

    cat_objs = {}
    for cat_name in categories_data:
        category, created = Category.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = category
        if created:
            print(f"Catégorie créée : {cat_name}")

    # 2. Liste des Produits à insérer
    produits = [
        # Électronique & Informatique
        {
            "name": "Ecouteurs Sans Fil Bluetooth 5.3",
            "description": "Écouteurs intra-auriculaires avec réduction de bruit active, autonomie de 24h et boîtier de charge sans fil.",
            "price": 18000.0,
            "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600",
            "category": cat_objs["Électronique & Informatique"]
        },
        {
            "name": "Clavier Mécanique RGB Gamer",
            "description": "Clavier mécanique rétroéclairé RGB avec switchs bleus réactifs, idéal pour la bureautique et le jeu vidéo.",
            "price": 25000.0,
            "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
            "category": cat_objs["Électronique & Informatique"]
        },
        {
            "name": "Souris Sans Fil Ergonomique",
            "description": "Souris optique rechargeables 2.4G silencieuse avec sensibilité réglable jusqu'à 1600 DPI.",
            "price": 8500.0,
            "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600",
            "category": cat_objs["Électronique & Informatique"]
        },
        {
            "name": "Support PC Portable Ventilation",
            "description": "Support réglable en aluminium avec 2 ventilateurs intégrés pour maintenir votre ordinateur au frais.",
            "price": 12000.0,
            "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600",
            "category": cat_objs["Électronique & Informatique"]
        },

        # Mode & Accessoires
        {
            "name": "Montre Homme Quartz Élégante",
            "description": "Montre-bracelet pour homme avec cadran noir, bracelet en cuir véritable et étanchéité 3 ATM.",
            "price": 22000.0,
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
            "category": cat_objs["Mode & Accessoires"]
        },
        {
            "name": "Sac à Dos Voyage Antivol USB",
            "description": "Sac à dos étanche pour ordinateur 15.6 pouces avec port de charge USB externe et bandes réfléchissantes.",
            "price": 16500.0,
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600",
            "category": cat_objs["Mode & Accessoires"]
        },
        {
            "name": "Lunettes de Soleil Polarise Homme/Femme",
            "description": "Protection UV400 optimale avec monture légère en alliage métallique ultra résistant.",
            "price": 9500.0,
            "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600",
            "category": cat_objs["Mode & Accessoires"]
        },

        # Smartphones & Tablettes
        {
            "name": "Support Smartphone Magnétique Voiture",
            "description": "Support universel à fixation rapide sur grille d'aération avec aimants haute puissance.",
            "price": 4500.0,
            "image": "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=600",
            "category": cat_objs["Smartphones & Tablettes"]
        },
        {
            "name": "Batterie Externe Power Bank 20000mAh",
            "description": "Chargeur portable ultra rapide avec double sortie USB et affichage LED du niveau de batterie.",
            "price": 17500.0,
            "image": "https://images.unsplash.com/photo-1609592424089-980f588c22dc?w=600",
            "category": cat_objs["Smartphones & Tablettes"]
        },
        {
            "name": "Trépied Ring Light avec Télécommande",
            "description": "Anneau lumineux LED avec trépied téléscopique et support téléphone pour photos et vidéos.",
            "price": 14000.0,
            "image": "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=600",
            "category": cat_objs["Smartphones & Tablettes"]
        },

        # Électricité & Éclairage
        {
            "name": "Ampoule LED Connectée WiFi RGB",
            "description": "Ampoule intelligente contrôlable à distance via smartphone, avec 16 millions de couleurs au choix.",
            "price": 7000.0,
            "image": "https://images.unsplash.com/photo-1550985616-10810253b84d?w=600",
            "category": cat_objs["Électricité & Éclairage"]
        },
        {
            "name": "Projecteur Solaire LED Extérieur 100W",
            "description": "Éclairage solaire autonome avec détecteur de mouvement et télécommande, résistant à la pluie (IP65).",
            "price": 28000.0,
            "image": "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=600",
            "category": cat_objs["Électricité & Éclairage"]
        },

        # Sports & Loisirs
        {
            "name": "Gourde Isotherme Inox 1L",
            "description": "Bouteille d'eau en acier inoxydable qui garde vos boissons froides pendant 24h ou chaudes pendant 12h.",
            "price": 8000.0,
            "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600",
            "category": cat_objs["Sports & Loisirs"]
        },
        {
            "name": "Tapis de Yoga Antidérapant 6mm",
            "description": "Tapis de gym confortable en matériau écologique TPE avec sangle de transport incluse.",
            "price": 13500.0,
            "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600",
            "category": cat_objs["Sports & Loisirs"]
        }
    ]

    # 3. Insertion dans la base de données
    created_count = 0
    for p in produits:
        obj, created = Product.objects.get_or_create(
            name=p["name"],
            defaults={
                "description": p["description"],
                "price": p["price"],
                "image": p["image"],
                "category": p["category"]
            }
        )
        if created:
            created_count += 1

    print(f"Terminé ! {created_count} nouveaux produits ont été ajoutés à votre base de données.")

if __name__ == '__main__':
    run_seed()