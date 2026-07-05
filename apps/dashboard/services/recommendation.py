"""Services de génération de recommandations.

Le module fournit `generate_recommendations` qui, à partir du profil
utilisateur et du score calculé, produit une liste de recommandations
adaptées. Les règles métier sont centralisées ici afin d'éviter la
logique dispersée dans les vues.
"""

from typing import List, Dict

def generate_recommendations(user, score: Dict) -> List[Dict]:
    """Retourne une liste de recommandations pour *user*.

    * `user` : instance du modèle User (ou un objet avec les attributs
      `role`, `classe`, etc.).
    * `score` : dictionnaire produit par ``calculate_test_score``.

    La fonction applique des règles simples :
    - Si le score total < 50 → recommandation « Renforcer les bases ».
    - Si une catégorie est < 30 → suggestion de cours ciblés.
    - Pour les étudiants en fin de cycle, proposer le suivi avec un
      conseiller.
    Les règles peuvent être enrichies ultérieurement.
    """
    recommendations: List[Dict] = []
    total = score.get("total", 0)
    details = score.get("details", {})

    if total < 50:
        recommendations.append({
            "type": "overall",
            "message": "Votre score global est faible ; envisagez de réviser les bases."
        })

    for cat, val in details.items():
        if val < 30:
            recommendations.append({
                "type": "category",
                "category": cat,
                "message": f"Renforcez vos compétences en {cat} (score {val})."
            })

    # Exemple de règle liée au rôle étudiant
    if getattr(user, "role", None) == "STUDENT":
        recommendations.append({
            "type": "counselor",
            "message": "Prenez contact avec votre conseiller pour un suivi personnalisé."
        })

    return recommendations
