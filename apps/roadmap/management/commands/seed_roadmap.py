"""Seed des étapes de roadmap par défaut (Collège / Lycée / Post-Bac)."""
from django.core.management.base import BaseCommand
from apps.roadmap.services import RoadmapSeedService


class Command(BaseCommand):
    help = "Crée ou met à jour les étapes de roadmap génériques par défaut."

    def handle(self, *args, **options):
        count = RoadmapSeedService.seed_etapes_par_defaut()
        self.stdout.write(self.style.SUCCESS(
            f"✓ {count} nouvelle(s) étape(s) créée(s). Total: 18 étapes (3 phases)."
        ))
