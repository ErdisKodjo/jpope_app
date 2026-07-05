import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.db.functions import Greatest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import MessageForm, ThreadForm
from .models import Forum, LikeMessageForum, MessageForum, Thread

logger = logging.getLogger(__name__)


def _notify(user, titre, message, type_notif="INFO", action_url=""):
    try:
        from apps.notifications.utils import notify
        notify(user=user, titre=titre, message=message, type_notif=type_notif, action_url=action_url)
    except Exception:
        logger.exception(
            "Échec de notification in-app pour l'utilisateur %s",
            getattr(user, "pk", user),
        )


class ForumListView(ListView):
    model = Forum
    template_name = "community/forum_list.html"
    context_object_name = "forums"

    def get_queryset(self):
        qs = Forum.objects.filter(is_active=True).order_by("ordre", "nom")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(nom__icontains=q) | Q(description__icontains=q))
        return qs


class ForumDetailView(DetailView):
    model = Forum
    template_name = "community/forum_detail.html"
    context_object_name = "forum"
    slug_field = "slug"

    def get_queryset(self):
        return Forum.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        threads = (
            self.object.threads
            .exclude(statut="SUPPRIME")
            .select_related("auteur", "dernier_message__auteur")
            .order_by("-is_epingle", "-dernier_message_at", "-created_at")
        )
        ctx["threads"] = threads[:30]
        ctx["nb_threads"] = self.object.threads.exclude(statut="SUPPRIME").count()
        return ctx


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = "community/thread_form.html"

    def get_forum(self):
        slug = self.kwargs.get("forum_slug") or self.request.POST.get("forum_slug") or self.request.GET.get("forum")
        if slug:
            return get_object_or_404(Forum, slug=slug, is_active=True)
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        forum = self.get_forum()
        if forum:
            ctx["forum"] = forum
        else:
            ctx["forums"] = Forum.objects.filter(is_active=True).order_by("ordre")
        return ctx

    def form_valid(self, form):
        forum_slug = self.kwargs.get("forum_slug") or self.request.POST.get("forum_slug")
        forum = get_object_or_404(Forum, slug=forum_slug, is_active=True)
        thread = form.save(commit=False)
        thread.auteur = self.request.user
        thread.forum = forum
        thread.save()
        forum.nombre_threads = forum.threads.exclude(statut="SUPPRIME").count()
        forum.dernier_message_at = timezone.now()
        forum.save(update_fields=["nombre_threads", "dernier_message_at"])
        messages.success(self.request, "Discussion créée avec succès !")
        return redirect("community:thread-detail", pk=thread.pk)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs.")
        return super().form_invalid(form)


class ThreadDetailView(DetailView):
    model = Thread
    template_name = "community/thread_detail.html"
    context_object_name = "thread"

    def get_object(self, queryset=None):
        obj = get_object_or_404(Thread.objects.select_related("forum", "auteur"), pk=self.kwargs["pk"])
        Thread.objects.filter(pk=obj.pk).update(nombre_vues=F("nombre_vues") + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        messages_qs = (
            self.object.messages
            .filter(is_supprime=False, est_valide=True)
            .select_related("auteur")
            .order_by("created_at")
        )
        ctx["messages_forum"] = messages_qs
        ctx["reply_form"] = MessageForm()
        if self.request.user.is_authenticated:
            ctx["liked_ids"] = set(
                LikeMessageForum.objects
                .filter(utilisateur=self.request.user, message__in=messages_qs)
                .values_list("message_id", flat=True)
            )
        else:
            ctx["liked_ids"] = set()
        return ctx


class MessageCreateView(LoginRequiredMixin, View):
    def post(self, request, thread_pk):
        thread = get_object_or_404(Thread, pk=thread_pk)
        if thread.is_ferme:
            messages.error(request, "Cette discussion est fermée.")
            return redirect("community:thread-detail", pk=thread_pk)
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.auteur = request.user
            msg.save()
            thread.nombre_reponses = thread.messages.filter(is_supprime=False).count()
            thread.dernier_message = msg
            thread.dernier_message_at = timezone.now()
            thread.save(update_fields=["nombre_reponses", "dernier_message", "dernier_message_at"])
            forum = thread.forum
            Forum.objects.filter(pk=forum.pk).update(
                nombre_messages=F("nombre_messages") + 1,
                dernier_message_at=timezone.now(),
            )
            if thread.auteur != request.user:
                action_url = reverse("community:thread-detail", kwargs={"pk": str(thread.pk)})
                _notify(
                    thread.auteur,
                    "Nouvelle réponse dans votre discussion",
                    f"{request.user.get_full_name() or request.user.email} a répondu à « {thread.titre} »",
                    type_notif="INFO",
                    action_url=action_url,
                )
            messages.success(request, "Votre réponse a été publiée.")
        else:
            messages.error(request, "Le contenu ne peut pas être vide.")
        return redirect("community:thread-detail", pk=thread_pk)


class LikeMessageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        msg = get_object_or_404(MessageForum, pk=pk)
        like, created = LikeMessageForum.objects.get_or_create(utilisateur=request.user, message=msg)
        if created:
            MessageForum.objects.filter(pk=msg.pk).update(nombre_likes=F("nombre_likes") + 1)
        else:
            like.delete()
            MessageForum.objects.filter(pk=msg.pk).update(
                nombre_likes=Greatest(F("nombre_likes") - 1, 0)
            )
        msg.refresh_from_db()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"likes": msg.nombre_likes, "liked": created})
        return redirect("community:thread-detail", pk=msg.thread.pk)
