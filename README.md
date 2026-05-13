# Free Space — Application Blog Django

Plateforme de blog complète construite avec **Django 6**, **MySQL** et **Tailwind CSS**.

## Fonctionnalités

- Création de posts avec catégories, tags, image mise en avant et statut brouillon/publié
- Slider de posts mis en avant sur la page d'accueil (Swiper.js)
- Commentaires imbriqués (une couche de réponses)
- J'aime / Je n'aime plus (AJAX, temps réel)
- Profils utilisateurs avec avatar et bio
- Recherche dans les titres et le contenu des posts
- Défilement infini sur la liste des articles

---

## Prérequis

- Python 3.10 ou supérieur
- MySQL 8.0 ou supérieur
- pip

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd <nom-du-repo>/blog
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données MySQL

Connectez-vous à MySQL puis exécutez :

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurer les accès à la base de données

Ouvrez `config/settings.py` et modifiez le bloc `DATABASES` avec vos informations :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog_db',
        'USER': 'root',        # ← votre utilisateur MySQL
        'PASSWORD': '',        # ← votre mot de passe MySQL
        'HOST': 'localhost',   # ← '127.0.0.1' si localhost ne fonctionne pas
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Créer un super-utilisateur (accès admin)

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur de développement

```bash
python manage.py runserver
```

Ouvrez votre navigateur sur **http://127.0.0.1:8000**

L'interface d'administration est disponible sur **http://127.0.0.1:8000/admin**

---

## Structure du projet

```
blog/
├── config/              # Paramètres, URLs racine, WSGI/ASGI
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── users/           # Modèle User personnalisé (avatar, bio, site web)
│   ├── posts/           # Modèles Post, Category, Tag + vues principales
│   ├── comments/        # Modèle Comment (réponses imbriquées)
│   └── likes/           # Endpoint toggle-like (JSON)
├── templates/           # Templates HTML (niveau projet)
│   ├── base.html
│   ├── components/      # _field.html, _post_card.html
│   ├── partials/        # _navbar.html, _footer.html
│   ├── posts/
│   ├── users/
│   └── registration/
└── static/
    ├── css/
    │   ├── style.css    # Variables CSS et styles de base
    │   └── enhance.css  # Couche UI améliorée
    └── js/
        ├── main.js      # Nav, toasts, toggle commentaires (toutes pages)
        └── index.js     # Slider Swiper + défilement infini (page d'accueil)
```

---

## Routes principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil (slider + grille d'articles) |
| `/blog/` | Tous les articles avec recherche |
| `/post/<slug>/` | Détail d'un article |
| `/post/new/` | Créer un article *(connexion requise)* |
| `/post/<slug>/edit/` | Modifier un article *(auteur uniquement)* |
| `/category/<slug>/` | Articles par catégorie |
| `/search/` | Résultats de recherche |
| `/users/register/` | Inscription |
| `/users/login/` | Connexion |
| `/users/profile/<username>/` | Profil public |
| `/users/profile/edit/` | Modifier son profil *(connexion requise)* |
| `/admin/` | Interface d'administration Django |

---

## Administration

Accédez à `/admin/` avec le compte super-utilisateur pour gérer les posts, catégories, tags, commentaires et utilisateurs.  
Pour qu'un post apparaisse dans le slider de la page d'accueil, cochez **"Is featured"** depuis l'admin.

---

## Lancer les tests

```bash
python manage.py test apps
```
