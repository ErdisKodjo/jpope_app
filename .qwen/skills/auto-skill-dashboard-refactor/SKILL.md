---
name: dashboard-refactor
description: Refactorisation du tableau de bord en services séparés et mise à jour des vues et templates
source: auto-skill
extracted_at: '2026-07-05T01:05:00.151Z'
---

## Contexte
Le tableau de bord affichait de nombreuses logiques métier directement dans les vues et les templates : calcul de scores, génération de recommandations, assignation de conseiller et visibilité des options. Cette approche rendait le code difficile à maintenir, à tester et à faire évoluer.

## Approche adoptée
1. **Création d’un paquet de services** sous `apps/dashboard/services` avec les modules :
   - `auth.py` : profilage limité du user pour le dashboard.
   - `score.py` : agrégation des résultats de tests.
   - `recommendation.py` : génération de recommandations basées sur le score.
   - `conseiller.py` : assignation et contrôle d’accès du conseiller.
   - `visibility.py` : filtrage d’options du UI selon le rôle et l’état.
2. **Refactorisation de `DashboardHomeView`** :
   - Import des services.
   - Mise à jour du `context` avec les nouvelles fonctions (`auth.get_dashboard_profile`, `score.calculate_test_score`, `recommendation.generate_recommendations`, `conseiller.assign_conseiller`).
   - Appel à `visibility.filter_options` pour préparer les drapeaux de visibilité.
3. **Mise à jour des templates** (`dashboard/home.html`) :
   - Remplacement des tests de rôle (`request.user.is_*`) par les drapeaux (`show_*`).
   - Ajout d’un bouton « Créer un vœu » conditionné par `show_create_voeu`.
4. **Ajout de tests unitaires** (`tests/dashboard/test_services.py`) couvrant chaque service et les cas d’accès.
5. **Gestion des dépendances de test** : désactivation de `debug_toolbar` dans les paramètres de test pour éviter `ModuleNotFoundError`.

## Bénéfices
- **Séparation des responsabilités** : logique métier isolée dans des services réutilisables.
- **Facilité de test** : chaque service possède ses propres tests unitaires.
- **Templates plus clairs** : les décisions d’affichage sont déterminées côté serveur et simplement exposées via des drapeaux.
- **Maintenance simplifiée** : les modifications futures (ex. nouveaux critères de recommandation) se font dans les services sans toucher aux vues ou aux templates.

## Procédure de réplication
1. Créer le répertoire `apps/dashboard/services` et les cinq modules ci‑dessus.
2. Implémenter les fonctions comme illustré dans le code du projet.
3. Modifier `DashboardHomeView.get_context_data` pour appeler les services et appliquer `visibility.filter_options`.
4. Adapter les templates en remplaçant les vérifications de rôle par les drapeaux `show_*`.
5. Ajouter des tests unitaires pour chaque service.
6. S’assurer que les paramètres de test excluent les applications non installées (ex. `debug_toolbar`).

Cette approche peut être réutilisée pour tout autre tableau de bord ou page présentant une logique métier lourde dans les vues.
