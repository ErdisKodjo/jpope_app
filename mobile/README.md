# AvenSU-Orienta Mobile — React Native (Expo)

Application mobile multiplateforme (iOS + Android) pour la plateforme d'orientation AvenSU-Orienta.
Communique avec l'API Django REST via JWT.

## Installation

```bash
cd mobile
npm install
npm start          # lance Expo Dev Server
# ou
npm run android    # émulateur Android
npm run ios        # simulateur iOS
```

## Architecture

```
mobile/
├── src/
│   ├── App.tsx                    # Point d'entrée + Provider racine
│   ├── navigation/                # React Navigation (Auth + Main stacks + Tabs)
│   ├── screens/                   # Écrans de l'app
│   │   ├── auth/                  # Login, Register, 2FA, Consent parental, OAuth
│   │   ├── dashboard/             # Dashboard étudiant/parent/établissement/conseiller
│   │   ├── catalog/               # Catalogue écoles + formations + simulateur admission + visites 3D
│   │   ├── orientation/           # Tests RIASEC + Ikigai + rapport combiné
│   │   ├── roadmap/               # Roadmap évolutive Collège/Lycée/Post-Bac
│   │   ├── library/               # Bibliothèque numérique
│   │   ├── community/             # Forum + messagerie + alumni + avis
│   │   ├── chatbot/               # AvenBot (chat IA)
│   │   ├── crm/                   # CRM établissement + campagnes marketing + leads
│   │   ├── rgpd/                  # Consentements + export + droit à l'oubli
│   │   └── profile/               # Profil utilisateur + abonnement + 2FA setup
│   ├── components/                # Composants réutilisables
│   ├── services/                  # API client (axios) + services métier
│   ├── store/                     # State management (Zustand)
│   ├── utils/                     # Helpers (format, validation, storage)
│   ├── theme/                     # Couleurs, typography, espacements
│   └── types/                     # Types TypeScript
├── assets/                        # Images, fonts, splash
├── app.json                       # Config Expo
├── package.json
└── tsconfig.json
```

## Configuration

L'URL de l'API est configurable dans `app.json` → `extra.apiBaseUrl`.
Pour un device physique en dev : utiliser l'IP LAN du serveur Django au lieu de `localhost`.

```json
"extra": {
  "apiBaseUrl": "http://192.168.1.50:8000/api/v1"
}
```

## Fonctionnalités

### Authentification
- Login email/mot de passe + 2FA TOTP
- Inscription avec choix de rôle (étudiant/parent/conseiller/établissement)
- Auth sociale Google + Apple (via WebBrowser + OAuth callback)
- Consentement parental pour mineurs (rattachement parent/tuteur)
- Reset password + vérification email

### Dashboard étudiant
- Progression roadmap (3 phases)
- Étapes à venir + jalons
- Vœux d'orientation + favoris
- Statistiques personnalisées

### Catalogue
- Recherche établissements/formations (filtres multi-critères)
- Fiche établissement avec visite virtuelle 3D (WebView Matterport/Sketchfab)
- Simulateur d'admissions prédictif (% chances)
- Comparateur de formations

### Orientation
- Tests RIASEC (Holland)
- Test Ikigai (4 piliers)
- Rapport combiné RIASEC × Ikigai
- Recommandations personnalisées

### Bibliothèque
- Catalogue de ressources (manuels, annales, cours prep)
- Filtres par matière, niveau, type
- Recommandations basées sur le profil
- Téléchargement avec check premium
- Favoris + votes

### Communauté
- Forum + threads + messages
- Messagerie privée
- Mentorat alumni ↔ étudiants
- Avis certifiés alumni sur établissements
- Sessions collectives conseiller

### Chatbot AvenBot
- Chat IA 24/7 (WebSocket)
- Suggestions de questions
- Historique de conversation

### CRM Établissement
- Pipeline de candidatures (kanban)
- Accepter / refuser / mettre en attente
- Campagnes marketing ciblées
- Leads qualifiés + facturation au lead
- Statistiques campagne (vues, clics, conversions)

### RGPD
- Liste des consentements
- Export de données personnelles (ZIP)
- Droit à l'oubli (anonymisation)
- Journal des accès

### Profil
- Édition des informations personnelles
- Setup 2FA (QR code + codes de secours)
- Abonnement Premium (Stripe + Flooz + TMoney)
- Comptes sociaux connectés

## Build de production

```bash
# Installer EAS CLI
npm install -g eas-cli

# Configurer le projet EAS
eas login
eas build:configure

# Build Android (APK)
eas build -p android --profile preview

# Build iOS
eas build -p ios --profile preview
```

## Stack technique

- **Expo SDK 52** + React Native 0.76
- **React Navigation 7** (Native Stack + Bottom Tabs)
- **Zustand** pour le state management (léger, pas de boilerplate)
- **Axios** pour les appels API
- **React Native Paper** (Material Design 3)
- **Expo SecureStore** pour le stockage sécurisé (tokens JWT)
- **TypeScript** strict mode
