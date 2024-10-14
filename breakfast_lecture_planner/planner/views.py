from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from markdown import markdown
from django.http import JsonResponse

from .forms import PostForm
from .models import Post



class ContactsView(View):
    template_name = 'planner/contacts.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class FaqView(View):
    template_name = 'planner/FAQ.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class CabinetView(View):
    template_name = 'planner/cabinet.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class Planner(DetailView):
    model = Post
    template_name = 'planner/post.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=12)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['content'] = markdown(post.content)
        return context


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'planner/post_form.html'

    def get_success_url(self):
        return reverse_lazy('planner:post-detail', kwargs={'pk': self.object.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = 'planner/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['content'] = markdown(post.content)
        return context


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'planner/post_form.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save()
            return JsonResponse({'content': markdown(self.object.content)})

        return JsonResponse({'error': 'Invalid form'}, status=400)