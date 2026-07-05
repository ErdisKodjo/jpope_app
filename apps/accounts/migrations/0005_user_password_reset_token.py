"""
Ajoute des champs séparés pour le token de réinitialisation de mot de passe.
Corrige le bug P1 : le token de vérification email et le token de reset
utilisaient le même champ, causant des conflits.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_counselorprofile_nombre_accompagnements_actifs_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password_reset_token",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="token de réinitialisation",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="password_reset_token_expires",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="expiration token reset",
            ),
        ),
    ]