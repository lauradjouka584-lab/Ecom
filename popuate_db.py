import os
import re
import time
import django
import requests

# --- Démarrer Django pour pouvoir utiliser tes modèles (Category, Product) ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecompro.settings')
django.setup()

from django.core.files.base import ContentFile   # sert à enregistrer une image dans l'ImageField
from Mboa_ecom.models import Category, Product

# --- TA CLÉ PIXABAY : remplace COLLE_TA_CLE_ICI par ta vraie clé ---
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "57863766-148ca226cbdd0433ccc8d9f7e")

# Dictionnaire de correction : certains mots-clés sont collés (ex: "powerbank").
# Pixabay comprend mieux "power bank", donc on les sépare ici.
QUERY_FIX = {
    "powerbank": "power bank", "frenchpress": "french press", "airfryer": "air fryer",
    # ... etc.
}
# Une erreur personnalisée, utilisée quand on envoie trop de requêtes à Pixabay
class RateLimitError(Exception):
    """Limite Pixabay atteinte (trop de requêtes)."""


def slugify(text):
    # Transforme un nom de produit en nom de fichier propre :
    # "Écouteurs Sans Fil" -> "couteurs-sans-fil"
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:50]


def build_query(keywords):
    # Prépare le texte de recherche.
    # "mechanical,keyboard" -> ["mechanical", "keyboard"]
    words = keywords.replace(",", " ").split()
    # Pour chaque mot : on prend sa correction s'il en a une (QUERY_FIX), sinon le mot tel quel
    return " ".join(QUERY_FIX.get(w, w) for w in words)


def find_image_url(keywords):
    """Demande à Pixabay le lien de la meilleure photo pour ce produit."""
    # Les paramètres de la recherche
    params = {
        "key": PIXABAY_API_KEY,           # ta clé
        "q": build_query(keywords),       # ce qu'on cherche
        "image_type": "photo",            # des photos seulement (pas de dessins)
        "per_page": 3,                    # on demande 3 résultats
        "safesearch": "true",             # exclut les images pour adultes
    }

    # On essaie 2 fois maximum
    for attempt in range(2):
        r = requests.get("https://pixabay.com/api/", params=params, timeout=25)
        if r.status_code == 429:          # 429 = "trop de requêtes"
            if attempt == 0:              # 1ère fois : on attend 60 secondes et on réessaie
                print("   (limite atteinte, pause de 60 secondes...)")
                time.sleep(60)
                continue
            raise RateLimitError()        # 2ème fois : on abandonne et on prévient
        break                             # pas d'erreur 429 : on sort de la boucle

    # Si la clé est fausse, on arrête tout avec un message clair
    if r.status_code in (400, 401, 403) and "key" in r.text.lower():
        raise SystemExit("Clé Pixabay invalide. Vérifie PIXABAY_API_KEY en haut du fichier.")
    # Autre erreur : pas d'image pour ce produit
    if r.status_code != 200:
        return None
    # Pixabay répond avec une liste "hits" (les photos trouvées)
    hits = r.json().get("hits", [])
    if not hits:                          # aucune photo trouvée
        return None
    # On prend la 1ère photo (la plus pertinente), en grande taille si possible
    return hits[0].get("largeImageURL") or hits[0].get("webformatURL")


def download(keywords):
    """Télécharge la photo et retourne son contenu, ou None si ça échoue."""
    try:
        url = find_image_url(keywords)    # 1) on récupère le lien de la photo
        if not url:
            return None
        # on télécharge la photo à partir de ce lien
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        # on vérifie que c'est bien une image (et pas une page d'erreur)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            return r.content              # le contenu de l'image
    except requests.RequestException:     # problème de connexion, timeout...
        pass
    return None         # échec : le script affichera "ÉCHEC image"

