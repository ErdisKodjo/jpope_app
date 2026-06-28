from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions personnalisé pour l'API."""
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code
        response.data["error_type"] = exc.__class__.__name__
    else:
        logger.exception("Erreur non gérée dans l'API", exc_info=exc)
        response = Response(
            {
                "error": "Erreur interne du serveur",
                "status_code": 500,
                "detail": "Une erreur inattendue s'est produite.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
