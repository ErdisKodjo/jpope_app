"""
Service Chatbot — Orchestrateur principal.
Supporte Anthropic (Claude), OpenAI et Ollama comme fournisseurs LLM.
"""
import logging
import time
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.chatbot.models import (
    Conversation, Message,
    RoleMessage, SourceReponse, StatutConversation,
)

logger = logging.getLogger(__name__)

# Configuration LLM depuis les settings Django
CHATBOT_SETTINGS = getattr(settings, "CHATBOT", {
    "LLM_PROVIDER": "ollama",  # "openai" or "ollama"
    "OPENAI_API_KEY": "",
    "OPENAI_MODEL": "gpt-4o-mini",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "llama3.2",
    "MAX_TOKENS": 1024,
    "TEMPERATURE": 0.7,
})

SYSTEM_PROMPT = """Tu es AvenBot, l'assistant virtuel intelligent de la plateforme AvenSU-Orienta,
spécialisée dans l'orientation post-bac pour les étudiants d'Afrique de l'Ouest (principalement le Togo).

Ton rôle est d'aider les étudiants à :
- Choisir leur formation et établissement
- Découvrir les métiers et leurs débouchés
- Comprendre les démarches d'inscription et concours
- Trouver des événements (JPO, salons, webinaires)
- Interpréter leurs résultats de tests d'orientation (RIASEC)
- Gérer leurs favoris et vœux d'inscription

Réponds toujours en français, de manière bienveillante, claire et concise.
Utilise des listes et du formatage Markdown quand c'est utile.
Si tu ne connais pas la réponse, dis-le honnêtement et propose une alternative."""


class ChatbotService:
    """
    Orchestrateur principal du chatbot.

    Flux de traitement d'un message utilisateur :
    1. Sauvegarde du message utilisateur
    2. Construction du contexte
    3. Appel au LLM (OpenAI ou Ollama)
    4. Sauvegarde de la réponse
    5. Mise à jour des stats de la conversation
    """

    def __init__(self):
        self.llm = LLMService()

    @transaction.atomic
    def traiter_message(
        self,
        conversation: Conversation,
        message_utilisateur: str,
    ) -> Message:
        """
        Traite un message utilisateur et retourne la réponse du chatbot.
        """
        start_time = time.time()

        # 1. Sauvegarder le message utilisateur
        msg_user = Message.objects.create(
            conversation=conversation,
            role=RoleMessage.USER,
            contenu=message_utilisateur,
        )

        # 2. Construire l'historique pour le LLM
        historique = self._construire_historique(conversation)

        # 3. Appeler le LLM
        try:
            llm_response = self.llm.generer_reponse(
                messages=historique,
                message_utilisateur=message_utilisateur,
                contexte_utilisateur=conversation.contexte_utilisateur,
            )
            reponse_contenu = llm_response.get("content", "")
            tokens_total = llm_response.get("tokens_total", 0)
            modele = llm_response.get("model", "")
            source = SourceReponse.LLM_DIRECT

        except Exception as e:
            logger.error(f"Erreur LLM: {e}", exc_info=True)
            reponse_contenu = (
                "Je rencontre une difficulté technique. "
                "Veuillez réessayer dans quelques instants ou "
                "contacter le support AvenSU."
            )
            tokens_total = 0
            modele = ""
            source = SourceReponse.FALLBACK

        # 4. Calculer la latence
        latence_ms = int((time.time() - start_time) * 1000)

        # 5. Sauvegarder la réponse
        msg_assistant = Message.objects.create(
            conversation=conversation,
            role=RoleMessage.ASSISTANT,
            contenu=reponse_contenu,
            source_reponse=source,
            tokens_total=tokens_total,
            tokens_used=tokens_total,
            modele_utilise=modele,
            latence_ms=latence_ms,
        )

        # 6. Mettre à jour la conversation
        Conversation.objects.filter(pk=conversation.pk).update(
            nombre_messages=F("nombre_messages") + 2,
            nombre_messages_utilisateur=F("nombre_messages_utilisateur") + 1,
            nombre_messages_assistant=F("nombre_messages_assistant") + 1,
            dernier_message_at=timezone.now(),
            tokens_utilises=F("tokens_utilises") + tokens_total,
        )
        conversation.refresh_from_db()

        # Générer le titre si premier message
        if conversation.nombre_messages == 2 and not conversation.titre:
            conversation.titre = message_utilisateur[:100]
            conversation.save(update_fields=["titre"])

        return msg_assistant

    def _construire_historique(self, conversation: Conversation, limit: int = 10) -> list:
        """
        Construit l'historique de la conversation pour le LLM.
        """
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        # Contexte utilisateur
        if conversation.contexte_utilisateur:
            contexte = self._formater_contexte(conversation.contexte_utilisateur)
            if contexte:
                messages[0]["content"] += f"\n\n{contexte}"

        # Historique des messages (limité aux N derniers)
        historique_db = list(
            Message.objects.filter(
                conversation=conversation,
                role__in=[RoleMessage.USER, RoleMessage.ASSISTANT],
            ).order_by("-created_at")[:limit]
        )
        historique_db.reverse()

        for msg in historique_db:
            role = "user" if msg.role == RoleMessage.USER else "assistant"
            messages.append({
                "role": role,
                "content": msg.contenu,
            })

        return messages

    def _formater_contexte(self, contexte: dict) -> str:
        """Formate le contexte utilisateur pour l'injection dans le prompt."""
        lignes = []

        if contexte.get("nom"):
            lignes.append(f"Étudiant: {contexte['nom']}")

        if contexte.get("niveau_etude"):
            lignes.append(f"Niveau: {contexte['niveau_etude']}")

        if contexte.get("domaines_interets"):
            lignes.append(f"Domaines d'intérêt: {', '.join(contexte['domaines_interets'])}")

        if contexte.get("code_holland"):
            lignes.append(f"Profil RIASEC: {contexte['code_holland']}")

        if lignes:
            return "Profil de l'utilisateur:\n" + "\n".join(lignes)
        return ""

    def creer_conversation(
        self,
        utilisateur,
        canal: str = "WEB",
    ) -> Conversation:
        """Crée une nouvelle conversation pour un utilisateur."""
        return Conversation.objects.create(
            utilisateur=utilisateur,
            canal=canal,
        )

    def get_historique_conversation(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> list:
        """Retourne l'historique d'une conversation."""
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).order_by("created_at")[:limit]
        return list(messages)


