"""Services d'authentification et de profilage du tableau de bord.

Ce module centralise les informations renvoyées au dashboard afin d'éviter de
révéler des champs inutiles en fonction du rôle de l'utilisateur.
"""

from typing import Dict
from django.contrib.auth import get_user_model

User = get_user_model()

def get_dashboard_profile(user: User) -> Dict:
    """Retourne un dictionnaire contenant uniquement les champs utiles
    pour le tableau de bord en fonction du rôle de *user*.
    """
    base = {
        "id": user.id,
        "username": user.username,
        "role": getattr(user, "role", ""),
        "full_name": f"{user.first_name} {user.last_name}".strip(),
    }
    # Ajout de champs spécifiques selon le rôle
    if base["role"] == "STUDENT":
        base.update({
            "classe": getattr(user, "classe", None),
            "etablissement": getattr(user, "etablissement", None),
        })
    elif base["role"] == "COUNSELOR":
        base.update({"departement": getattr(user, "departement", None)})
    elif base["role"] == "ADMIN":
        base.update({"is_superuser": user.is_superuser})
    return base
