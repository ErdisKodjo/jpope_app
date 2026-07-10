"""Management command pour initialiser les politiques de conservation RGPD par défaut."""
from django.core.management.base import BaseCommand
from apps.compliance.services import RGPDService


class Command(BaseCommand):
    help = "Crée ou met à jour les politiques de conservation RGPD par défaut."

    def handle(self, *args, **options):
        RGPDService.seed_politiques_par_defaut()
        self.stdout.write(self.style.SUCCESS(
            "✓ Politiques de conservation RGPD initialisées (8 catégories)."
        ))
