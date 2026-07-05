"""Services de visibilité et de filtrage des options du tableau de bord.

Les fonctions de ce module sont appelées depuis la vue pour retirer du
contexte les actions que l'utilisateur ne doit pas voir (ex. : création de
vœux hors période, options réservées aux admins, etc.).
"""

from typing import Dict

def filter_options(user, context: Dict) -> None:
    """Modifie *context* en place pour masquer les options non autorisées.

    Les clés ajoutées au contexte sont de type ``show_<feature>`` :
    - ``show_create_voeu`` : True si l'étudiant peut créer un vœu.
    - ``show_admin_panel`` : True uniquement pour les administrateurs.
    - ``show_counselor_contact`` : True si l'étudiant a un conseiller
      assigné et que le conseiller est accessible.
    """
    role = getattr(user, "role", None)
    # Options génériques
    context["show_admin_panel"] = role == "ADMIN"
    context["show_create_voeu"] = role == "STUDENT"

    # Exemple de condition temporelle : désactiver la création de vœu
    # si la période de candidature est close. Cette information provient
    # généralement d'un modèle ``Period`` – on utilise une valeur hard‑coded
    # ici pour illustrer la logique.
    from datetime import date
    candidature_closed = getattr(user, "candidature_closed", False)
    if role == "STUDENT":
        context["show_create_voeu"] = not candidature_closed

    # Contact conseiller
    if role == "STUDENT":
        has_conseiller = getattr(user, "conseiller_id", None) is not None
        context["show_counselor_contact"] = has_conseiller
    else:
        context["show_counselor_contact"] = False
