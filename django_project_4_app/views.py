from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from .models import User, Post, Comment, Message, Chat, Follow
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm, SearchForm, FollowForm
from django.contrib.auth import authenticate, login
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView, FormView
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.db.models import F

# Create your views here.


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        posts = Post.objects.filter(author=request.user)
        form = PostForm()
        return render(request, self.template_name, {'posts': posts, 'form': form})

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('profile')
        else:
            posts = Post.objects.filter(author=request.user)
            return render(request, self.template_name, {'posts': posts, 'form': form})


class CreatePostView(TemplateView):
    template_name = 'create_post.html'

    def get(self, request, *args, **kwargs):
        form = PostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
        else:
            return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class PostView(TemplateView):
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = {}
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        context['post'] = post
        context['comments'] = Comment.objects.filter(post=post)
        context['comment_form'] = CommentForm()
        context['post_edit_form'] = PostForm(instance=post)

        return context

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        comment_form = CommentForm(request.POST)
        post_edit_form = PostForm(request.POST, request.FILES, instance=post)

        if 'comment_submit' in request.POST:
            if comment_form.is_valid():
                body = comment_form.cleaned_data['body']
                Comment.objects.create(post=post, body=body, author=request.user)
        elif 'post_edit_submit' in request.POST:
            if post_edit_form.is_valid() and post.author == request.user:
                post_edit_form.save()

        return redirect('post_detail', pk=post.id)


@method_decorator(login_required, name='dispatch')
class PostEditView(TemplateView):
    template_name = 'edit_post.html'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])

        # Check if the current user is the author of the post
        if post.author != request.user:
            return redirect('post_detail', pk=post.id)

        context = {
            'post': post,
            'post_edit_form': PostForm(instance=post),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])

        # Check if the current user is the author of the post
        if post.author != request.user:
            return redirect('post_detail', pk=post.id)

        post_edit_form = PostForm(request.POST, request.FILES, instance=post)

        if post_edit_form.is_valid():
            post_edit_form.save()

        return redirect('post_detail', pk=post.id)

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        post_edit_form = PostForm(request.POST, request.FILES, instance=post)

        if post_edit_form.is_valid():
            post_edit_form.save()

        return redirect('post_detail', pk=post.id)


class RegistrationView(CreateView):
    template_name = 'registration.html'
    model = User
    form_class = RegistrationForm
    success_url = reverse_lazy('/')

    def get_success_url(self, **kwargs):
        response = HttpResponse()
        response.set_cookie('name', 'Bob')
        return '/'


class SearchView(FormView):
    template_name = 'search.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        data_post = self.request.POST
        users = User.objects.filter(username__contains=data_post['input'])
        results = render_to_string('search_results_template.html', {'results': users})
        return JsonResponse({'results': results}, safe=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Search')
        context['profile'] = self.request.user
        return context


class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

    def post(self, request, **kwargs):
        data_post = request.POST
        current_user = self.request.user
        current_user_follow, _ = Follow.objects.get_or_create(user=current_user)
        f_user = get_object_or_404(User, id=data_post['follow'])
        f_user_follow, _ = Follow.objects.get_or_create(user=f_user)

        if data_post['is_followed'] == '0':
            current_user_follow.following.add(f_user)
            f_user_follow.followers.add(current_user)
        else:
            current_user_follow.following.remove(f_user)
            f_user_follow.followers.remove(current_user)

        current_user_follow.save()
        f_user_follow.save()

        return JsonResponse({'is_follow': int(data_post['is_followed']) ^ 1, 'followers': F('followers') + 1})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        user = get_object_or_404(User, id=self.kwargs['pk'])
        current_user_follow, _ = Follow.objects.get_or_create(user=current_user)

        context['is_followed'] = current_user_follow.following.filter(id=user.id).exists()
        context['title'] = user.username
        context['followers'] = current_user_follow.followers.count()
        context['following'] = current_user_follow.following.count()
        context['current_user'] = current_user
        context['user'] = user
        context['posts'] = Post.objects.filter(user=user)
        context['post_am'] = Post.objects.filter(user=user).count()

        return context


class LoginPage(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    redirect_authenticated_user = True


class LogoutPage(LogoutView):
    pass


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        users = User.objects.filter(username__icontains=search_query)

        if users.exists():
            posts = Post.objects.filter(author__in=users)
        else:
            posts = Post.objects.all()

        context['posts'] = posts
        context['search_query'] = search_query

        return context