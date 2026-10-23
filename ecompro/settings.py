"""
Réglages (settings) du projet ecompro.
Ce fichier marche en LOCAL (ton PC) et sur HEROKU (en ligne).
Le code décide tout seul où il se trouve grâce aux "variables d'environnement".
"""

from pathlib import Path     # sert à manipuler les chemins de dossiers
import os                    # sert à lire les variables d'environnement (os.environ)
import dj_database_url       # transforme l'adresse de la base Heroku en réglage Django


# ==========================================================
# CHEMINS DU PROJET
# ==========================================================
# BASE_DIR = le dossier principal du projet (celui où se trouve manage.py).
# __file__ = ce fichier settings.py ; on remonte de 2 dossiers pour arriver à ECOM.
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates')


# ==========================================================
#SÉCURITÉ
# ==========================================================
# os.environ.get("NOM", "valeur par défaut") fonctionne ainsi :
#   - sur Heroku : il prend la valeur  définit avec "heroku config:set"
#   - en local   : la variable n'existe pas, prend la valeur par défaut

# SECRET_KEY : clé secrète de Django (signe les sessions, les cookies...).
# Sur Heroku,  une vraie clé secrète longue. 
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-cle-pour-le-local-seulement")

# DEBUG : mode développement.
# Ici : DEBUG vaut True seulement si la variable DEBUG est égale à "True".
DEBUG = os.environ.get("DEBUG", "True") == "True"

# ALLOWED_HOSTS : liste des adresses autorisées à ouvrir ton site.
# En local : 127.0.0.1 et localhost. Sur Heroku : nom-de-ton-app.herokuapp.com.
# .split(",") transforme "a,b" en liste ["a", "b"].
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost,.vercel.app").split(",")

# ==========================================================
#  APPLICATIONS INSTALLÉES
# ==========================================================
INSTALLED_APPS = [
    'django.contrib.admin',          # le site d'administration (/admin)
    'django.contrib.auth',           # gestion des utilisateurs et mots de passe
    'django.contrib.contenttypes',   # outil interne de Django pour les modèles
    'django.contrib.sessions',       # garde des infos de visite (sessions)
    'django.contrib.messages',       # messages "succès / erreur" affichés aux utilisateurs
    'django.contrib.staticfiles',    # gère les fichiers CSS, JS et images du site
    'Mboa_ecom',                     # TON application (produits, catégories, commandes)
    'django.contrib.postgres',       # fonctions avancées de PostgreSQL
]


# ==========================================================
#  MIDDLEWARE (étapes que chaque requête traverse, dans l'ordre)
# ==========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # règles de sécurité de base
    'whitenoise.middleware.WhiteNoiseMiddleware',               # affiche les CSS/JS sur Heroku (doit rester ici, juste après Security)
    'django.contrib.sessions.middleware.SessionMiddleware',     # active les sessions
    'django.middleware.common.CommonMiddleware',                # fonctions courantes (ex : ajoute le / final dans les URLs)
    'django.middleware.csrf.CsrfViewMiddleware',                # protège les formulaires (jeton CSRF)
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # sait quel utilisateur est connecté
    'django.contrib.messages.middleware.MessageMiddleware',     # active les messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # empêche d'afficher ton site dans un cadre piégé
]


# ==========================================================
#  URLS ET TEMPLATES
# ==========================================================
# Fichier principal des URLs (ecompro/urls.py).
ROOT_URLCONF = 'ecompro.urls'

# Réglages des templates (tes pages HTML).
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # moteur de templates de Django
        'DIRS': [TEMPLATES_DIRS],   # dossier supplémentaire où chercher les .html
        'APP_DIRS': True,           # cherche aussi dans le dossier "templates" de chaque application
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',            # permet d'utiliser "request" dans les templates
                'django.contrib.auth.context_processors.auth',           # permet d'utiliser "user" dans les templates
                'django.contrib.messages.context_processors.messages',   # permet d'afficher les messages
            ],
        },
    },
]

