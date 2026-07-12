"""
Service Stripe pour paiements par carte bancaire.

Cahier des charges (Business Plan P-5) :
Stripe est utilisé pour les abonnements Premium des candidats et SaaS des établissements.
Flooz/TMoney (déjà implémentés) couvrent les paiements Mobile Money locaux.

Endpoints exposés :
- Création d'un PaymentIntent (paiement ponctuel)
- Création d'un Customer + Subscription (abonnement récurrent)
- Webhook Stripe (signature + dispatch d'événements)
- Portal billing (gestion client self-service)
"""
import logging
from typing import Optional, Dict, Any
import stripe
from django.conf import settings

logger = logging.getLogger(__name__)


class StripeService:
    """Service de paiement Stripe (carte bancaire, abonnements)."""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.currency = settings.STRIPE_CURRENCY  # XOF (FCFA)

    # ─── Customers ───

    def create_customer(self, user) -> Dict[str, Any]:
        """Crée un customer Stripe lié à l'utilisateur AvenSU."""
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
            phone=user.phone or None,
            metadata={
                "avensu_user_id": str(user.id),
                "avensu_role": user.role,
            },
        )
        return {"stripe_customer_id": customer.id, "customer": customer}

    def get_or_create_customer(self, user) -> str:
        """Récupère le customer_id existant ou en crée un nouveau."""
        from apps.payments.models import Abonnement
        abonnement = Abonnement.objects.filter(utilisateur=user).first()
        if abonnement and abonnement.stripe_customer_id:
            return abonnement.stripe_customer_id
        result = self.create_customer(user)
        return result["stripe_customer_id"]

    # ─── Payment Intents (paiement ponctuel) ───

    def create_payment_intent(
        self,
        amount: int,
        user,
        description: str = "",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Crée un PaymentIntent pour un paiement ponctuel.
        amount en FCFA (entier, sans décimales car XOF est une currency 0-decimal).
        """
        customer_id = self.get_or_create_customer(user)
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=self.currency,
            customer=customer_id,
            description=description,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True},
        )
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": self.currency,
        }

    # ─── Subscriptions (abonnements récurrents) ───

    def create_subscription(
        self,
        user,
        price_id: str,
        plan_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Crée un abonnement Stripe pour un utilisateur.
        price_id : ID du Price Stripe (configuré sur le dashboard Stripe)
        """
        customer_id = self.get_or_create_customer(user)
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
            metadata=metadata or {},
        )
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status,
        }

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Annule un abonnement en fin de période."""
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True,
        )
        return {"subscription_id": subscription.id, "cancel_at": subscription.cancel_at}

    def retrieve_subscription(self, subscription_id: str) -> Dict[str, Any]:
        sub = stripe.Subscription.retrieve(subscription_id)
        return {
            "id": sub.id,
            "status": sub.status,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }

    # ─── Webhook ───

    def construct_webhook_event(self, payload: bytes, signature: str):
        """Vérifie la signature du webhook Stripe."""
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

    def handle_webhook_event(self, event) -> Dict[str, Any]:
        """
        Dispatch l'événement Stripe vers les handlers appropriés.
        Met à jour les abonnements en base + déclenche les actions (notifications, etc.)
        """
        event_type = event["type"]
        data = event["data"]["object"]

        handler_map = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed,
        }
        handler = handler_map.get(event_type)
        if handler:
            return handler(data)
        logger.info(f"Stripe webhook non géré : {event_type}")
        return {"handled": False, "event_type": event_type}

    def _handle_payment_succeeded(self, data):
        logger.info(f"Stripe payment succeeded: {data.get('id')}")
        return {"handled": True, "action": "payment_succeeded"}

    def _handle_payment_failed(self, data):
        logger.warning(f"Stripe payment failed: {data.get('id')}")
        return {"handled": True, "action": "payment_failed"}

    def _handle_subscription_created(self, data):
        from apps.payments.models import Abonnement
        sub_id = data.get("id")
        customer_id = data.get("customer")
        # Récupère l'utilisateur via le metadata
        user_id = data.get("metadata", {}).get("avensu_user_id")
        if user_id:
            try:
                from apps.accounts.models import User
                user = User.objects.get(id=user_id)
                Abonnement.objects.update_or_create(
                    stripe_subscription_id=sub_id,
                    defaults={
                        "utilisateur": user,
                        "stripe_customer_id": customer_id,
                        "statut": data.get("status", "active"),
                    },
                )
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found for Stripe sub {sub_id}")
        return {"handled": True, "action": "subscription_created"}

    def _handle_subscription_updated(self, data):
        from apps.payments.models import Abonnement
        sub_id = data.get("id")
        Abonnement.objects.filter(stripe_subscription_id=sub_id).update(
            statut=data.get("status", "active"),
        )
        return {"handled": True, "action": "subscription_updated"}

    def _handle_subscription_deleted(self, data):
        from apps.payments.models import Abonnement
        Abonnement.objects.filter(stripe_subscription_id=data.get("id")).update(
            statut="annule",
        )
        return {"handled": True, "action": "subscription_deleted"}

    def _handle_invoice_paid(self, data):
        logger.info(f"Stripe invoice paid: {data.get('id')}")
        return {"handled": True, "action": "invoice_paid"}

    def _handle_invoice_failed(self, data):
        logger.warning(f"Stripe invoice payment failed: {data.get('id')}")
        return {"handled": True, "action": "invoice_failed"}

    # ─── Portal customer (self-service) ───

    def create_portal_session(self, user, return_url: str) -> Dict[str, Any]:
        """Crée une session Stripe Customer Portal pour gestion self-service."""
        customer_id = self.get_or_create_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"url": session.url}

    # ─── Plans ───

    def list_plans(self) -> Dict[str, Any]:
        """Liste les Price Stripe disponibles (pour l'affichage sur l'app)."""
        prices = stripe.Price.list(active=True, expand=["data.product"])
        return {
            "plans": [
                {
                    "id": p.id,
                    "product_name": p.product.name,
                    "amount": p.unit_amount,
                    "currency": p.currency,
                    "interval": p.recurring.interval if p.recurring else "one_time",
                    "interval_count": p.recurring.interval_count if p.recurring else 1,
                }
                for p in prices
            ]
        }
