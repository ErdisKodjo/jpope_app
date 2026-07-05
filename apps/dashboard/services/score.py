"""Services de calcul des scores de test.

Le module expose une fonction `calculate_test_score` qui agrège les
résultats d'un étudiant et renvoie un dictionnaire contenant le score
global ainsi que les détails par matière.
"""

from typing import Dict, List
from django.db.models import Sum

# Supposons que le modèle TestResult possède les champs `user`, `score`
# et `category` (matière). Ajustez les imports si le nom diffère.

def calculate_test_score(test_results) -> Dict:
    """Calcule le score total et la répartition par catégorie.

    * `test_results` : queryset ou liste d'objets avec les attributs
      `score` (int/float) et `category` (str).
    Retourne :
    ```json
    {
        "total": <somme>,
        "details": {"math": 45, "français": 30, ...}
    }
    ```
    """
    total = 0
    details: Dict[str, int] = {}
    for tr in test_results:
        score = getattr(tr, "score", 0)
        cat = getattr(tr, "category", "inconnu")
        total += score
        details[cat] = details.get(cat, 0) + score
    return {"total": total, "details": details}