# Point d'entrée du serveur (utilisé par gunicorn sur Heroku : ecompro.wsgi).
WSGI_APPLICATION = 'ecompro.wsgi.application'


# ==========================================================
# BASE DE DONNÉES
# ==========================================================
# Heroku ajoute tout seul la variable DATABASE_URL quand tu installes Heroku Postgres.
if os.environ.get("DATABASE_URL"):
    # --- Cas HEROKU : on utilise la base PostgreSQL de Heroku ---
    DATABASES = {
        # dj_database_url lit DATABASE_URL et crée le réglage Django.
        # conn_max_age=600 : garde la connexion ouverte 10 min (plus rapide).
        # ssl_require=True : connexion chiffrée (exigée par Heroku).
        "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    # --- Cas LOCAL : ta base PostgreSQL sur ton PC ---
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',   # type de base : PostgreSQL
            'NAME': 'ecom_db',                           # nom de la base
            'USER': 'postgres',                          # utilisateur
            'PASSWORD': os.environ.get("DB_PASSWORD", ""),            
            'HOST': 'localhost',                         
            'PORT': '5432',                              # port standard de PostgreSQL
        }
    }


# ==========================================================
#  VALIDATION DES MOTS DE PASSE
# ==========================================================
# Règles pour créer un mot de passe (par exemple dans l'admin).
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # pas trop proche du nom d'utilisateur
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},            # longueur minimale (8 caractères)
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},           # refuse les mots de passe trop courants
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},          # refuse les mots de passe 100 % chiffres
]


# ==========================================================
#  LANGUE ET HEURE
# ==========================================================
LANGUAGE_CODE = 'fr-fr'   
TIME_ZONE = 'UTC'         
USE_I18N = True           # active la traduction
USE_TZ = True             # Django enregistre les dates avec le fuseau horaire


# ==========================================================
#  FICHIERS STATIQUES (CSS, JavaScript, style de l'admin)
# ==========================================================
# STATIC_URL : début de l'adresse des fichiers statiques (ex : /static/admin/...).
STATIC_URL = 'static/'

# STATIC_ROOT : dossier où "collectstatic" rassemble tous les fichiers statiques.
# Heroku lance cette commande tout seul au déploiement. Ce réglage est OBLIGATOIRE.
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==========================================================
#  IMAGES DES PRODUITS (media)
# ==========================================================
# MEDIA_URL : début de l'adresse des images envoyées (ex : /media/products/photo.jpg).
MEDIA_URL = '/media/'

# MEDIA_ROOT : dossier où les images sont enregistrées sur ton PC (en local).
MEDIA_ROOT = BASE_DIR / 'media'

# CLOUDINARY_URL est la variable qui contient la clé Cloudinary.
if os.environ.get("CLOUDINARY_URL"):
    # --- Cas HEROKU (ou local avec la clé) : les images vont sur Cloudinary ---
    INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.staticfiles'), 'cloudinary_storage')
    INSTALLED_APPS.append('cloudinary')
    STORAGES = {
        # "default" = où sont enregistrées les images des ImageField -> Cloudinary
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        # "staticfiles" = où sont les CSS/JS -> servis par WhiteNoise
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }
else:
    # --- Cas LOCAL sans clé Cloudinary : les images restent dans le dossier media ---
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }


# ==========================================================
#  HTTPS SUR HEROKU
# ==========================================================
# Heroku reçoit les visiteurs en HTTPS puis les envoie à ton app en HTTP.
# Cette ligne dit à Django : "si Heroku indique que c'était du HTTPS, fais-lui confiance".
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Liste des sites autorisés à envoyer des formulaires (protection CSRF).
# On crée "https://nom-de-ton-app.herokuapp.com" à partir de ALLOWED_HOSTS,
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]


# ==========================================================
#  EMAIL
# ==========================================================
# Les emails ne sont pas envoyés pour de vrai : ils s'affichent dans le terminal.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}