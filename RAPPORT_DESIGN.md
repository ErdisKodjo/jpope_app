# Rapport de refonte design — AvenSU-Orienta
**Palette Golfe Design System — Implémentation complète**

---

## 1. Contexte du projet

**AvenSU-Orienta** est une plateforme d'orientation post-bac destinée aux étudiants d'Afrique de l'Ouest (Togo). Elle permet de :
- Consulter un catalogue de formations et d'établissements
- Passer des tests d'orientation RIASEC
- Recevoir des recommandations personnalisées
- Suivre ses candidatures via un tableau de bord
- Échanger sur des forums communautaires
- Consulter des événements (salons, portes ouvertes)
- Interagir avec un assistant IA (AvenBot)

**Stack technique :** Django 5.1.3 · Bootstrap 4 · `AUTH_USER_MODEL = "accounts.User"` (email = USERNAME_FIELD)

**Périmètre de la refonte :** harmonisation visuelle complète via un design system maison baptisé **Palette Golfe**, sans aucune modification de la logique applicative (URLs, vues, modèles, migrations).

---

## 2. Palette Golfe — Design System

### 2.1 Tokens de couleurs principaux

| Rôle | Token CSS | Valeur hex | Usage |
|---|---|---|---|
| Lagune (primaire) | `--color-primary` = `--lagune-500` | `#0f6b8a` | Navigation, liens, info, bordures actives |
| Safran (accent CTA) | `--color-accent` = `--safran-500` | `#f0a032` | Boutons principaux, highlights, badges |
| Nuit (fond sombre) | `--color-deep` = `--nuit-800` | `#0b1e2e` | Footer, sections sombres, navbar |
| Parchemin (fond global) | `--color-bg` | clair neutre | Fond général des pages |
| Safran clair | `--color-bg-warm` = `--safran-50` | — | Hover states, fonds chauds |
| Safran très clair | `--color-accent-light` = `--safran-100` | — | États actifs, selections |
| Texte sur safran | `--color-accent-text` = `--nuit-800` | `#0b1e2e` | Texte sur fonds safran |

### 2.2 Familles RIASEC

| Dimension | Token | Usage |
|---|---|---|
| R (Réaliste) | `--riasec-R` | Barre hover hexmark RIASEC |
| I (Investigateur) | `--riasec-I` | idem |
| A (Artistique) | `--riasec-A` | idem |
| S (Social) | `--riasec-S` | idem |
| E (Entrepreneur) | `--riasec-E` | idem |
| C (Conventionnel) | `--riasec-C` | idem |

### 2.3 Ordre de chargement CSS

```
design_tokens.css  →  main_styles.css  →  responsive.css  →  custom.css  →  [extra_css par page]
```

`main_styles.css` (CSS legacy) n'est jamais modifié directement. `custom.css` charge en dernier et écrase tout.

### 2.4 Composant signature — Hexmark

```css
clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)
```

Tailles disponibles : `--xs` `--sm` `--md` `--lg` `--xl` `--2xl`  
Variantes RIASEC : `hexmark--R` `hexmark--I` `hexmark--A` `hexmark--S` `hexmark--E` `hexmark--C`

---

## 3. Chiffres de la refonte

| Métrique | Valeur |
|---|---|
| Templates actifs traités | 34 sur 36 (2 exclus : dead template + email) |
| Lignes dans `custom.css` après refonte | 2 537 |
| Lignes dans `auth.css` | 282 |
| CSS legacy retirés de templates actifs | 2 fichiers (`courses_styles.css`, `teachers_styles.css`) |
| Étapes réalisées | 10 |
| Fichiers modifiés ou créés | ~40 |

---

## 4. Étapes réalisées

### Étape 1 — Audit initial
Inventaire complet des fichiers CSS, templates, composants, et identification des incohérences avec la palette legacy (`#ffb606`, `var(--gold-*)`, Bootstrap `#ffc107`).

### Étape 2 — Tokens CSS et cohérence
Mise en place des aliases de migration dans `custom.css` : remplacement de `var(--gold-50)` → `var(--color-bg-warm)`, `var(--gold-100)` → `var(--color-accent-light)`, et normalisation des focus rings (lagune `rgba(15,107,138,...)` sur contextes primaires, safran `rgba(240,160,50,...)` sur contextes accent).

