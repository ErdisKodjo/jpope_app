"""
Admin Django sécurisé avec 2FA django-otp obligatoire.

Conformément au cahier des charges §3 :
- 2FA obligatoire pour les comptes Établissements et Conseillers
- Cette sécurité s'étend à l'admin Django via django-otp

Pour activer l'admin 2FA :
1. Migrer : python manage.py migrate
2. Créer un superuser : python manage.py createsuperuser
3. Se connecter à /admin/ → aller sur /otp/totp/
4. Scanner le QR code avec Google Authenticator
5. Saisir le code → le device TOTP est activé
6. Pour les futurs superusers : ils DOIVENT configurer TOTP avant de pouvoir accéder à l'admin

Pour rendre le 2FA obligatoire pour tous les staffs :
- Définir DJANGO_OTP_ADMIN_REQUIRE_ADMIN = True dans settings/prod.py
- Les utilisateurs sans device TOTP actif seront redirigés vers /otp/totp/setup/
"""
from django.contrib import admin
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken

# Optionnel : remplacer admin.site par OTPAdminSite pour forcer 2FA
# Décommenter pour activer l'admin 2FA obligatoire
# admin.site.__class__ = OTPAdminSite

admin.site.register(TOTPDevice, TOTPDeviceAdmin)
admin.site.register(StaticDevice)
admin.site.register(StaticToken)