# (nom, description, prix FCFA, mots-clés image en anglais)
DATA = {
    "Électronique & High-Tech": [
        ("Écouteurs Sans Fil Bluetooth 5.3", "Réduction de bruit active, autonomie 24h avec boîtier de charge.", 15000, "earbuds"),
        ("Clavier Mécanique RGB Gamer", "Switchs bleus réactifs, rétroéclairage personnalisable et châssis alu.", 25000, "mechanical,keyboard"),
        ("Souris Sans Fil Ergonomique", "Silencieuse, batterie rechargeable 1600 DPI pour bureautique.", 8500, "computer,mouse"),
        ("Support PC Portable Aluminium", "Pliable et réglable sur 6 hauteurs pour une meilleure posture.", 12000, "laptop,stand"),
        ("Power Bank 20000mAh Charge Rapide", "Double sortie USB-C/USB-A avec affichage LED du niveau de batterie.", 18000, "powerbank"),
        ("Enceinte Portative Bluetooth Étanche", "Son à 360°, étanchéité IPX7, idéal pour l'extérieur.", 22000, "bluetooth,speaker"),
        ("Montre Connectée Smartwatch", "Suivi cardiaque, podomètre, notifications d'appels et étanche.", 30000, "smartwatch"),
        ("Webcam HD 1080p avec Micro", "Parfaite pour les visioconférences, cours en ligne et streaming.", 14000, "webcam"),
        ("Support Smartphone Magnétique Voiture", "Fixation sur grille d'aération avec aimants puissants N52.", 5000, "phone,holder"),
        ("Casque Audio Over-Ear Bluetooth", "Coussinets à mémoire de forme et autonomie record de 40 heures.", 28000, "headphones"),
        ("Clé USB 64 Go", "Vitesse USB 3.0, format compact avec capuchon métallique.", 6500, "usb,flash"),
        ("Disque Dur Externe 1 To", "Stockage portable USB 3.0, compatible PC et Mac.", 42000, "external,harddrive"),
        ("Câble USB-C Tressé 2m", "Nylon renforcé, charge rapide et transfert de données.", 3500, "usb,cable"),
        ("Chargeur Secteur Rapide 30W", "Prise murale compacte avec port USB-C Power Delivery.", 9000, "phone,charger"),
        ("Trépied Smartphone Flexible", "Pieds articulés, idéal pour photos, vidéos et lives.", 7000, "tripod"),
        ("Chargeur Solaire Portable", "Panneau solaire pliable, idéal en cas de coupure d'électricité.", 16000, "solar,charger"),
        ("Écouteurs Filaires Jack 3.5mm", "Son clair avec micro intégré et télécommande.", 2500, "wired,earphones"),
        ("Lecteur de Cartes SD USB", "Compatible SD et microSD, transfert rapide.", 3000, "sdcard"),
        ("Ampoule Connectée Wi-Fi RGB", "16 millions de couleurs, contrôle depuis le téléphone.", 7500, "lightbulb"),
        ("Ring Light 26cm avec Trépied", "Éclairage LED réglable pour selfies, TikTok et maquillage.", 14500, "ring,light"),
        ("Microphone Cravate Sans Fil", "Idéal pour interviews et vidéos, portée 20m.", 12500, "microphone"),
        ("Manette de Jeu Sans Fil", "Compatible PC et Android, batterie rechargeable.", 13500, "gamepad"),
        ("Télécommande Universelle TV", "Compatible la plupart des téléviseurs et décodeurs.", 3500, "remote,control"),
        ("Station de Charge Sans Fil 15W", "Charge par induction pour smartphones compatibles.", 11000, "wireless,charger"),
        ("Caméra de Surveillance Wi-Fi", "Vision nocturne, détection de mouvement, vue sur téléphone.", 24000, "security,camera"),
    ],
    "Mode & Accessoires": [
        ("Montre Homme Quartz Bracelet Cuir", "Cadran analogique minimaliste avec verre minéral anti-rayures.", 20000, "wristwatch"),
        ("Sac à Dos Voyage Antivol USB", "Compartiment pour ordinateur 15.6 pouces et tissu imperméable.", 17000, "backpack"),
        ("Lunettes de Soleil Polarisées UV400", "Monture rétro unisexe, verre traité contre les éblouissements.", 9000, "sunglasses"),
        ("Portefeuille Homme en Cuir Véritable", "Protection RFID intégrée contre le piratage des cartes bancaires.", 8500, "leather,wallet"),
        ("Sac à Main Femme Élégant", "Cuir synthétique de haute qualité avec bandoulière amovible.", 22000, "handbag"),
        ("Basket Streetwear Tendance", "Semelle amortissante, design moderne et confort respirant.", 25000, "sneakers"),
        ("Ceinture Homme en Cuir Noir", "Boucle métallique automatique et finition soignée.", 6000, "leather,belt"),
        ("Casquette Baseball Coton", "Réglable à l'arrière, visière précurvée, style classique.", 4500, "baseball,cap"),
        ("Écharpe Cachemire Unisex", "Douceur extrême et chaleur optimale pour les saisons fraîches.", 10000, "scarf"),
        ("Chapeau de Paille Été", "Protection solaire élégante avec ruban décoratif.", 7000, "straw,hat"),
        ("Chemise Homme Coton Slim", "Coupe ajustée, tissu respirant, idéale bureau et sorties.", 12000, "shirt,men"),
        ("Jean Slim Homme Stretch", "Denim confortable et résistant, coupe moderne.", 15000, "jeans"),
        ("Robe d'Été Femme Fleurie", "Tissu léger et fluide, parfaite pour les journées chaudes.", 14000, "summer,dress"),
        ("Cravate Soie Homme", "Finition soignée, motif classique pour cérémonies.", 5500, "necktie"),
        ("Gants d'Hiver Tactiles", "Doublure chaude, compatibles écran tactile.", 6500, "gloves"),
        ("Veste en Jean Homme", "Denim épais, coupe droite, style intemporel.", 18000, "denim,jacket"),
        ("T-shirt Coton Col Rond", "100% coton doux, plusieurs coloris disponibles.", 5000, "tshirt"),
        ("Sweat à Capuche Unisexe", "Molleton épais avec poche kangourou.", 13000, "hoodie"),
        ("Jupe Plissée Femme", "Taille élastique, tissu fluide et élégant.", 9500, "skirt"),
        ("Boucles d'Oreilles Dorées", "Plaquées or, hypoallergéniques, design moderne.", 4000, "earrings"),
        ("Collier Pendentif Argenté", "Chaîne fine avec pendentif élégant.", 5500, "necklace"),
        ("Bracelet Perles Homme", "Perles naturelles, élastique résistant.", 3500, "bracelet"),
        ("Sandales Plates Femme", "Semelle souple, confortables toute la journée.", 8500, "sandals"),
        ("Chaussettes de Sport (Lot de 6)", "Coton respirant, renforcées talon et orteils.", 4500, "socks"),
        ("Bonnet Tricoté Unisexe", "Maille douce, chaud et extensible.", 3500, "beanie"),
    ],
    "Maison & Électroménager": [
        ("Aspirateur Robot Intelligent", "Navigation cartographique, nettoyage programmable via application.", 85000, "robot,vacuum"),
        ("Blender / Mixeur 1000W", "Bol en verre 1.5L, idéal pour smoothies et glace pilée.", 24000, "blender"),
        ("Cafetière à Piston Inox 1L", "Conserve la chaleur, filtre double paroi en acier inoxydable.", 13000, "frenchpress"),
        ("Bouilloire Électrique Inox 1.7L", "Chauffe rapide, arrêt automatique à ébullition.", 11000, "electric,kettle"),
        ("Friteuse sans Huile (Air Fryer) 4L", "Cuisine saine, 8 programmes préenregistrés, écran tactile.", 45000, "airfryer"),
        ("Diffuseur d'Huiles Essentielles LED", "Humidificateur ultra-silencieux avec 7 couleurs de lumière.", 9500, "aroma,diffuser"),
        ("Lampe de Bureau LED Tactile", "Luminosité réglable, chargeur induction intégré pour smartphone.", 16000, "desk,lamp"),
        ("Ensemble de Casseroles Antiadhésives", "Lot de 3 poêles en aluminium forgé compatibles tous feux.", 32000, "cookware"),
        ("Balance de Cuisine Électronique", "Précision au gramme près, plateau inox facile à nettoyer.", 6500, "kitchen,scale"),
        ("Humidificateur d'Air Ultrasonique", "Réservoir de 2L, améliore la qualité de l'air ambiant.", 18000, "humidifier"),
        ("Fer à Repasser Vapeur", "Semelle céramique, jet de vapeur puissant, 2200W.", 14000, "clothes,iron"),
        ("Ventilateur Sur Pied Oscillant", "3 vitesses, hauteur réglable, silencieux.", 20000, "standing,fan"),
        ("Grille-Pain 2 Fentes", "7 niveaux de brunissage, ramasse-miettes amovible.", 12500, "toaster"),
        ("Set de Couteaux de Cuisine Inox", "6 pièces avec bloc en bois, lames affûtées.", 19000, "kitchen,knives"),
        ("Cuiseur à Riz Électrique 1.8L", "Maintien au chaud automatique, cuve antiadhésive.", 21000, "rice,cooker"),
        ("Tapis de Salon Moderne", "Poils doux, motif géométrique, 160x230cm.", 35000, "rug"),
        ("Coussins Décoratifs (Lot de 2)", "Housses déhoussables, tissu velours.", 9000, "cushion"),
        ("Rideaux Occultants (Paire)", "Bloquent la lumière, œillets métalliques.", 17000, "curtains"),
        ("Miroir Mural Rond", "Cadre métallique doré, 60cm de diamètre.", 15000, "wall,mirror"),
        ("Parure de Draps en Coton", "Drap housse, drap plat et 2 taies, 2 places.", 22000, "bed,sheets"),
        ("Oreiller à Mémoire de Forme", "Soutien de la nuque, housse lavable.", 10500, "pillow"),
        ("Poubelle Automatique 30L", "Ouverture par capteur, design moderne.", 26000, "trash,bin"),
        ("Étendoir à Linge Pliable", "Structure en acier, grande capacité de séchage.", 12500, "drying,rack"),
        ("Boîtes de Rangement (Lot de 3)", "Plastique résistant avec couvercle, empilables.", 11000, "storage,box"),
        ("Horloge Murale Silencieuse", "Mécanisme sans tic-tac, diamètre 30cm.", 8000, "wall,clock"),
    ],
    "Beauté & Cosmetique": [
        ("Sèche-Cheveux Professionnel 2200W", "Technologie ionique anti-frisottis avec 3 températures.", 21000, "hairdryer"),
        ("Lisseur à Cheveux en Céramique", "Montée en température rapide jusqu'à 230°C.", 17500, "hair,straightener"),
        ("Tondeuse à Barbe & Cheveux Rechargeable", "Lames en acier inoxydable avec 4 sabots de coupe.", 13000, "hair,clipper"),
        ("Brosse Nettoyante Visage Silicone", "Vibrations soniques pour désincruster les pores en douceur.", 8000, "facial,brush"),
        ("Sérum Hydratant Acide Hyaluronique", "Soin visage repulpant et anti-âge 30ml.", 12000, "face,serum"),
        ("Palette de Maquillage Ombres à Paupières", "18 teintes pigmentées mats et irisées.", 15000, "eyeshadow,palette"),
        ("Coffret Parfum Eau de Parfum 100ml", "Fragrance florale et boisée durable toute la journée.", 35000, "perfume"),
        ("Huile d'Argan Bio Purifiée", "Soin nourrissant pour cheveux, visage et corps 100ml.", 7500, "argan,oil"),
        ("Miroir LED Maquillage Orientable", "Éclairage réglable avec miroir grossissant x5.", 11000, "makeup,mirror"),
        ("Brosse à Dents Électrique Ultrasonique", "5 modes de nettoyage avec minuteur de 2 minutes.", 16000, "electric,toothbrush"),
        ("Vernis à Ongles Longue Tenue", "Coffret de 6 couleurs, séchage rapide.", 6500, "nailpolish"),
        ("Rouge à Lèvres Mat", "Texture velours, tenue 12h, teinte intense.", 5500, "lipstick"),
        ("Crème Hydratante Visage 50ml", "Hydratation 24h pour tous types de peau.", 9000, "face,cream"),
        ("Savon Naturel au Karité", "Savon artisanal doux, adapté aux peaux sensibles.", 2500, "handmade,soap"),
        ("Brosse à Cheveux Démêlante", "Poils souples, démêle sans casser les cheveux.", 4500, "hairbrush"),
        ("Gel Douche Parfumé 500ml", "Formule douce, parfum frais longue durée.", 3500, "shower,gel"),
        ("Shampoing Nourrissant 400ml", "Pour cheveux secs, enrichi en huiles naturelles.", 4500, "shampoo"),
        ("Beurre de Karité Pur 200g", "Non raffiné, hydrate peau et cheveux.", 5000, "shea,butter"),
        ("Crème Solaire SPF50 150ml", "Protection haute, résistante à l'eau.", 9500, "sunscreen"),
        ("Déodorant Roll-On Homme", "Protection 48h, sans alcool.", 2500, "deodorant"),
        ("Fond de Teint Liquide", "Couvrance modulable, fini naturel.", 8500, "foundation,makeup"),
        ("Mascara Volume Extrême", "Cils longs et volumineux, formule waterproof.", 5500, "mascara"),
        ("Pinceaux de Maquillage (Set de 12)", "Poils doux avec trousse de rangement.", 9500, "makeup,brushes"),
        ("Coupe-Ongles Inox", "Lame précise avec lime intégrée.", 1500, "nail,clipper"),
        ("Rasoir Électrique Homme", "Rechargeable, 3 têtes flottantes, lavable.", 19000, "electric,shaver"),
    ],
    "Sports & Loisirs": [
        ("Gourde Isotherme Inox 1L", "Garde au froid pendant 24h et au chaud pendant 12h.", 8000, "water,bottle"),
        ("Tapis de Yoga Antidérapant 6mm", "Matériau écologique TPE avec sangle de transport.", 13500, "yogamat"),
        ("Haltères Réglables Plastifiées 2x5kg", "Revêtement antidérapant idéal pour le fitness à la maison.", 19000, "dumbbells"),
        ("Corde à Sauter avec Compteur", "Roulements à billes rapides pour entraînement cardio.", 4500, "jumprope"),
        ("Élastiques de Musculation (Set de 5)", "Différents niveaux de résistance pour tout le corps.", 7500, "resistance,bands"),
        ("Sac de Sport Pliable 30L", "Compartiment séparé pour chaussures et poche étanche.", 11000, "gym,bag"),
        ("Pistolet de Massage Musculaire", "6 embouts interchangeables pour la récupération sportive.", 27000, "massage,gun"),
        ("Ballon de Football Officiel Taille 5", "Coutures renforcées pour une grande durabilité sur tous terrains.", 10000, "soccer,ball"),
        ("Brassard Smartphone Course à Pied", "Tissu respirant avec fenêtre tactile transparente.", 4000, "running,armband"),
        ("Lunettes de Natation Anti-Buée", "Protection UV et joint silicone étanche confortable.", 6000, "swimming,goggles"),
        ("Ballon de Basketball Taille 7", "Grip optimal, usage intérieur et extérieur.", 12000, "basketball"),
        ("Raquettes de Ping-Pong (Set de 2)", "Avec 3 balles, manche ergonomique.", 9000, "pingpong,paddle"),
        ("Casque de Vélo Réglable", "Léger, bien ventilé, ajustement par molette.", 15000, "bicycle,helmet"),
        ("Gants de Boxe 12 oz", "Rembourrage dense, fermeture velcro.", 17000, "boxing,gloves"),
        ("Tente de Camping 3 Places", "Montage rapide, imperméable, légère.", 38000, "camping,tent"),
        ("Chaussures de Running Homme", "Semelle amortissante, tige respirante.", 28000, "running,shoes"),
        ("Maillot de Football Domicile", "Tissu séchage rapide, coupe sport.", 9500, "football,jersey"),
        ("Raquettes de Badminton (Set de 2)", "Avec volants et housse de transport.", 11000, "badminton,racket"),
        ("Ballon de Volley-Ball", "Surface douce, idéal plage et salle.", 9000, "volleyball"),
        ("Sac de Frappe Boxe 80cm", "Cuir synthétique renforcé, avec chaîne de suspension.", 35000, "punching,bag"),
        ("Shaker Protéines 700ml", "Avec grille mélangeuse, étanche.", 3500, "protein,shaker"),
        ("Barre de Traction Porte", "Sans vis, supporte jusqu'à 120kg.", 14000, "pullup,bar"),
        ("Roue Abdominale Fitness", "Poignées antidérapantes avec tapis genoux.", 8500, "ab,wheel"),
        ("Canne à Pêche Télescopique", "2m70, légère et facile à transporter.", 12500, "fishing,rod"),
        ("Skateboard Complet 31 Pouces", "Planche en érable, roues rapides.", 25000, "skateboard"),
    ],
    "Informatique & Bureau": [
        ("Ordinateur Portable 15.6\" 8 Go / 256 Go", "Processeur rapide, idéal études et bureautique.", 280000, "laptop"),
        ("Écran PC 24 Pouces Full HD", "Dalle IPS, faible consommation, HDMI et VGA.", 95000, "computer,monitor"),
        ("Imprimante Multifonction Jet d'Encre", "Impression, scan et copie, connexion Wi-Fi.", 65000, "printer"),
        ("Tapis de Souris Gaming XXL", "Surface lisse, base antidérapante, bords cousus.", 6000, "mousepad"),
        ("Routeur Wi-Fi Double Bande", "Couverture étendue, 4 antennes, installation facile.", 28000, "wifi,router"),
        ("Hub USB 4 Ports", "Extension USB 3.0 compacte pour ordinateur portable.", 5500, "usb,hub"),
        ("Chaise de Bureau Ergonomique", "Dossier respirant, accoudoirs et hauteur réglables.", 55000, "office,chair"),
        ("Disque SSD 512 Go", "Démarrage rapide, lecture jusqu'à 550 Mo/s.", 38000, "ssd"),
        ("Calculatrice Scientifique", "240 fonctions, idéale pour lycée et BTS.", 9500, "scientific,calculator"),
        ("Agrafeuse de Bureau Métal", "Robuste, capacité 25 feuilles.", 3500, "stapler"),
        ("Tablette Tactile 10 Pouces", "Écran HD, 64 Go de stockage, double caméra.", 120000, "tablet"),
        ("Vidéoprojecteur Portable HD", "Idéal pour présentations et cinéma maison.", 110000, "projector"),
        ("Multiprise Parafoudre 6 Prises", "Protection contre les surtensions, câble 2m.", 8000, "power,strip"),
        ("Bureau Informatique en Bois", "Plateau spacieux avec tiroir de rangement.", 45000, "office,desk"),
        ("Clavier Sans Fil Compact", "Touches silencieuses, connexion USB 2.4GHz.", 9000, "wireless,keyboard"),
        ("Souris Gaming Filaire RGB", "6 boutons programmables, 7200 DPI.", 12000, "gaming,mouse"),
        ("Casque Micro USB Bureau", "Réduction de bruit du micro, idéal visioconférence.", 14500, "headset,microphone"),
        ("Carte Mémoire microSD 128 Go", "Classe 10, avec adaptateur SD.", 12000, "microsd"),
        ("Câble HDMI 3m Haute Vitesse", "Compatible 4K, connecteurs plaqués or.", 4000, "hdmi,cable"),
        ("Adaptateur USB-C vers HDMI", "Pour connecter un portable à un écran ou TV.", 8500, "usbc,adapter"),
        ("Onduleur 650VA", "Protège l'ordinateur des coupures de courant.", 40000, "power,supply"),
        ("Support Écran Bras Articulé", "Réglable en hauteur, fixation sur bureau.", 22000, "monitor,arm"),
        ("Sacoche Ordinateur 15 Pouces", "Rembourrée, avec bandoulière et poches.", 12500, "laptop,bag"),
        ("Refroidisseur PC Portable", "Double ventilateur silencieux, 5 hauteurs.", 11000, "laptop,cooler"),
    ],
    "Jouets & Enfants": [
        ("Blocs de Construction 500 Pièces", "Briques colorées compatibles, développe la créativité.", 15000, "building,blocks"),
        ("Poupée Mannequin avec Accessoires", "Poupée articulée avec robes et chaussures.", 8500, "doll"),
        ("Voiture Télécommandée Tout-Terrain", "Rechargeable, portée 50m, pneus crantés.", 18000, "rc,car"),
        ("Peluche Ourson Géant 80cm", "Douce et câline, idéale en cadeau.", 12000, "teddybear"),
        ("Puzzle 1000 Pièces Paysage", "Carton épais, image haute définition.", 7000, "jigsaw,puzzle"),
        ("Jeu de Société Famille", "De 2 à 6 joueurs, dès 8 ans.", 10000, "board,game"),
        ("Tableau Noir Enfant avec Craies", "Double face, support en bois.", 9500, "chalkboard"),
        ("Cartable Scolaire Enfant", "Bretelles rembourrées, plusieurs compartiments.", 11500, "school,backpack"),
        ("Jeu d'Échecs en Bois", "Plateau pliable avec pièces lestées.", 9000, "chess"),
        ("Tricycle Évolutif Bébé", "Poignée parentale, siège sécurisé.", 28000, "tricycle"),
        ("Xylophone Musical Enfant", "8 notes colorées avec 2 baguettes.", 5000, "xylophone"),
        ("Pâte à Modeler (Lot de 12 Pots)", "Couleurs vives, non toxique.", 4500, "playdough"),
        ("Cerf-Volant Multicolore", "Facile à piloter, avec 50m de fil.", 3500, "kite"),
        ("Ballons de Baudruche Fête (Lot de 100)", "Couleurs assorties pour anniversaires.", 3000, "party,balloons"),
        ("Kit de Dessin et Coloriage", "Crayons, feutres et cahier de coloriage.", 6000, "coloring,pencils"),
        ("Dinette Cuisine Enfant", "Ustensiles et aliments en plastique, jeu d'imitation.", 13500, "toy,kitchen"),
        ("Camion de Pompier Jouet", "Avec sirène et lumières, matière robuste.", 9000, "toy,truck"),
        ("Lot de Petites Voitures (x10)", "Voitures métalliques assorties.", 7500, "toy,cars"),
        ("Piano Électronique Enfant", "24 touches, mélodies intégrées.", 14500, "toy,piano"),
        ("Ballon de Plage Gonflable", "Grand format coloré, idéal piscine.", 2000, "beach,ball"),
        ("Hochet Bébé Coloré", "Matière sans danger, facile à saisir.", 2500, "baby,rattle"),
        ("Tapis d'Éveil Bébé", "Avec arches et jouets suspendus.", 19000, "baby,playmat"),
        ("Pistolet à Eau Grande Capacité", "Portée 8m, réservoir 600ml.", 3500, "water,gun"),
        ("Jeu de 54 Cartes Classique", "Cartes plastifiées durables.", 1500, "playing,cards"),
    ],
    "Auto & Moto": [
        ("Casque Moto Intégral", "Visière anti-rayures, homologué, doublure amovible.", 35000, "motorcycle,helmet"),
        ("Aspirateur Voiture Portable", "Puissante aspiration, branchement allume-cigare.", 12000, "car,vacuum"),
        ("Chargeur Allume-Cigare Double USB", "Charge rapide pour 2 appareils en même temps.", 4500, "car,charger"),
        ("Housse de Siège Auto Universelle", "Matière respirante, installation facile.", 15000, "car,seat,cover"),
        ("Cric Hydraulique 2 Tonnes", "Robuste, idéal pour changer une roue.", 25000, "car,jack"),
        ("Batterie Voiture 12V 60Ah", "Longue durée, démarrage fiable.", 60000, "car,battery"),
        ("Huile Moteur 5W30 (5L)", "Protection moteur, adaptée essence et diesel.", 22000, "motor,oil"),
        ("Tapis de Sol Voiture Caoutchouc", "Set de 4, antidérapants et lavables.", 13000, "car,floor,mat"),
        ("Dashcam Embarquée Full HD", "Enregistrement en boucle, vision nocturne.", 28000, "dashcam"),
        ("Balais d'Essuie-Glace (Paire)", "Caoutchouc silencieux, montage universel.", 6500, "windshield,wiper"),
        ("Gants de Moto Renforcés", "Protection des phalanges, doigts tactiles.", 11000, "motorcycle,gloves"),
        ("Antivol Cadenas Haute Sécurité", "Acier trempé, résiste aux coupes.", 9500, "padlock"),
        ("Pneu Moto 17 Pouces", "Bonne adhérence sur route sèche et mouillée.", 32000, "motorcycle,tire"),
        ("Support GPS / Navigation Voiture", "Ventouse renforcée, rotation 360°.", 7500, "gps,navigation"),
        ("Désodorisant Voiture (Lot de 3)", "Parfums frais, longue durée.", 2500, "airfreshener"),
        ("Kit de Nettoyage Auto", "Éponge, microfibres et shampoing auto.", 9500, "car,wash"),
        ("Lampe Torche LED Rechargeable", "Très lumineuse, 3 modes d'éclairage.", 6000, "flashlight"),
        ("Câbles de Démarrage Batterie", "2.5m, pinces renforcées, 500A.", 8500, "jumper,cables"),
        ("Triangle de Signalisation", "Obligatoire en voiture, pliable.", 3500, "warning,triangle"),
        ("Extincteur Voiture 1kg", "Poudre ABC, avec support de fixation.", 12000, "fire,extinguisher"),
        ("Pare-Soleil Pare-Brise", "Réfléchissant, protège l'intérieur de la chaleur.", 4500, "windshield,sunshade"),
        ("Caméra de Recul Voiture", "Vision nocturne, aide au stationnement.", 15000, "backup,camera"),
        ("Housse de Volant Cuir", "Antidérapante, universelle 38cm.", 5000, "steering,wheel,cover"),
        ("Manomètre Pression Pneus", "Digital, lecture rapide et précise.", 4000, "tire,gauge"),
    ],
    "Papeterie & Fournitures": [
        ("Cahier 200 Pages Grands Carreaux", "Couverture rigide, papier de qualité.", 1200, "notebook"),
        ("Stylos à Bille (Boîte de 50)", "Encre bleue fluide, pointe moyenne.", 3500, "ballpoint,pen"),
        ("Crayons de Couleur (Boîte de 24)", "Mines résistantes, couleurs vives.", 3000, "colored,pencils"),
        ("Surligneurs Fluo (Lot de 6)", "Pointe biseautée, encre fluo.", 2500, "highlighter"),
        ("Classeur à Levier A4", "Dos large, solide mécanisme.", 2000, "binder"),
        ("Agenda 2026 Journalier", "Couverture souple, une page par jour.", 4500, "planner"),
        ("Ciseaux de Bureau Inox", "Lames précises, poignée ergonomique.", 1500, "scissors"),
        ("Colle Bâton (Lot de 5)", "Colle sans solvant, forte adhérence.", 1800, "glue,stick"),
        ("Règle Métallique 30cm", "Graduée, antidérapante.", 1000, "ruler"),
        ("Taille-Crayon Métal", "Lame en acier, pour crayons standards.", 500, "pencil,sharpener"),
        ("Gommes Blanches (Lot de 10)", "Effacent proprement sans abîmer le papier.", 1000, "eraser"),
        ("Ramette Papier A4 500 Feuilles", "80g/m², idéale impression et copie.", 3500, "paper"),
        ("Notes Autocollantes Colorées", "Lot de 12 blocs, adhésif repositionnable.", 2500, "sticky,notes"),
        ("Trombones (Boîte de 100)", "Acier galvanisé, anti-rouille.", 600, "paperclips"),
        ("Marqueurs Tableau Blanc (Lot de 4)", "Effaçables à sec, couleurs assorties.", 2500, "whiteboard,marker"),
        ("Tableau Blanc Magnétique 60x90", "Cadre aluminium avec plumier.", 18000, "whiteboard"),
        ("Carnet de Notes Spirale A5", "Reliure spirale, 100 pages.", 1500, "spiral,notebook"),
        ("Pochettes Plastiques Transparentes", "Lot de 100, perforées, format A4.", 3000, "document,folder"),
        ("Compas de Géométrie Métal", "Précis, avec mine de rechange.", 1800, "drawing,compass"),
        ("Set de Géométrie Complet", "Équerre, rapporteur, règle et compas.", 2500, "geometry,set"),
        ("Plastifieuse A4", "Chauffe rapide, avec 20 pochettes.", 24000, "laminator"),
        ("Perforatrice 2 Trous", "Capacité 30 feuilles, guide de réglage.", 4000, "hole,punch"),
        ("Peinture Acrylique (12 Tubes)", "Couleurs vives pour toile et papier.", 7500, "acrylic,paint"),
        ("Pinceaux de Peinture (Set de 15)", "Poils synthétiques de tailles variées.", 5500, "paintbrushes"),
        ("Dictionnaire Français Illustré", "Plus de 50 000 mots, format poche.", 8000, "dictionary,book"),
    ],
    "Jardin & Bricolage": [
        ("Arrosoir en Plastique 10L", "Pomme amovible, anse ergonomique.", 4000, "watering,can"),
        ("Tuyau d'Arrosage 15m", "Anti-vrilles, avec pistolet multi-jets.", 12000, "garden,hose"),
        ("Sécateur de Jardin", "Lames en acier, coupe nette jusqu'à 20mm.", 5500, "pruning,shears"),
        ("Gants de Jardinage Renforcés", "Paume enduite, respirants.", 2500, "gardening,gloves"),
        ("Pelle de Jardin", "Manche en bois, tête en acier trempé.", 6000, "garden,shovel"),
        ("Râteau de Jardin", "16 dents métalliques, manche solide.", 5500, "garden,rake"),
        ("Pots de Fleurs (Lot de 5)", "Plastique résistant avec soucoupes.", 7500, "flower,pots"),
        ("Terreau Universel 20L", "Riche en nutriments, pour plantes et potager.", 4500, "potting,soil"),
        ("Graines de Tomates (Sachet)", "Variété productive, facile à cultiver.", 1000, "tomato,seeds"),
        ("Brouette Jardin 100L", "Roue pneumatique, châssis renforcé.", 40000, "wheelbarrow"),
        ("Tondeuse à Gazon Électrique", "1200W, largeur de coupe 32cm.", 65000, "lawn,mower"),
        ("Perceuse Sans Fil 18V", "2 batteries, mandrin auto-serrant.", 45000, "cordless,drill"),
        ("Boîte à Outils 100 Pièces", "Mallette complète pour la maison.", 28000, "toolbox"),
        ("Marteau Manche Fibre", "Tête acier forgé, 500g.", 4500, "hammer"),
        ("Jeu de Tournevis (24 Pièces)", "Embouts magnétiques interchangeables.", 7500, "screwdriver,set"),
        ("Clé à Molette 250mm", "Mâchoire réglable, acier chromé.", 5000, "adjustable,wrench"),
        ("Mètre Ruban 5m", "Boîtier robuste, ruban verrouillable.", 2000, "tape,measure"),
        ("Niveau à Bulle 40cm", "Aluminium, 3 fioles de précision.", 4000, "spirit,level"),
        ("Scie à Main Universelle", "Lame trempée pour bois et plastique.", 4500, "hand,saw"),
        ("Échelle Pliante Aluminium", "4 marches, légère et stable.", 38000, "folding,ladder"),
        ("Serrure de Porte avec Clés", "Acier renforcé, installation facile.", 9500, "door,lock"),
        ("Lampe Solaire de Jardin (Lot de 4)", "S'allume automatiquement la nuit.", 12000, "solar,garden,light"),
        ("Pistolet à Colle Chaude", "Avec 10 bâtons de colle.", 5500, "glue,gun"),
        ("Rallonge Électrique 10m", "3 prises, câble renforcé.", 8500, "extension,cord"),
        ("Chaise de Jardin Pliante", "Structure acier, légère et confortable.", 15000, "garden,chair"),
    ],
}