class LLMService:
    """
    Service d'abstraction LLM — supporte Anthropic (Claude), OpenAI et Ollama.
    """

    def __init__(self):
        self.provider = CHATBOT_SETTINGS.get("PROVIDER", "anthropic")
        self.max_tokens = CHATBOT_SETTINGS.get("MAX_TOKENS", 1024)
        self.temperature = CHATBOT_SETTINGS.get("TEMPERATURE", 0.7)

    def generer_reponse(
        self,
        messages: list,
        message_utilisateur: str = "",
        contexte_utilisateur: dict = None,
    ) -> dict:
        """
        Génère une réponse via le LLM configuré.

        Returns:
            dict: {"content": str, "tokens_total": int, "model": str}
        """
        if self.provider == "anthropic":
            return self._appeler_anthropic(messages)
        elif self.provider == "openai":
            return self._appeler_openai(messages)
        else:
            return self._appeler_ollama(messages)

    def _appeler_anthropic(self, messages: list) -> dict:
        """Appelle l'API Anthropic Claude."""
        try:
            import anthropic

            api_key = CHATBOT_SETTINGS.get("ANTHROPIC_API_KEY", "")
            model = CHATBOT_SETTINGS.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

            # Anthropic sépare le message system des autres messages
            system_content = ""
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    chat_messages.append({"role": msg["role"], "content": msg["content"]})

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=self.max_tokens,
                system=system_content,
                messages=chat_messages,
            )

            content = response.content[0].text if response.content else ""
            tokens_total = response.usage.input_tokens + response.usage.output_tokens

            return {
                "content": content,
                "tokens_total": tokens_total,
                "model": model,
            }

        except ImportError:
            logger.error("Package 'anthropic' non installé. Installez avec: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"Erreur API Anthropic: {e}")
            raise

    def _appeler_openai(self, messages: list) -> dict:
        """Appelle l'API OpenAI."""
        try:
            import openai

            api_key = CHATBOT_SETTINGS.get("OPENAI_API_KEY", "")
            model = CHATBOT_SETTINGS.get("OPENAI_MODEL", "gpt-4o-mini")

            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return {
                "content": response.choices[0].message.content,
                "tokens_total": response.usage.total_tokens,
                "model": model,
            }

        except ImportError:
            logger.error("Package 'openai' non installé. Installez avec: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Erreur API OpenAI: {e}")
            raise

    def _appeler_ollama(self, messages: list) -> dict:
        """Appelle l'API Ollama (local)."""
        try:
            import requests

            base_url = CHATBOT_SETTINGS.get("OLLAMA_BASE_URL", "http://localhost:11434")
            model = CHATBOT_SETTINGS.get("OLLAMA_MODEL", "llama3.2")

            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            prompt_eval_count = data.get("prompt_eval_count", 0)

            return {
                "content": content,
                "tokens_total": eval_count + prompt_eval_count,
                "model": model,
            }

        except requests.exceptions.ConnectionError:
            logger.error(
                f"Impossible de se connecter à Ollama sur {CHATBOT_SETTINGS.get('OLLAMA_BASE_URL')}. "
                f"Assurez-vous qu'Ollama est démarré."
            )
            raise
        except Exception as e:
            logger.error(f"Erreur Ollama: {e}")
            raise
