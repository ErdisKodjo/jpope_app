"""Services liés à l'affectation et à la visibilité des conseillers.

Ce module centralise la logique permettant de déterminer quel conseiller
est disponible pour un étudiant et si le conseiller peut être contacté.
"""

from typing import Optional

def assign_conseiller(user) -> Optional[dict]:
    """Retourne le conseiller assigné à *user* (ou ``None``).

    La règle actuelle :
    - Un étudiant possède un champ ``conseiller`` (FK vers le modèle
      ``Counselor``). Si ce champ est renseigné, on renvoie ses données.
    - Sinon, on sélectionne le conseiller le plus disponible du même
      département.
    """
    conseiller = getattr(user, "conseiller", None)
    if conseiller:
        return {"id": conseiller.id, "name": str(conseiller)}
    # Fallback : chercher un conseiller du même département
    dept = getattr(user, "departement", None)
    if not dept:
        return None
    # Importation paresseuse pour éviter les imports circulaires
    from apps.dashboard.models import Counselor
    cand = Counselor.objects.filter(departement=dept).first()
    return {"id": cand.id, "name": str(cand)} if cand else None

def is_conseiller_accessible(user, conseiller_obj) -> bool:
    """Vérifie que *user* a le droit de contacter *conseiller_obj*.

    - Un étudiant ne peut contacter que le conseiller qui lui est assigné.
    - Un conseiller peut voir uniquement les étudiants qui lui sont
      rattachés.
    - Les administrateurs ont un accès complet.
    """
    role = getattr(user, "role", None)
    if role == "ADMIN":
        return True
    if role == "STUDENT":
        return getattr(user, "conseiller_id", None) == conseiller_obj.id
    if role == "COUNSELOR":
        return conseiller_obj.id == user.id
    return False