def run_seed():
    if PIXABAY_API_KEY == "COLLE_TA_CLE_ICI":
        print("Colle d'abord ta clé Pixabay dans PIXABAY_API_KEY (en haut du fichier).")
        return

    total = sum(len(v) for v in DATA.values())
    print(f"Début : {total} produits à traiter...")

    ok, skipped, failed = 0, 0, 0
    n = 1

    try:
        for cat_name, items in DATA.items():
            category, _ = Category.objects.get_or_create(name=cat_name)

            for name, description, price, keywords in items:
                product, _ = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        "description": description,
                        "price": float(price),
                        "category": category,
                    },
                )

                # Saute si une vraie image est déjà enregistrée
                current = product.image.name if product.image else ""
                if current and not current.startswith("http"):
                    print(f"[{n}/{total}] déjà fait : {name}")
                    skipped += 1
                    n += 1
                    continue

                content = download(keywords)
                if content:
                    product.image.save(f"{slugify(name)}.jpg", ContentFile(content), save=True)
                    print(f"[{n}/{total}] OK : {name}")
                    ok += 1
                else:
                    product.image = None
                    product.save()
                    print(f"[{n}/{total}] ÉCHEC image : {name}")
                    failed += 1
                n += 1
                time.sleep(0.7)  # reste sous la limite de 100 requêtes/minute

    except RateLimitError:
        print("\nLimite Pixabay atteinte. Attends quelques minutes puis relance :")
        print("le script continue là où il s'est arrêté.")

    print(f"\nBilan : {ok} images ajoutées, {skipped} déjà présentes, {failed} échecs.")
    if failed:
        print("Relance le script pour réessayer les échecs.")


if __name__ == '__main__':
    run_seed()