from django.views.generic import DetailView, ListView

from .models import Forum, Thread


class ForumListView(ListView):
    model = Forum
    template_name = "community/forum_list.html"
    context_object_name = "forums"

    def get_queryset(self):
        return Forum.objects.filter(is_active=True).order_by("ordre")


class ForumDetailView(DetailView):
    model = Forum
    template_name = "community/forum_detail.html"
    context_object_name = "forum"


class ThreadDetailView(DetailView):
    model = Thread
    template_name = "community/thread_detail.html"
    context_object_name = "thread"
