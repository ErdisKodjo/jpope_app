"""
Tâches Celery pour l'app analytics.
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(queue="analytics")
def aggreger_stats_quotidiennes():
    """Agrège les statistiques de la veille."""
    from apps.analytics.models import DailyStats, PageView, ActionLog, SearchQuery

    hier = (timezone.now() - timedelta(days=1)).date()

    # Calculer les stats de la veille
    debut = timezone.datetime.combine(hier, timezone.datetime.min.time())
    fin = timezone.datetime.combine(hier, timezone.datetime.max.time())
    if timezone.is_aware(debut):
        pass
    else:
        import pytz
        tz = timezone.get_current_timezone()
        debut = tz.localize(debut)
        fin = tz.localize(fin)

    pages_vues = PageView.objects.filter(
        created_at__date=hier
    ).count()

    sessions_uniques = PageView.objects.filter(
        created_at__date=hier,
    ).values("session_key").distinct().count()

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        nouveaux_utilisateurs = User.objects.filter(
            date_joined__date=hier
        ).count()
    except Exception:
        nouveaux_utilisateurs = 0

    tests_demarres = ActionLog.objects.filter(
        created_at__date=hier,
        type_action="TEST_STARTED",
    ).count()
    tests_completes = ActionLog.objects.filter(
        created_at__date=hier,
        type_action="TEST_COMPLETED",
    ).count()

    formations_consultees = ActionLog.objects.filter(
        created_at__date=hier,
        type_action="FORMATION_VIEW",
    ).count()

    stats, created = DailyStats.objects.update_or_create(
        date=hier,
        defaults={
            "nouveaux_utilisateurs": nouveaux_utilisateurs,
            "pages_vues": pages_vues,
            "sessions_uniques": sessions_uniques,
            "tests_demarres": tests_demarres,
            "tests_completes": tests_completes,
            "formations_consultees": formations_consultees,
        },
    )

    action = "créées" if created else "mises à jour"
    logger.info(f"Stats quotidiennes {action} pour {hier}")
    return {
        "date": str(hier),
        "pages_vues": pages_vues,
        "nouveaux_utilisateurs": nouveaux_utilisateurs,
    }


@shared_task(queue="analytics")
def calculer_kpis_quotidiens():
    """Calcule les KPIs pour la veille."""
    from apps.analytics.models import KPIDefinition, KPISnapshot, DailyStats

    hier = (timezone.now() - timedelta(days=1)).date()

    try:
        stats = DailyStats.objects.get(date=hier)
    except DailyStats.DoesNotExist:
        logger.warning(f"Pas de DailyStats pour {hier}")
        return 0

    kpis = KPIDefinition.objects.filter(is_active=True)
    nb_calcules = 0

    kpi_valeurs = {
        "taux_completion_tests": stats.taux_completion_tests,
        "pages_vues_jour": float(stats.pages_vues),
        "nouveaux_utilisateurs_jour": float(stats.nouveaux_utilisateurs),
    }

    for kpi in kpis:
        valeur = kpi_valeurs.get(kpi.code)
        if valeur is None:
            continue

        KPISnapshot.objects.update_or_create(
            kpi=kpi,
            date=hier,
            periode="QUOTIDIENNE",
            defaults={"valeur": valeur},
        )
        nb_calcules += 1

    logger.info(f"{nb_calcules} KPIs calculés pour {hier}")
    return nb_calcules


@shared_task(queue="analytics")
def nettoyer_ancien_tracking(jours_retention: int = 90):
    """Supprime les logs de tracking anciens pour alléger la base."""
    from apps.analytics.models import PageView, ActionLog

    seuil = timezone.now() - timedelta(days=jours_retention)

    count_pv, _ = PageView.objects.filter(created_at__lt=seuil).delete()
    count_al, _ = ActionLog.objects.filter(created_at__lt=seuil).delete()

    logger.info(
        f"Nettoyage tracking : {count_pv} pages vues, "
        f"{count_al} actions supprimées"
    )
    return {"pages_vues": count_pv, "action_logs": count_al}


@shared_task(queue="analytics")
def aggreger_stats_hebdomadaires():
    """Agrège les stats de la semaine précédente."""
    from apps.analytics.models import DailyStats

    date_fin = timezone.now().date() - timedelta(days=1)
    date_debut = date_fin - timedelta(days=6)

    stats = DailyStats.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin,
    )

    totaux = {
        "pages_vues": sum(s.pages_vues for s in stats),
        "nouveaux_utilisateurs": sum(s.nouveaux_utilisateurs for s in stats),
        "tests_completes": sum(s.tests_completes for s in stats),
        "revenus_fcfa": sum(s.revenus_fcfa for s in stats),
    }

    logger.info(f"Agrégation hebdomadaire {date_debut}→{date_fin} : {totaux}")
    return totaux


@shared_task(queue="analytics")
def detecter_anomalies():
    """Détecte des anomalies dans les statistiques."""
    from apps.analytics.models import DailyStats

    hier = (timezone.now() - timedelta(days=1)).date()
    avant_hier = hier - timedelta(days=1)

    try:
        stats_hier = DailyStats.objects.get(date=hier)
        stats_avant = DailyStats.objects.get(date=avant_hier)
    except DailyStats.DoesNotExist:
        return []

    anomalies = []

    if stats_avant.pages_vues > 0:
        variation = (
            (stats_hier.pages_vues - stats_avant.pages_vues)
            / stats_avant.pages_vues
        ) * 100

        if variation < -50:
            anomalies.append({
                "type": "chute_trafic",
                "description": f"Chute de {abs(variation):.1f}% du trafic",
                "severity": "haute",
            })

    if anomalies:
        logger.warning(f"Anomalies détectées: {anomalies}")

    return anomalies
