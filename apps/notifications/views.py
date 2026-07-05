"""
Vues web pour l'app notifications.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        filtre = self.request.GET.get("filtre")
        if filtre == "non_lues":
            qs = qs.filter(is_read=False)
        elif filtre == "lues":
            qs = qs.filter(is_read=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["nb_non_lues"] = Notification.objects.filter(user=self.request.user, is_read=False).count()
        ctx["filtre"] = self.request.GET.get("filtre", "")
        return ctx


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = Notification.objects.filter(pk=pk, user=request.user).first()
        if notif:
            notif.marquer_comme_lue()
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            next_url = "/"
        return redirect(next_url)


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        from django.shortcuts import redirect
        return redirect("notifications:list")