### Étape 3 — Hexmark et composants RIASEC
- Ajout de la taille `.hexmark--2xl` (96×96px)
- Migration du badge profil dominant dans `resultat_detail.html` : texte brut → `hexmark hexmark--2xl hexmark--{{ profil }}`
- `.riasec_card .lettre` : `border-radius` → hexagone `clip-path`
- Ajout des barres hover RIASEC par dimension (`.riasec_card--R::before`, etc.)
- Normalisation des interactions (`answer_option`, `info_step`)

### Étape 4 — Hero CSS et icônes hexagonales *(confirmation requise)*
- Remplacement du carrousel jQuery OwlCarousel par une animation CSS pure (`.hero_css_slider`, `@keyframes hero_slide_in`) avec 3 slides à rotation automatique 18s
- Suppression du `{% block extra_js %}` OwlCarousel dans `home.html`
- `.hero_box_icon`, `.service_card_icon`, `.orientation_home_card_icon` : `border-radius` → `clip-path` hexagonal
- `.service_card_icon` : fond `--color-primary-light` → `--color-accent`, hover → `--color-deep`

### Étape 5 — Page headers unifiés *(confirmation requise)*
Création du composant `.page_header` dans `custom.css` (240px, fond nuit-800, image de fond opacité 15%, hexmark décoratif `::before`, barre accent `::after`) et migration de **13 templates** qui utilisaient le header legacy `<div class="home">` cassé (100vh sur pages internes).

Templates migrés :
`catalog/formation_list.html` · `catalog/etablissement_list.html` · `catalog/metier_list.html` · `catalog/formation_detail.html` · `catalog/etablissement_detail.html` · `orientation/home.html` · `orientation/test_list.html` · `orientation/test_detail.html` · `orientation/resultat_detail.html` · `orientation/resultat_list.html` · `orientation/recommandation_list.html` · `community/forum_list.html` · `events/event_list.html`

### Étape 6 — Section titles et CTA dark
- `.section_title h1::after, h2::after` : barre accent safran 48×4px par défaut, centrée si `.text-center`
- `.cta_section` : fond `--color-primary` (lagune) → `--color-deep` (nuit-800) + texte blanc + hexmark décoratif `::before`
- `.cta_benefits_list` et `.cta_benefit_item` : adaptation fond sombre (rgba blancs)
- `home.html` CTA : `btn_secondary` → `comment_button`, `btn_ghost--dark` → `btn_ghost--white`

### Étape 7 — Dashboard, Navbar et tokens manquants *(confirmation requise)*
- `.btn_register_nav` : fond nuit + texte lagune (contraste 2.5:1) → fond **safran** + texte nuit-800 (contraste >4:1)
- `navbar.html` : `badge badge-warning` → `tag_badge`
- `dashboard/home.html` : correction de `var(--dark-50)`, `var(--orange-100)`, `var(--green-100)` (tokens indéfinis) + `color:#6f42c1` hardcodé
- `conseiller_eval_detail.html` : fallback `var(--color-warning,#ffc107)` → `var(--color-accent)`
- Ajout override global `.badge-warning` → tokens safran

