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

## Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/mehdiaichouch2002/free-space-blog.git
cd free-space-blog
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv
```

```bash
# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données MySQL

Connectez-vous à MySQL et exécutez :

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurer les accès à la base de données

Ouvrez `config/settings.py` et modifiez le bloc `DATABASES` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog_db',
        'USER': 'root',        # ← votre utilisateur MySQL
        'PASSWORD': '',        # ← votre mot de passe MySQL
        'HOST': 'localhost',   # ← ou '127.0.0.1'
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Charger les données d'exemple

```bash
python manage.py loaddata fixtures/sample_data.json
```

Cela crée automatiquement :

| Compte | Mot de passe | Rôle |
|--------|-------------|------|
| `admin` | `admin123` | Super-utilisateur (accès `/admin/`) |
| `alice` | `user123` | Utilisateur normal |
| `karim` | `user123` | Utilisateur normal |

Et charge : 4 catégories, 5 tags, 5 articles publiés + 1 brouillon, 6 commentaires, 6 likes.

### 8. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrez **http://127.0.0.1:8000** dans votre navigateur.  
L'interface d'administration est sur **http://127.0.0.1:8000/admin**.

---

## Structure du projet

```
blog/
├── config/              # Paramètres, URLs racine, WSGI/ASGI
├── apps/
│   ├── users/           # Modèle User personnalisé (avatar, bio, site web)
│   ├── posts/           # Modèles Post, Category, Tag + vues principales
│   ├── comments/        # Modèle Comment (réponses imbriquées)
│   └── likes/           # Endpoint toggle-like (JSON)
├── fixtures/
│   └── sample_data.json # Données d'exemple prêtes à charger
├── templates/           # Templates HTML (niveau projet)
└── static/              # CSS et JavaScript
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

## Lancer les tests

```bash
python manage.py test apps
```
