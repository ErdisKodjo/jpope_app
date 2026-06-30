"""
Vues Django (non-API) pour l'app chatbot.
"""
from django.views.generic import TemplateView

from apps.accounts.mixins import VerifiedAccountMixin
from apps.chatbot.models import Conversation
from apps.orientation.models import ResultatTest


class ChatbotPageView(VerifiedAccountMixin, TemplateView):
    """Page dédiée AvenBot — interface de chat complète."""
    template_name = "chatbot/chatbot.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        ctx["conversations"] = Conversation.objects.filter(
            utilisateur=user, is_active=True
        ).order_by("-updated_at")[:10]

        contexte = {"nom": user.get_full_name()}
        dernier_resultat = (
            ResultatTest.objects.filter(utilisateur=user)
            .order_by("-created_at")
            .first()
        )
        if dernier_resultat:
            contexte["code_holland"] = dernier_resultat.code_holland
            if dernier_resultat.scores_par_dimension:
                top = sorted(
                    dernier_resultat.scores_par_dimension.items(),
                    key=lambda x: x[1], reverse=True
                )[:3]
                contexte["domaines_interets"] = [k for k, _ in top]

        ctx["contexte_utilisateur"] = contexte
        return ctx