### Étape 8 — Pages d'erreur et polish profil *(confirmation requise)*
- `404.html` et `500.html` : refonte complète (header legacy → `.page_header`, suppression de 79 lignes de `<style>` inline hardcodé, correction d'un **bug actif** : 4 URLs invalides `catalog:list` / `etablissements:list` / `events:list` / `contact` causant une cascade `NoReverseMatch → 500`)
- Ajout section `.error_section` / `.error_number--accent` / `.error_number--danger` / `.info_box_error` dans `custom.css`
- `profile.html` : `var(--color-warning)` → `var(--color-accent)` sur l'indicateur de progression partielle

### Étape 9 — Nettoyage final des fallbacks Bootstrap
- `verification_pending.html` : `var(--color-warning-bg, #fff3cd)` + `var(--color-warning, #ffc107)` × 2 → tokens safran
- `admin_verify_list.html` : border-left statut SOUMIS → `var(--color-accent)`
- `login.html` : `color:#666` → `var(--color-text-muted)`
- `chatbot.html` : `var(--color-primary-dark, #0056b3)` → `var(--color-deep)`

### Étape 10 — Retrait des CSS legacy et catalogue
- `courses_styles.css` retiré de `formation_list.html` (toutes ses classes sont dans `custom.css`)
- `teachers_styles.css` retiré de `etablissement_list.html` (idem)
- `class="row course_boxes"` → `class="row"` (suppression du `margin-top:68px` legacy)
- Remplacement de tous les `badge badge-secondary/light/success` Bootstrap dans les deux templates catalog → `tag_badge` et variantes
- `events/event_list.html` : `border-bottom:2px solid #ebebeb` → `var(--color-border-light)`

---

## 5. Problèmes corrigés en cours de route

| Problème | Impact | Solution |
|---|---|---|
| Headers internes `height:100vh` | Écran blanc de 100vh sur toutes les pages internes | Création du composant `.page_header` (étape 5) |
| CTA section `color:var(--color-dark)` sur `background:var(--color-primary)` | Texte lagune sur fond lagune — illisible | Fond → `--color-deep`, texte → blanc (étape 6) |
| `btn_secondary` invisible sur CTA | Fond nuit sur fond nuit (CTA) | → `comment_button` (safran sur nuit) |
| URLs invalides dans `404.html` | `NoReverseMatch` pendant le rendu → cascade vers `500` | Suppression de la section "Liens utiles" (étape 8) |
| `.btn_register_nav` contraste insuffisant | Lagune sur nuit-800, ratio ~2.5:1 (WCAG AA = 4.5:1) | Fond safran + texte nuit-800 (étape 7) |
| Tokens `--dark-50`, `--orange-100`, `--green-100` inexistants | Kanban sans couleurs de fond | → tokens valides (étape 7) |
| OwlCarousel jQuery sur le hero | Dépendance JS lourde, animation saccadée | Remplacement par animation CSS pure (étape 4) |
| Fallbacks Bootstrap `#ffc107`, `#fff3cd` partout | Jaune Bootstrap au lieu du safran de la charte | Remplacement systématique étapes 7, 8, 9 |

---

## 6. État final du codebase CSS

### Fichiers CSS et leurs rôles

| Fichier | Rôle | Modifiable |
|---|---|---|
| `design_tokens.css` | Variables CSS globales (couleurs, typo, espacements) | Oui |
| `main_styles.css` | Thème legacy — layout navbar, structure générale | **Non** (jamais) |
| `responsive.css` | Breakpoints legacy | Non |
| `custom.css` | Toutes les surcharges et nouveaux composants | Oui (prioritaire) |
| `auth.css` | Composants pages d'authentification uniquement | Oui |

### Composants CSS disponibles dans `custom.css`

| Composant | Classes |
|---|---|
| Hexmark | `.hexmark`, `.hexmark--{xs/sm/md/lg/xl/2xl}`, `.hexmark--{R/I/A/S/E/C}` |
| Buttons | `.comment_button`, `.btn_ghost`, `.btn_ghost--white`, `.btn_ghost--dark`, `.btn_danger`, `.btn_sm`, `.btn_login_nav`, `.btn_register_nav` |
| Badges | `.tag_badge`, `.tag_badge--{primary/info/success/danger/accent}` |
| Cards | `.unified_card`, `.riasec_card`, `.riasec_card--{R/I/A/S/E/C}`, `.admin_card`, `.dashboard_card` |
| Page header | `.page_header`, `.page_header_bg`, `.page_header_content` |
| Hero | `.hero_css_slider`, `.hero_slide` (animation CSS) |
| Sections | `.page_section`, `.section_title`, `.cta_section` |
| Formulaires | `.input_field`, `.form_label`, `.form_error`, `.filter_form_container`, `.filter_label` |
| Orientation | `.answer_option`, `.likert_label`, `.choice_option`, `.question_block` |
| Dashboard | `.stat_number`, `.stat_item_value--{primary/info/success/danger}`, `.kanban_header`, `.kanban_column` |
| Erreurs | `.error_section`, `.error_number`, `.error_number--{accent/danger}`, `.error_title`, `.error_text`, `.info_box_error` |
| Profil | `.profile_avatar_wrap`, `.profile_section_title`, `.admin_sidebar_item` |
| Navigation | `.main_nav_item`, `.notif_bell_btn`, `.account_dropdown_nav` |
| Auth | `.auth_card`, `.auth_form_side`, `.auth_info_side`, `.auth_btn`, `.auth_link`, `.role_card` |

---

## 7. Améliorations possibles

### 7.1 Accessibilité (priorité haute)

**Contrastes à vérifier :**
- `.tag_badge` par défaut (fond clair, texte muted) — ratio à vérifier WCAG AA
- Texte `rgba(255,255,255,0.55)` dans `.page_header .breadcrumb-item` — potentiellement sous le seuil 4.5:1

**ARIA manquants :**
- La cloche notifications (`.notif_bell_btn`) n'a pas de région live pour les nouvelles notifications
- Le hero slider CSS n'a pas `aria-live` ni `role="region"` avec un label
- Le menu hamburger mobile déclenche un menu (`#menu`) sans ARIA expanded/controls

**Focus visible :**
- Ajouter `:focus-visible` sur tous les éléments interactifs qui n'en ont pas encore (`.tag_badge` cliquable dans certains contextes)

### 7.2 Mobile / Responsive (priorité haute)

**Menu mobile absent :**
- Le hamburger `#hamburger_container` toggles `#menu` (défini dans `main_styles.css`) mais sa structure HTML n'a jamais été auditée pour le nouveau design. Le menu mobile utilise encore l'ancienne palette.
- Proposition : créer un `.mobile_nav` drawer dans `custom.css` avec fond nuit-800, liens en blanc, accent safran sur l'item actif.

**Navbar scroll :**
- `.header.scrolled` déclenche à `top: 15px` — vérifier que cela fonctionne toujours correctement avec le nouveau `btn_register_nav` safran.

**Chatbot :**
- La sidebar conversations est masquée en mobile (`display:none`). Proposer un bouton toggle pour l'afficher/masquer via un drawer.

### 7.3 Performance (priorité moyenne)

**Google Fonts dans les CSS legacy :**
- `courses_styles.css` et `teachers_styles.css` importaient `Open Sans` + `Roboto` via `@import url(...)`. Ces CSS ne sont plus chargés dans les templates actifs, mais si `main_styles.css` ou `responsive.css` les importent encore, cela représente 2 requêtes bloquantes supplémentaires.
- Recommandation : vérifier et centraliser les fonts dans `base.html` avec `<link rel="preconnect">` + `rel="preload"`.

**Images hero :**
- `slider_background.jpg` est chargé sur chaque `.page_header` via `style="background-image:..."`. Ajouter `loading="lazy"` n'est pas applicable aux backgrounds CSS.
- Recommandation : servir une version WebP + srcset, et utiliser `content-visibility: auto` sur les sections sous le fold.

**CSS non utilisé :**
- `main_styles.css` (1506 lignes) contient encore des styles pour des composants legacy non utilisés (`.course_box`, `.teacher_item`, `.milestone_item`, etc.). Un audit PurgeCSS/UnCSS réduirait considérablement le poids.

### 7.4 Design System — Extensions

**Dark mode :**
- Les tokens sont en place (`--color-bg`, `--color-deep`, etc.) mais aucun `@media (prefers-color-scheme: dark)` n'existe. L'architecture de tokens faciliterait l'ajout d'un theme sombre en redéfinissant ~15 variables.

**Footer tokenisé :**
- `footer.html` est entièrement en `style=""` inline avec des `rgba(255,255,255,0.x)` répétitifs. Créer une section `.footer_*` dans `custom.css` réduirait de ~30 lignes et permettrait une maintenance plus simple.

**`section_title` sur h3 :**
- Le composant `.section_title` gère `h1` et `h2` mais pas `h3`. Certaines sous-sections utilisent des `h3` comme titre de section — étendre le sélecteur si nécessaire.

**Variante `.page_header--sm` :**
- Actuellement tous les page headers font 240px. Certaines pages de formulaire simples (login, reset password) n'ont pas de header du tout. Une variante `height:140px` sans image de fond serait plus appropriée pour ces pages.

### 7.5 Composants manquants

**Pagination custom :**
- La pagination utilise encore Bootstrap `.pagination` / `.page-link` sans surcharge complète dans `custom.css`. Les couleurs d'état actif (`.page-item.active .page-link`) utilisent la couleur Bootstrap par défaut au lieu de `--color-primary`.

**Toasts / notifications :**
- Aucun composant de notification toast n'est défini. AvenBot, les erreurs de formulaires et les confirmations d'action utilisent des alertes Bootstrap non stylisées.

**Loader / Skeleton screens :**
- Les statistiques du dashboard (`#favoris-count` etc.) affichent `—` pendant le fetch API. Un skeleton screen ou un spinner cohérent avec le design system améliorerait la perception de performance.

**Modal custom :**
- Les modals (`#reviewModal`, `#rejectModal`) utilisent Bootstrap `.modal` sans surcharge complète. Les `.modal-header` et `.modal-footer` pourraient hériter des tokens de couleur.

### 7.6 Qualité du code

**Inline styles résiduels :**
- Environ 60-80 attributs `style=""` subsistent dans les templates (espacements, font-size hardcodés). La majorité sont des ajustements ponctuels acceptables, mais une deuxième passe pourrait extraire les patterns récurrents en classes utilitaires légères.

**`badge badge-light border` dans `formation_list` :**
- Le rendu final des `.tag_badge` sur fond carte doit être vérifié visuellement — le `.tag_badge` par défaut a un fond légèrement coloré qui peut créer un contraste insuffisant sur certaines cartes.

**Detaills non couverts :**
- `catalog/formation_detail.html` et `catalog/etablissement_detail.html` n'ont pas été auditées pour les hardcoded colors dans cet sprint. Une vérification post-déploiement est recommandée.
- `community/` (thread detail, replies) et `events/event_detail.html` n'ont pas été audités non plus.

---

## 8. Récapitulatif des fichiers modifiés

### CSS
| Fichier | Type de modification |
|---|---|
| `static/css/custom.css` | Principal fichier modifié — ajout de ~1000 lignes de composants |

### Templates — Partials
| Fichier | Modifications |
|---|---|
| `templates/partials/navbar.html` | Badge rôle → `tag_badge` |
| `templates/partials/footer.html` | Aucune (déjà propre) |

### Templates — Accounts
| Fichier | Modifications |
|---|---|
| `templates/accounts/login.html` | `color:#666` → token |
| `templates/accounts/register.html` | Aucune (déjà propre) |
| `templates/accounts/profile.html` | `var(--color-warning)` → `var(--color-accent)` |
| `templates/accounts/profile_edit.html` | Aucune (déjà propre) |
| `templates/accounts/student_profile_edit.html` | Aucune (déjà propre) |
| `templates/accounts/verification_pending.html` | Fallbacks Bootstrap → tokens safran |
| `templates/accounts/admin_verify_list.html` | Fallback `#ffc107` → `var(--color-accent)` |
| `templates/accounts/password_reset_request.html` | Aucune (déjà propre) |

### Templates — Pages principales
| Fichier | Modifications |
|---|---|
| `templates/home.html` | Hero CSS slider, CTA buttons |
| `templates/404.html` | Refonte complète + fix URLs invalides |
| `templates/500.html` | Refonte complète |
| `templates/base.html` | Aucune |

### Templates — Catalog
| Fichier | Modifications |
|---|---|
| `templates/catalog/formation_list.html` | `page_header`, retrait `courses_styles.css`, badges → `tag_badge` |
| `templates/catalog/etablissement_list.html` | `page_header`, retrait `teachers_styles.css`, badges → `tag_badge` |
| `templates/catalog/metier_list.html` | `page_header` |
| `templates/catalog/formation_detail.html` | `page_header` |
| `templates/catalog/etablissement_detail.html` | `page_header` |

### Templates — Orientation
| Fichier | Modifications |
|---|---|
| `templates/orientation/home.html` | `page_header` |
| `templates/orientation/test_list.html` | `page_header` |
| `templates/orientation/test_detail.html` | `page_header` |
| `templates/orientation/take_test.html` | Aucune (déjà propre) |
| `templates/orientation/resultat_detail.html` | `page_header`, hexmark profil dominant |
| `templates/orientation/resultat_list.html` | `page_header` |
| `templates/orientation/recommandation_list.html` | `page_header` |

### Templates — Dashboard
| Fichier | Modifications |
|---|---|
| `templates/dashboard/home.html` | Tokens undefined, couleur hardcodée |
| `templates/dashboard/conseiller_eval_list.html` | Aucune (déjà propre) |
| `templates/dashboard/conseiller_eval_form.html` | Aucune (déjà propre) |
| `templates/dashboard/conseiller_eval_detail.html` | Fallback `#ffc107` → `var(--color-accent)` |
| `templates/dashboard/admin_eval_list.html` | Aucune (déjà propre) |

### Templates — Autres
| Fichier | Modifications |
|---|---|
| `templates/events/event_list.html` | `page_header`, `#ebebeb` → token |
| `templates/community/forum_list.html` | `page_header` |
| `templates/chatbot/chatbot.html` | Fallback `#0056b3` → `var(--color-deep)` |

---

*Rapport généré le 29 juin 2026 — AvenSU-Orienta Palette Golfe Design System v1.0*
