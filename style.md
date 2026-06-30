# Documentation de Stylisation — AvenSu-Orienta (Course Platform)

## Table des Matières

1. [Structure du Projet](#structure-du-projet)
2. [Palette de Couleurs](#palette-de-couleurs)
3. [Typographie](#typographie)
4. [Fichiers CSS Statiques](#fichiers-css-statiques)
5. [Plugins et Librairies Externes](#plugins-et-librairies-externes)
6. [Composants Bootstrap Utilisés](#composants-bootstrap-utilisés)
7. [Transitions et Animations](#transitions-et-animations)
8. [Templates — Base et Composants Réutilisables](#templates--base-et-composants-réutilisables)
9. [Templates — Pages Authentification](#templates--pages-authentification)
10. [Templates — Page Accueil](#templates--page-accueil)
11. [Templates — Catalogue](#templates--catalogue)
12. [Templates — Communauté](#templates--communauté)
13. [Templates — Événements](#templates--événements)
14. [Templates — Orientation](#templates--orientation)
15. [Templates — Dashboard Étudiant](#templates--dashboard-étudiant)
16. [Templates — Dashboard Établissement](#templates--dashboard-établissement)
17. [Templates — Administration](#templates--administration)
18. [Responsive Design](#responsive-design)
19. [Accessibilité](#accessibilité)
20. [Récapitulatif Statistiques](#récapitulatif-statistiques)

---

## Structure du Projet

Le projet Django **AvenSu-Orienta** est une plateforme d'orientation scolaire au Togo composée de 7 applications :

| Application | Rôle |
|---|---|
| `accounts` | Authentification et gestion utilisateurs |
| `catalog` | Catalogue de formations, écoles et métiers |
| `orientation` | Tests RIASEC et coaching IA |
| `dashboard` | Carnet de bord étudiant et gestion établissement |
| `community` | Forum et discussions |
| `events` | Événements et salons |
| `administration` | Interface d'administration |

---

## Palette de Couleurs

| Rôle | Nom | Code Hex |
|---|---|---|
| Primaire / Accent | Or | `#ffb606` |
| Texte principal | Gris très foncé | `#1a1a1a` |
| Arrière-plan | Blanc | `#FFFFFF` |
| Bordures | Gris clair | `#ebebeb` |
| Texte secondaire | Gris moyen | `#707070` / `#888` / `#a5a5a5` |
| Danger / Erreur | Rouge | `#dc3545` |
| Succès | Vert | `#28a745` |
| Info | Bleu ciel | `#17a2b8` |
| Admin primaire | Bleu | `#4e73df` |
| Warning | Orange | `#f6c23e` |
| Fond secondaire | Gris très clair | `#f8f9fa` |
| Texte logo "Aven" | Bleu foncé | `#1b1ec9` |
| Fond dark (admin) | Noir | `#222` |
| Focus / Hover | Or léger | `#fffbef` / `#fffcf2` / `#fff2d1` |

**Gradient pages d'authentification :**
```css
linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)
```

---

## Typographie

### Polices chargées
- **Google Fonts** : Open Sans (400, 600, 700, 800) + Roboto (400, 500, 700)
- **Famille par défaut du `body`** : `Roboto, sans-serif`

### Tailles standard
| Élément | Taille | Poids |
|---|---|---|
| `h1` | 36px | 800 |
| `h2` | 22px | 700 |
| `h3` | 18px | 700 |
| `h4` | 14px | 700 |
| `h5` | 11px | 700 |
| `p` | 14px | 400 |
| Titres détail | 36px | 800 |
| Titres section | 24px | 700 |

### Règles globales
- `font-smoothing: antialiased` sur tous les éléments
- `text-decoration: none` par défaut sur les liens
- `line-height: 2.29` sur les paragraphes
- `letter-spacing: -0.5px` sur le logo

---

## Fichiers CSS Statiques

### `static/styles/bootstrap4/bootstrap.min.css`
Framework Bootstrap 4 minifié complet.

---

### `static/styles/main_styles.css`
Styles génériques du site (~300+ lignes).

```css
/* Éléments couverts */
body, p, h1-h6          /* Reset et base */
.header                 /* Navbar fixe */
.hamburger_container    /* Menu mobile */
.hero_slider            /* Slider accueil */
.hero_boxes             /* Boîtes SVG accueil */
.page_section           /* Sections génériques */
.footer                 /* Pied de page */
.trans_200/.trans_300   /* Classes de transition */
```

---

### `static/styles/responsive.css`
Breakpoints responsive pour tous les éléments. Adaptations mobile pour : header, navigation, cards/grilles, formulaires, sidebars.

---

### `static/styles/courses_styles.css`
Styles du catalogue de formations (~2000+ lignes).

```css
.unified_card           /* Carte formation */
.course_box             /* Boîte formation */
.unified_card_domain_badge  /* Badge domaine absolu */
/* Filtres, formulaires de recherche, grilles */
```

---

### `static/styles/news_styles.css`
Styles des pages forum/communauté (~2000+ lignes).

```css
/* Sidebar, colonnes latérales, cartes de contenu */
/* Commentaires, formulaires de réponse */
/* Sections réutilisables */
```

---

### `static/styles/news_post_styles.css`
Styles détaillés des posts individuels, commentaires et formulaires de réponse.

---

### `static/styles/elements_styles.css`
Composants génériques d'éléments réutilisables.

---

### `static/styles/teachers_styles.css`
Styles pour les cartes de profils et d'établissements.

---

### `static/styles/contact_styles.css`
Formulaires de contact et zones de saisie.

---

### `static/css/auth.css`

```css
.auth_page_container {
  /* gradient bleu, min-height: 80vh, flexbox center */
}
.auth_card {
  /* white, border-radius: 15px, flex-row, box-shadow: 15px */
}
.auth_form_side {
  /* padding: 50px, flex: 1 */
}
.auth_info_side {
  /* background: #ffb606, padding: 50px, width: 350px, flex-column */
}
.auth_title {
  /* font-size: 32px, font-weight: 800, color: #1a1a1a */
}
.auth_btn {
  /* background: #ffb606, color: #1a1a1a, font-weight: 700 */
  /* border-radius: 15px, text-transform: uppercase */
  /* :hover → background: noir, color: white */
}
.auth_link {
  /* color: #ffb606, font-weight: 700 */
}
```

---

### `static/css/custom.css`
Composants personnalisés principaux (~600 lignes).

```css
/* Champs de formulaire */
.input_field {
  height: 50px;
  border: 2px solid #ebebeb;
  background: white;
  padding-left: 20px;
  /* :focus → border-color: #ffb606 */
}
.text_field {
  height: 150px;
  padding-top: 15px;
}
.form_label, .filter_label {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
}

/* Conteneurs */
.filter_form_container {
  background: #f8f9fa;
  border-radius: 5px;
  box-shadow: rgba(0,0,0,0.08);
  margin-top: -50px;
  z-index: 10;
}
.dashboard_card {
  background: white;
  padding: 30px;
  border: 2px solid #ebebeb;
  border-radius: 5px;
  /* :hover → border-color: #ffb606 */
}
.admin_card {
  background: white;
  padding: 30px;
  border: 2px solid #ebebeb;
}

/* Sidebar */
.admin_sidebar_item {
  padding: 12px;
  background: white;
  border: 1px solid #ebebeb;
  border-left: 4px solid transparent;
  /* :hover → background: #fffbef, border-left: #ffb606, box-shadow */
  /* .active → même style que hover */
}
.admin_sidebar_item_danger {
  border-left-color: #dc3545;
  background: #fff8f8;
  /* :hover → background: #dc3545 */
}

/* Badges et statuts */
.status_badge {
  padding: 4px 12px;
  background: #ffb606;
  color: white;
  font-size: 12px;
  font-weight: 700;
  border-radius: 20px;
}

/* Kanban */
.kanban_column {
  min-height: 400px;
}

/* Boutons */
.comment_button {
  height: 48px;
  background: #ffb606;
  color: #1a1a1a;
  font-weight: 700;
}

/* Sidebar boxes */
.sidebar_box {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
}

/* Pages de détail */
.detail_container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: rgba(0,0,0,0.05);
}
.detail_title {
  font-size: 36px;
  font-weight: 800;
  color: #1a1a1a;
}
.detail_meta_item {
  display: flex;
  align-items: center;
  margin-right: 30px;
}
.detail_meta_icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff2d1;
  color: #ffb606;
  margin-right: 12px;
}
.detail_meta_label {
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 700;
  color: gray;
}
.detail_meta_value {
  font-size: 15px;
  color: #1a1a1a;
  font-weight: 600;
}
.detail_image_container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: rgba(0,0,0,0.1);
}
.detail_image {
  height: 450px;
  object-fit: cover;
}
.detail_section_title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  /* ::after → width: 50px, height: 3px, background: #ffb606 */
}

/* Cards unifiées */
.unified_card {
  border: none;
  box-shadow: rgba(0,0,0,0.06);
  border-radius: 8px;
  /* :hover → translateY(-5px), box-shadow augmenté */
}

/* Chat IA */
.chat_container {
  background: #f8f9fa;
  padding: 40px;
  border-radius: 5px;
  box-shadow: rgba(0,0,0,0.05);
}
.chat_window {
  height: 450px;
  overflow-y: auto;
  background: white;
  padding: 30px;
  border: 2px solid #ebebeb;
  margin-bottom: 30px;
}
.message_coach {
  background: #ffb606;
  color: white;
  padding: 15px 20px;
  border-radius: 20px 20px 20px 0;
  margin-bottom: 20px;
  max-width: 80%;
  box-shadow: rgba(255,182,6,0.2);
}
.message_user {
  background: #f1f1f1;
  color: #1a1a1a;
  padding: 15px 20px;
  border-radius: 20px 20px 0 20px;
  margin-bottom: 20px;
  margin-left: auto;
  max-width: 80%;
  text-align: right;
}

/* Résultats RIASEC */
.result_banner {
  background: #ffb606;
  padding: 60px;
  border-radius: 5px;
  color: white;
  margin-top: -80px;
  z-index: 10;
  box-shadow: rgba(0,0,0,0.1);
}

/* Notifications */
.notif_bell_btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0,0,0,0.12);
}
.notif_badge {
  background: #dc3545;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 10px;
  color: white;
}
.notif_card {
  background: white;
  border-left: 4px solid #ffb606;
  padding: 15px 20px;
  margin-bottom: 10px;
}

/* RIASEC Grid */
.riasec_grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}
.riasec_card {
  background: white;
  border: 2px solid #ebebeb;
  border-radius: 8px;
  padding: 20px 18px;
  width: 140px;
  text-align: center;
  /* :hover → border-color: #ffb606, box-shadow */
}

/* Options réponses */
.answer_option {
  display: block;
  background: white;
  border: 2px solid #ebebeb;
  padding: 15px 20px;
  margin-bottom: 12px;
  cursor: pointer;
  border-radius: 4px;
  /* :hover → border-color: #ffb606 */
  /* .active → border-color: #ffb606, background: #fffdf5 */
}
```

---

## Plugins et Librairies Externes

### OwlCarousel 2.2.1
```
CSS : static/plugins/OwlCarousel2-2.2.1/owl.carousel.css
      static/plugins/OwlCarousel2-2.2.1/owl.theme.default.css
      static/plugins/OwlCarousel2-2.2.1/animate.css
JS  : static/plugins/OwlCarousel2-2.2.1/owl.carousel.js

Utilisé pour : hero slider (3 slides), carousels formations
```

### FontAwesome 5.0.1
```
CSS : static/plugins/fontawesome-free-5.0.1/css/fontawesome-all.css

Classes utilisées (exemples) :
fa-user, fa-bell, fa-heart, fa-envelope, fa-map-marker-alt, fa-star,
fa-check-circle, fa-angle-left, fa-angle-right, fa-bars, fa-user-circle,
fa-user-clock, fa-file-download, fa-question-circle, fa-shield-alt,
fa-power-off, fa-trash, fa-edit, fa-plus, fa-search, fa-lock
```

### GreenSock (GSAP)
```
JS : static/plugins/greensock/TweenMax.min.js
     static/plugins/greensock/TimelineMax.min.js
     static/plugins/greensock/animation.gsap.min.js
     static/plugins/greensock/ScrollToPlugin.min.js

Utilisé pour : animations slides, transitions smooth, parallax
```

### ScrollMagic 1.2.0
```
JS : static/plugins/scrollmagic/ScrollMagic.min.js
     static/plugins/scrollmagic/animation.gsap.min.js

Utilisé pour : parallax scrolling, scroll triggers
```

### Parallax.js 2.0.0
```
JS : static/plugins/parallax.js-2.0.0/jquery.parallax.min.js

Utilisé pour : effets parallax sur backgrounds
```

### ProgressBar.js
```
JS : static/plugins/progressbar/progressbar.min.js

Utilisé pour : barres de progression du test RIASEC
```

### jQuery 3.2.1
```
JS : static/js/jquery-3.2.1.min.js

Utilisé pour : DOM manipulation, requêtes AJAX, event handling
```

### jQuery ScrollTo / Easing
```
JS : static/plugins/scrollTo/jquery.scrollTo.min.js
     static/plugins/easing/easing.js

Utilisé pour : smooth scroll, easing functions
```

### Themify Icons (Administration uniquement)
```
Icônes : ti-menu, ti-search, ti-bell, ti-user, ti-home, ti-book,
         ti-briefcase, ti-calendar, ti-check-box, ti-world, ti-dashboard,
         ti-pencil, ti-trash, ti-file, ti-check, ti-alert,
         ti-pie-chart, ti-comment-alt, ti-plus, ti-minus
```

### Chart.js (Administration uniquement)
```
CDN : https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js

Utilisé pour : graphique doughnut — distribution des rôles
Couleurs : ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
```

### Popper.js + Bootstrap 4 JS
```
JS : static/styles/bootstrap4/popper.js
     static/styles/bootstrap4/bootstrap.min.js

Utilisé pour : modals, dropdowns, alerts, tabs, collapsibles
```

---

## Composants Bootstrap Utilisés

| Composant | Classes |
|---|---|
| Grille | `container`, `row`, `col-lg-*`, `col-md-*`, `col-sm-*` |
| Cartes | `card`, `card-body`, `card-header`, `card-footer`, `card-title` |
| Badges | `badge`, `badge-primary/success/warning/danger/info/secondary/light` |
| Boutons | `btn`, `btn-primary/success/warning/danger/info`, `btn-sm`, `btn-outline-*` |
| Formulaires | `form-control`, `form-group`, `input-group`, `custom-control` |
| Alertes | `alert`, `alert-info/warning/danger/success` |
| Tableaux | `table`, `table-responsive`, `table-striped`, `table-hover` |
| Dropdowns | `dropdown`, `dropdown-menu`, `dropdown-item`, `dropdown-toggle` |
| Modals | `modal`, `modal-dialog`, `modal-content`, `modal-header/body/footer` |
| Navigation | `nav`, `nav-tabs`, `nav-link`, `nav-item` |
| Breadcrumb | `breadcrumb`, `breadcrumb-item` |
| Pagination | `pagination`, `page-item`, `page-link` |
| Flex | `d-flex`, `flex-row`, `flex-column`, `align-items-*`, `justify-content-*` |
| Espacement | `m-*`, `p-*`, `ml-*`, `mt-*`, `mb-*`, `mr-*` |
| Texte | `text-center/left/right`, `text-white`, `text-muted`, `text-danger` |
| Fond | `bg-primary/success/warning/danger/info/light/dark` |
| Affichage | `d-block`, `d-flex`, `d-none`, `d-sm-none`, `d-lg-block` |

---

## Transitions et Animations

### Classes de transition
```css
.trans_200 { transition: all 200ms ease; }
.trans_300 { transition: all 300ms ease; }
.trans_400 { transition: all 400ms ease; }
.trans_500 { transition: all 500ms ease; }
```

### Hover effects
- `.hvr-grow` : `transform: scale(1.05)` au hover
- Cards `.unified_card` : `translateY(-5px)` + box-shadow augmenté
- Boutons : changement background + shadow
- Liens : apparition underline + changement couleur

### Animations globales
- Hero slider : fade in/out (OwlCarousel + GSAP)
- Parallax scrolling sur les images hero (ScrollMagic)
- Barres de progression : `width` animé en `0.3s`
- Dropdowns Bootstrap : slide down/up natif

---

## Templates — Base et Composants Réutilisables

### `templates/base/base.html`

Structure HTML5 globale du site.

```html
<!-- Chargement CSS -->
Bootstrap 4, FontAwesome 5.0.1, OwlCarousel, main_styles, responsive, custom

<!-- Chargement JS -->
jQuery 3.2.1, Popper, Bootstrap JS, TweenMax, OwlCarousel, ScrollMagic

<!-- Structure DOM -->
<div class="super_container">
  {% include "components/header.html" %}
  {% include "components/mobile_menu.html" %}
  {% block content %}{% endblock %}
  {% include "components/footer.html" %}
</div>

<!-- Formulaire logout caché (déclenché par JS) -->
<form id="logout-form" method="post" action="{% url 'logout' %}" style="display:none;">
```

---

### `templates/components/header.html`

```css
.header {
  position: fixed;
  background: white;
  height: 100px;
  z-index: 9999;
}
.logo_container {
  /* img logo + span texte 30px color #3a3a3a */
}
.main_nav_item.active {
  /* style actif avec underline ou couleur or */
}
.header_side {
  width: 279px;
  background: #ffb606;
}
.btn_login_nav {
  border: 1px solid white;
  background: transparent;
  /* :hover → background: white */
}
.btn_register_nav {
  background: #1a1a1a;
  color: #ffb606;
  box-shadow: rgba(0,0,0,0.2);
}
.account_dropdown_nav {
  background: rgba(0,0,0,0.1);
  border-radius: 30px;
}
.notif_bell_btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0,0,0,0.12);
}
.notif_badge {
  background: #dc3545;
  position: absolute;
  top: -6px;
  right: -6px;
}
```

---

### `templates/components/footer.html`

```css
.footer {
  background: #222; /* ou #fff selon contexte */
}
.footer_content {
  /* row avec 4 colonnes */
}
.footer_col { padding: 30px; }
.footer_column_title {
  font-weight: 700;
  text-transform: uppercase;
}
.footer_bar {
  display: flex;
  justify-content: center;
  padding: 20px;
}
```

---

### `templates/components/logo.html`

```css
.logo_container {
  display: flex;
  align-items: center;
}
/* img : height: 40px, margin-right: 12px */
/* "Aven" → color: #1b1ec9 */
/* "Su"   → color: #ffb606 */
/* font-size: 22px, font-weight: 900, letter-spacing: -0.5px */
```

---

### `templates/components/mobile_menu.html`

```css
.menu_container.menu_mm {
  position: fixed;
  z-index: 100;
}
.menu_close_container { /* bouton fermeture */ }
.menu_social_container { /* icônes réseaux sociaux */ }
.menu_copyright { /* copyright texte */ }
```

---

### `templates/components/page_header.html`

```css
.home {
  /* section avec background-image */
}
.home_background_container { /* conteneur image */ }
.home_background {
  background-image: url(...);
  /* effet parallax */
}
.home_content {
  /* h1 en overlay sur image */
}
```

---

### `templates/components/pagination.html`

```css
.pagination_container {
  display: flex;
  justify-content: center;
}
.pagination_list {
  display: flex;
  gap: 8px;
}
.pagination_list li.active {
  /* fond or, texte blanc */
}
/* Navigation via AJAX */
```

---

### `templates/components/sidebar_account.html`

```css
.admin_sidebar_item {
  padding: 12px;
  background: white;
  border: 1px solid #ebebeb;
  border-left: 4px solid transparent;
  /* :hover et .active → background: #fffbef, border-left-color: #ffb606, box-shadow or */
}
.admin_sidebar_item_danger {
  border-left-color: #dc3545;
  background: #fff8f8;
  /* :hover → background: #dc3545, color: white */
}
/* Icônes FontAwesome (fas) */
/* Badge notification rouge circulaire */
```

---

### `templates/components/sidebar_profile.html`

```css
.sidebar_section {
  background: white;
  padding: 20px;
  border: 1px solid #ebebeb;
}
.testimonial_image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid #ffb606;
  object-fit: cover;
}
/* h4 : font-weight bold, mb-0 */
/* Badge rôle : badge badge-warning, font-size 10px */
```

---

### `templates/components/sidebar_representative.html`

Menu sidebar établissement (5 items). Même styling que `sidebar_account`.

---

### `templates/components/form_renderer.html`

```css
.form_group { margin-bottom: 20px; }
.form_label {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a1a;
  text-transform: uppercase;
}
.input_field {
  height: 50px;
  border: 2px solid #ebebeb;
  background: white;
  padding-left: 20px;
  /* :focus → border-color: #ffb606 */
}
.text_field { height: 150px; padding-top: 15px; }
.custom_radio_card { position: relative; }
.custom_radio_card input {
  position: absolute;
  opacity: 0; /* masqué */
}
.radio_card_label {
  border: 2px solid #ebebeb;
  background: white;
  border-radius: 8px;
  padding: 15px;
  /* :checked → border-color: #ffb606, background: #fffcf2, box-shadow jaune */
}
.radio_text {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 14px;
}
/* Erreurs : .alert.alert-danger p-2 small */
```

---

## Templates — Pages Authentification

### `templates/pages/accounts/login.html`

```
Layout : gradient bleu → .auth_card (flex-row) → .auth_form_side + .auth_info_side
```

```css
.auth_page_container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth_card {
  background: white;
  border-radius: 15px;
  display: flex;
  flex-direction: row;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}
.auth_form_side { padding: 50px; flex: 1; }
.auth_info_side {
  background: #ffb606;
  padding: 50px;
  width: 350px;
  display: flex;
  flex-direction: column;
}
/* Responsive → flex-direction: column sur mobile */
```

---

### `templates/pages/accounts/register.html`
Même layout que `login.html`. Formulaire `multipart/form-data` pour l'upload de fichiers.

---

### `templates/pages/accounts/password_reset_form.html`
### `templates/pages/accounts/password_reset_confirm.html`
### `templates/pages/accounts/password_reset_done.html`
### `templates/pages/accounts/password_reset_complete.html`
Même layout/styling que les pages auth. Formulaires de réinitialisation de mot de passe.

---

### `templates/pages/accounts/pending_approval.html`

```css
/* .page_section : container standard */
/* .dashboard_card centré, py-5 */
/* i.fa-user-clock.fa-5x : grand icône warning */
/* .alert.alert-info : message d'attente */
```

---

### `templates/pages/accounts/profile.html`

```
Layout : col-lg-8 (formulaire) + col-lg-4 (sidebar profil + compte)
```

```css
.profile_form_container {
  background: white;
  padding: 40px;
  border: 2px solid #ebebeb;
}
/* Inclut : form_renderer, sidebar_profile, sidebar_account */
/* Bouton sauvegarde : .comment_button (or) */
```

---

## Templates — Page Accueil

### `templates/pages/home.html`
Agrège 6 sections via `include` :

```
_hero_slider.html
_hero_boxes.html
_popular_courses.html
_register_search.html
_services.html
_events.html
```

---

### `templates/pages/home/_hero_slider.html`

```css
.hero_slider_container { width: 100%; }
.hero_slider { /* OwlCarousel */ }
.hero_slide {
  /* overlay sur background-image */
}
.hero_slide_container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}
.hero_slide_content {
  text-align: center;
  /* h1 span → color: #ffb606 */
  /* animations GSAP */
}
.hero_slider_nav {
  /* boutons prev/next absolus, trans_200 */
}
```

---

### `templates/pages/home/_hero_boxes.html`

```css
.hero_boxes {
  padding: 60px 0;
}
.hero_box {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.hero_box_col { /* col-lg-4 */ }
.hero_box_content { margin-left: 20px; }
.hero_box_title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}
.hero_box_link { color: #ffb606; font-weight: 700; }
/* Images SVG : earth-globe, books, professor */
```

---

### `templates/pages/home/_popular_courses.html`

```css
/* .page_section : background white */
/* .section_title : h1 text-center */
/* .row.course_boxes : grille col-lg-4 */
/* Réutilise .card.unified_card */
/* Card : image 200px | title | text | footer logo école */
```

---

### `templates/pages/home/_services.html`

```css
/* .services : .page_section */
/* .row.services_row : 6 colonnes col-lg-4 */
/* .service_item : text-left, flex-column */
/* .icon_container : flex-column, justify-content: flex-end */

/* Services : Catalogue | Test RIASEC | Forum | Experts | IA Coach | Suivi Post-BAC */
/* Images SVG par service */
```

---

### `templates/pages/home/_events.html`

```css
.event_item_unified {
  display: flex;
  flex-direction: row;
  border-radius: 8px;
}
.event_date_unified {
  background: #ffb606;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.event_day_unified {
  font-size: 24px;
  font-weight: 800;
}
.event_month_unified {
  font-size: 14px;
  text-transform: uppercase;
  font-weight: 700;
}
.event_body_unified {
  padding: 20px;
  flex-grow: 1;
}
.event_img_unified {
  width: 150px;
  height: 100%;
  object-fit: cover;
}
```

---

## Templates — Catalogue

### `templates/pages/catalog/formation_list.html`

```
Layout : .page_header (image) → .filter_form_container → .row.course_boxes
```

```css
.filter_form_container {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 5px;
  margin-top: -50px;
  z-index: 10;
  box-shadow: rgba(0,0,0,0.08);
}
/* Filtres : domaine (select), niveau (select) */
/* Bouton RECHERCHER : .comment_button (or) */
/* Chargement partiel via AJAX */
```

---

### `templates/pages/catalog/_formation_list_partial.html`

```css
/* Partiel AJAX rechargé dynamiquement */
.unified_card {
  border: none;
  box-shadow: 0 4px 15px rgba(0,0,0,0.06);
  border-radius: 8px;
  /* :hover → translateY(-5px), shadow augmenté */
}
/* Badge compatibilité : position absolute top-right, fond warning/success */
/* .unified_card_domain_badge : position absolute bottom-left, background: #ffb606 */
.unified_card_body {
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.unified_card_title {
  font-size: 18px;
  font-weight: 700;
}
.unified_card_text { font-size: 14px; color: #707070; }
.unified_card_footer {
  background: #f8f9fa;
  border-top: 1px solid #ebebeb;
}
/* .unified_price_box : logo école + badge location or */
```

---

### `templates/pages/catalog/formation_detail.html`

```
Layout : col-lg-8 (détail) + col-lg-4 (sidebar : actions + métiers liés)
```

```css
/* Réutilise .detail_container, .detail_title, .detail_meta_item, etc. */
/* .detail_section_title::after → 50px wide, 3px height, background: #ffb606 */
.detail_description {
  font-size: 16px;
  line-height: 1.8;
  color: #444;
}
/* Badges compétences : background: #ffb606, color: #1a1a1a */
/* Score compatibilité : badge success/warning/secondary selon % */
/* Sidebar : .sidebar_box + .comment_button pour actions */
```

---

### `templates/pages/catalog/school_list.html`
### `templates/pages/catalog/_school_list_partial.html`
### `templates/pages/catalog/school_detail.html`
Même structure et styling que les templates formation.

Filtres spécifiques : nom (input), ville (select), type public/privé (select).

---

### `templates/pages/catalog/metier_list.html`
### `templates/pages/catalog/_metier_list_partial.html`
### `templates/pages/catalog/metier_detail.html`
Même structure et styling que les templates formation.

Filtres spécifiques : mots-clés (input), secteur d'activité (select).

---

## Templates — Communauté

### `templates/pages/community/thread_list.html`

```
Layout : col-lg-8 (threads) + col-lg-4 (sidebar : recherche + filtre catégories)
```

```css
/* .sidebar_section_title h3 : font-weight 800, color #1a1a1a, font-size 20px */
.sidebar_box {
  background: white;
  border: 1px solid #ebebeb;
  padding: 20px;
  margin-top: 1rem;
}
/* Input search : width 100%, padding 10px, border: 1px solid #ebebeb */
/* Select catégories : padding 10px, border ebebeb */
/* Bouton : .comment_button (or) */
/* Chargement partiel via AJAX (_thread_list_partial.html) */
```

---

### `templates/pages/community/thread_detail.html`

```
Layout : col-lg-8 (discussion) + col-lg-4 (sidebar aide)
```

```css
.news_post_container { display: flex; flex-direction: column; }
.news_post_title { font-weight: 700; font-size: 24px; }
.news_post_meta { /* small, auteur + nombre de commentaires */ }
.news_post_text { font-size: 14px; line-height: 1.8; }
.comment_container { display: flex; flex-direction: row; }
.comment_image { width: 50px; height: 50px; border-radius: 50%; }
.comment_content { padding: 20px; }
.comment_name { font-weight: 700; }
.comment_date { font-size: small; color: gray; }
.leave_comment_title { font-size: 20px; font-weight: 700; }
/* .text_field : textarea 150px */
/* .comment_send_btn : or, trans_200 */
```

---

### `templates/pages/community/create_thread.html`
Formulaire de création de sujet. Réutilise `form_renderer` et `.comment_button`.

---

## Templates — Événements

### `templates/pages/events/event_list.html`

```
Layout : col-lg-8 (liste) + col-lg-4 (sidebar filtres + info box)
```

```css
/* Styles inline dans le template */
.event_filter_box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: rgba(0,0,0,0.05);
  border: 1px solid #ebebeb;
}
/* .form_label : 12px, bold, uppercase */
/* Input search : 15px margin-bottom */
/* Bouton : .comment_button (or) + trans_200, padding 12px */

/* Info box sidebar (dark) */
/* background: #1a1a1a, color: white, padding: 30px, border-radius: 12px */
/* .info_title : color #ffb606 */
/* Texte : color #ccc, font-size 14px, line-height 1.6 */
/* Link : text-warning, font-weight bold, small */

/* Chargement partiel via AJAX (_event_list_partial.html) */
```

---

## Templates — Orientation

### `templates/pages/orientation/test_intro.html`

```
Layout : col-lg-8 offset-lg-2 (centré)
```

```css
/* Styles inline dans le template */
.riasec_grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}
.riasec_card {
  background: white;
  border: 2px solid #ebebeb;
  border-radius: 8px;
  padding: 20px 18px;
  width: 140px;
  text-align: center;
  /* :hover → border-color: #ffb606, box-shadow rgba(0,0,0,0.08) */
}
/* .lettre : 30px, font-weight 900, color #ffb606 */
/* .nom    : 13px, font-weight 700, color #1a1a1a, margin-top 6px */
/* .exemple: 11px, color #888 */
.info_step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}
.step_num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ffb606;
  color: white;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
/* CTA : .comment_button "COMMENCER LE TEST" */
```

**Profils RIASEC affichés :** R – I – A – S – E – C (6 cartes)

---

### `templates/pages/orientation/test_question.html`

```
Layout : col-lg-8 offset-lg-2 (centré)
```

```css
/* Styles inline dans le template */
.question_card {
  background: white;
  border: 1px solid #ebebeb;
  border-radius: 6px;
  padding: 25px 30px;
  margin-bottom: 30px;
  box-shadow: rgba(0,0,0,0.04);
}
.question_title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 18px;
  line-height: 1.5;
}
.riasec_badge {
  display: inline-block;
  background: #ffb606;
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  margin-left: 8px;
}
.answer_option {
  display: block;
  background: white;
  border: 2px solid #ebebeb;
  padding: 15px 20px;
  margin-bottom: 12px;
  cursor: pointer;
  border-radius: 4px;
  /* :hover → border-color: #ffb606 */
  /* .active → border-color: #ffb606, background: #fffdf5 */
}
.progress_bar_container {
  background: #f0f0f0;
  border-radius: 20px;
  height: 6px;
  margin-bottom: 30px;
  overflow: hidden;
}
.progress_bar_fill {
  height: 6px;
  background: #ffb606;
  border-radius: 20px;
  transition: width 0.3s;
}
.question_counter { font-size: 13px; color: #888; margin-bottom: 8px; }
/* Bouton "VOIR MON PROFIL RIASEC" : .comment_button */
```

---

### `templates/pages/orientation/test_result.html`

```
Layout : col-lg-10 offset-lg-1 (centré)
```

```css
.result_banner {
  background: #ffb606;
  padding: 60px;
  border-radius: 5px;
  color: white;
  margin-top: -80px;
  z-index: 10;
  box-shadow: rgba(0,0,0,0.1);
}
.result_profile {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 10px;
  text-transform: uppercase;
}
/* Grille de recommandations formations avec match % */
/* Cards .unified_card avec badge compatibilité */
```

---

### `templates/pages/orientation/coach_chat.html`

```
Layout : col-lg-8 offset-lg-2 (centré)
```

```css
/* Réutilise .chat_container, .chat_window, .message_coach, .message_user */
/* .input_field pour saisie message */
/* Bouton ENVOYER : .comment_button (or) */
/* JS auto-scroll à la fin des messages */
```

---

## Templates — Dashboard Étudiant

### `templates/pages/dashboard/home.html`

```
Layout : col-lg-8 (contenu) + col-lg-4 (sidebar profil + compte)
```

**Section "Derniers Résultats" :**
```css
/* Affiche les tests passés : profil RIASEC, score, date */
/* .dashboard_card : white, border 2px ebebeb, 30px padding */
/* .status_badge : or, text blanc, border-radius 20px */
/* Link "consulter recommandations" → color: #ffb606 */
```

**Section "Suivi Démarches" (Kanban) :**
```css
.kanban_container { /* row flexbox */ }
.kanban_column { min-height: 400px; }
.kanban_header {
  background: #f0f0f0; /* ou bg-warning / bg-success selon colonne */
  padding: 2px;
  text-align: center;
  border-radius: 0;
  /* h5 : font-size 14px, font-weight bold */
}
.kanban_card {
  /* .dashboard_card avec padding 15px, margin-bottom 10px */
  /* border-left coloré selon statut */
  /* Dropdown Bootstrap pour changer statut */
}
/* 3 colonnes : À candidater (light) | Dossier envoyé (warning) | Réponses (success/danger) */
/* Réorganisation via AJAX (sortable) */
```

**Section "Agenda & Événements" :**
```css
/* .dashboard_card avec border-left: 5px solid #17a2b8 */
.event_date { font-size: 20px; font-weight: 700; }
/* Bouton "Rejoindre" : btn-outline-info (online) */
/* Badge "Présentiel" : badge-secondary (physique) */
```

---

## Templates — Dashboard Établissement

### `templates/pages/dashboard/etablissement/home.html`

```
Layout : col-lg-4 (sidebar representative) + col-lg-8 (contenu admin)
```

```css
.admin_card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  border: 2px solid #ebebeb;
  margin-bottom: 20px;
}
.stat_number { font-size: 40px; font-weight: 700; }
/* .small.font-weight-bold.text-uppercase : label statistique */
/* Tables Bootstrap standard */
```

---

### `templates/pages/dashboard/etablissement/formations_list.html`
Liste des formations de l'établissement. Tables Bootstrap + actions (éditer/supprimer).

---

### `templates/pages/dashboard/etablissement/formation_form.html`
Formulaire ajout/édition formation. Réutilise `form_renderer`.

---

## Templates — Administration

### `templates/administration/base_admin.html`

Framework : **SIQTheme** (thème custom dark).

```html
<!-- Chargement CSS -->
static/siqtheme/css/siqtheme.css

<!-- Body class -->
<body class="theme-dark">
```

```css
/* Layout CSS Grid */
.grid-wrapper.sidebar-bg.bg1 { /* conteneur principal */ }

.header {
  position: fixed;
  width: 100%;
  /* dark background, white text */
  z-index: très haut;
}
.brand { /* logo "AvenSu (or) Admin" */ }
.btn-toggle { /* hamburger mobile */ }

#sidebar {
  position: fixed;
  left: 0;
  /* dark theme */
}
.sidebar-menu { /* ul items avec hover */ }
.header-menu { /* sections headers */ }
/* .active : item actif surligné */

.main { /* main content area, à droite du sidebar */ }
/* Breadcrumb Bootstrap */
/* Messages Django → alerts Bootstrap */
/* {% block content %} */

.footer { text-align: center; }
#sidebar-right { /* panel droit utilisateur */ }
```

---

### `templates/administration/dashboard.html`

```css
/* Cards statistiques */
.card.bg-primary    { /* Utilisateurs */ }
.card.bg-success    { /* Formations */ }
.card.bg-info       { /* Établissements */ }
.card.bg-warning    { /* Événements */ }
/* Custom purple */
.card { background: #6f42c1; /* Métiers */ }

/* .card-body : display flex, justify-content: space-between */
/* i.ti-*.fa-3x : grandes icônes à droite */
/* .hvr-grow : effet zoom au hover */
/* .text-white : texte blanc sur fonds colorés */

/* Tableau utilisateurs en attente */
/* .table-hover + .badge.badge-secondary (rôle) */
/* Bouton Approuver : btn-success */

/* Graphique Chart.js (doughnut) */
/* Couleurs : ['#4e73df','#1cc88a','#36b9cc','#f6c23e','#e74a3b'] */
```

---

### `templates/administration/catalog/formation_list.html`

```css
.card { background: white; box-shadow: rgba(0,0,0,0.1); }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
/* Bouton Ajouter : btn btn-primary */
/* .table-responsive + .table.table-striped */
/* Images : height 40px */
/* Actions : btn-sm btn-info (ti-pencil) | btn-sm btn-danger (ti-trash) */
```

---

### Autres templates administration

```
administration/metier_list.html          — Même structure que formation_list
administration/etablissement_list.html   — Même structure
administration/evenement_list.html       — Même structure
administration/gestion_utilisateurs.html — Table complète + actions
administration/catalog/metier_form.html  — Formulaire métier
administration/catalog/formation_form.html — Formulaire formation
administration/*_confirm_delete.html     — Pages confirmation suppression
administration/questions/               — Modération des questions forum
```

---

## Responsive Design

### Breakpoints Bootstrap
| Breakpoint | Classe | Taille écran |
|---|---|---|
| Extra small | `col-*` | < 576px |
| Small | `col-sm-*` | ≥ 576px |
| Medium | `col-md-*` | ≥ 768px |
| Large | `col-lg-*` | ≥ 992px |
| Extra large | `col-xl-*` | ≥ 1200px |

### Adaptations mobiles (`responsive.css`)
- Header : masquage de la nav principale → hamburger + `.menu_mm`
- Navigation : menu overlay plein écran
- Cards/grilles : passage en colonne unique
- Formulaires : input pleine largeur
- Sidebars : passage en `width: 100%` sous le contenu principal
- Auth card : `flex-direction: column` (form + info empilés)
- Hero slider : hauteur réduite, texte ajusté

---

## Accessibilité

```html
<!-- ARIA utilisés -->
aria-label="Notifications"     <!-- cloche notifications -->
aria-haspopup="true"           <!-- dropdowns -->
aria-expanded="false"          <!-- toggles -->
aria-labelledby="..."          <!-- dropdowns menus -->
```

- Navigation clavier supportée (Tab)
- Focus visible sur les champs (`:focus → border-color: #ffb606`)
- Boutons avec textes explicites ou `aria-label`

---

## Récapitulatif Statistiques

| Métrique | Valeur |
|---|---|
| Templates HTML | 60+ |
| Fichiers CSS statiques | 18+ |
| Lignes CSS totales | ~18 000+ |
| Fichiers JS personnalisés | 8 |
| Plugins JS externes | 10+ |
| Applications Django | 7 |
| Pages uniques | 50+ |
| Composants réutilisables | 15+ |
| Couleurs dans la palette | 12 |
| Composants Bootstrap utilisés | 17+ |

---

*Documentation générée le 2026-06-28 — Projet AvenSu-Orienta (PPE301)*
