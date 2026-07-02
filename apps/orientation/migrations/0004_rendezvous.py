import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orientation', '0003_demandeaccompagnement_messageaccompagnement_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RendezVous',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_rdv', models.DateTimeField(verbose_name='date et heure')),
                ('duree_minutes', models.PositiveIntegerField(default=30, verbose_name='durée (min)')),
                ('format', models.CharField(
                    choices=[('VISIO', 'Visioconférence'), ('PRESENTIEL', 'Présentiel'), ('TELEPHONE', 'Téléphone')],
                    default='VISIO', max_length=20, verbose_name='format',
                )),
                ('lien_visio', models.URLField(blank=True, verbose_name='lien visioconférence')),
                ('adresse', models.CharField(blank=True, max_length=300, verbose_name='adresse (présentiel)')),
                ('notes', models.TextField(blank=True, verbose_name='ordre du jour')),
                ('statut', models.CharField(
                    choices=[('PROPOSE', 'Proposé'), ('CONFIRME', 'Confirmé'), ('ANNULE', 'Annulé'), ('TERMINE', 'Terminé')],
                    db_index=True, default='PROPOSE', max_length=20, verbose_name='statut',
                )),
                ('motif_annulation', models.TextField(blank=True, verbose_name="motif d'annulation")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('demande', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rendez_vous',
                    to='orientation.demandeaccompagnement',
                    verbose_name='demande associée',
                )),
                ('propose_par', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rdv_proposes',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='proposé par',
                )),
            ],
            options={
                'verbose_name': 'rendez-vous',
                'verbose_name_plural': 'rendez-vous',
                'ordering': ['date_rdv'],
            },
        ),
        migrations.AddIndex(
            model_name='rendezvous',
            index=models.Index(fields=['demande', 'statut'], name='orient_rdv_demande_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='rendezvous',
            index=models.Index(fields=['date_rdv'], name='orient_rdv_date_idx'),
        ),
    ]
