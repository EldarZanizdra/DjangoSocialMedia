from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from .models import User, Post, Comment, Message, Chat, Follow, Like
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import (RegistrationForm, LoginForm, PostForm, CommentForm,
                    SearchForm, ChatForm, MessageForm)

from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView, FormView
from django.views.generic.base import TemplateView, RedirectView
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

# Create your views here.


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.request.user)
        context['form'] = PostForm()

        context['followers_count'] = Follow.objects.filter(following=self.request.user).count()
        context['following_count'] = Follow.objects.filter(followers=self.request.user).count()

        return context

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('profile')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)


class StartChatView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        user1 = get_object_or_404(User, id=self.kwargs['user_id'])
        for c in Chat.objects.all():
            if user in c.members.all() and user1 in c.members.all():
                self.url = '/chats'
                break
        else:
            chat = Chat()
            chat.save()
            chat.members.add(user, user1)
            self.url = '/chats'
        return super().get_redirect_url(*args, **kwargs)


class ChatsView(TemplateView):
    template_name = 'chats.html'

    def post(self, request):
        data_post = request.POST
        user = self.request.user
        chat = get_object_or_404(Chat, id=data_post['chat'])

        if 'message' in data_post.keys():
            form = MessageForm(data=data_post)
            if form.is_valid():
                message = form.save(commit=False)
                message.user = user
                message.chat = chat
                message.save()
                return JsonResponse({'message': message.text}, safe=False)
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        messages = Message.objects.filter(chat=chat)
        form = MessageForm()
        result = render_to_string('chat.html', {'messages': messages, 'form': form, 'chat': chat, 'user': user})
        return JsonResponse(result, safe=False)


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
        context['user_likes_post'] = Like.objects.filter(post=post, user=self.request.user).exists()
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
        elif 'like_submit' in request.POST:
            user_likes_post = Like.objects.filter(post=post, user=request.user).exists()
            if not user_likes_post:
                Like.objects.create(post=post, user=request.user)
                liked = True
            else:
                Like.objects.filter(post=post, user=request.user).delete()
                liked = False

            context = self.get_context_data()
            context['user_likes_post'] = liked

            return JsonResponse({'success': True, 'liked': liked, 'like_am': post.likes.count})

        context = self.get_context_data()
        context['user_likes_post'] = Like.objects.filter(post=post, user=request.user).exists()

        return self.render_to_response(context)


@method_decorator(login_required, name='dispatch')
class PostEditView(TemplateView):
    template_name = 'edit_post.html'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])

        if post.author != request.user:
            return redirect('post_detail', pk=post.id)

        context = {
            'post': post,
            'post_edit_form': PostForm(instance=post),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])

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
        user_to_follow = get_object_or_404(User, id=data_post['follow'])
        user_to_follow_follow, _ = Follow.objects.get_or_create(user=user_to_follow)

        if data_post['is_followed'] == '0':
            current_user_follow.following.add(user_to_follow)
            user_to_follow_follow.followers.add(current_user)
        else:
            current_user_follow.following.remove(user_to_follow)
            user_to_follow_follow.followers.remove(current_user)

        current_user_follow.save()
        user_to_follow_follow.save()

        return JsonResponse({'is_follow': int(data_post['is_followed']) ^ 1, 'followers': user_to_follow_follow.followers.count()})

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
        context['posts'] = Post.objects.filter(author=user)
        context['post_am'] = context['posts'].count()

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

    def post(self, request, *args, **kwargs):
        if 'like_post' in request.POST:
            post_id = request.POST.get('like_post')
            post = Post.objects.get(pk=post_id)
            user = request.user

            user_likes_post = post.likes.filter(user=user).exists()

            if not user_likes_post:
                post.likes.create(user=user)
                is_liked = 1
            else:
                post.likes.filter(user=user).delete()
                is_liked = 0

            return JsonResponse({'success': True, 'like_am': post.likes.count(), 'is_liked': is_liked})

        return super().post(request, *args, **kwargs)