from django.conf import settings

def global_context(request):
    """Contexte global disponible dans tous les templates."""
    return {
        "PROJECT_NAME": "AvenSU-Orienta",
        "PROJECT_VERSION": "1.0.0",
        "DEBUG": settings.DEBUG,
        "CHATBOT_ENABLED": bool(settings.CHATBOT.get("OPENAI_API_KEY")),
    }
