from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from .models import User, Post, Comment, Message, Chat, Follow, Like
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import (RegistrationForm, LoginForm, PostForm, CommentForm,
                    SearchForm, MessageForm)
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView, FormView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator

# Create your views here.


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['posts'] = Post.objects.filter(author=user)
        context['form'] = PostForm()

        context['followers'] = Follow.objects.filter(following=user).values_list('followers__username', flat=True)
        context['following'] = Follow.objects.filter(followers=user).values_list('following__username', flat=True)

        context['followers_count'] = Follow.objects.filter(following=user).count()
        context['following_count'] = Follow.objects.filter(followers=user).count()

        return context


    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)


def get_followers(request):
    user = request.user
    followers = Follow.objects.filter(following=user).values('followers__id', 'followers__username')
    results = render_to_string('followers_results.html', {'results': followers})
    return JsonResponse({'results': results}, safe=False)


def get_following(request):
    user = request.user
    following = Follow.objects.filter(followers=user).values('following__id', 'following__username')
    results = render_to_string('following_results.html', {'results': following})
    return JsonResponse({'results': results}, safe=False)


class ChatNewView(TemplateView):
    template_name = 'chat.html'

    def get(self, request, **kwargs):
        if self.kwargs['id'] == self.request.user.id:
            return redirect('/')
        else:
            chat = Chat.objects.filter(user1=User.objects.get(id=self.kwargs['id']), user2=self.request.user)
            if not chat:
                chat = Chat.objects.filter(user2=User.objects.get(id=self.kwargs['id']), user1=self.request.user)
                if not chat:
                    chat = Chat(user1=self.request.user, user2=User.objects.get(id=self.kwargs['id']))
                    chat.save()
                else:
                    chat = chat[0]
            else:
                chat = chat[0]
            return redirect(f'/chat/{chat.id}')


@method_decorator(login_required, name='dispatch')
class ChatView(TemplateView):
    template_name = 'chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_id = self.kwargs.get('id')

        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return redirect('/')

        user = self.request.user
        if user not in [chat.user1, chat.user2]:
            return redirect('/')

        talker = chat.user2 if chat.user1 == user else chat.user1

        context['title'] = f'Chat with {talker}'
        context['talker'] = talker
        context['user'] = user
        context['chat'] = chat
        context['messages'] = chat.messages.filter(chat=chat.id)
        context['form'] = MessageForm()

        return context

    def post(self, request, **kwargs):
        form = MessageForm(request.POST)
        if form.is_valid():
            chat_id = kwargs.get('id')
            try:
                chat = Chat.objects.get(id=chat_id)
            except Chat.DoesNotExist:
                return HttpResponseBadRequest("Chat does not exist")

            message_id = request.POST.get('message_id')
            if message_id:
                try:
                    message = Message.objects.get(id=message_id, chat=chat)
                    message.text = form.cleaned_data['text']
                    message.save()
                except Message.DoesNotExist:
                    return HttpResponseBadRequest("Message does not exist")
            else:
                try:
                    message = Message.objects.create(
                        text=form.cleaned_data['text'],
                        chat=chat,
                        user=self.request.user
                    )
                except Exception as e:
                    print(f"Error creating message: {e}")
                    return HttpResponseBadRequest("Error creating message")

                chat.messages.add(message)

            resp = {'message': message.text, 'sender': message.user.username}
        else:
            print(f"Form errors: {form.errors}")
            resp = {'message': 'ERROR'}

        return JsonResponse(resp, safe=False)


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
        comments = Comment.objects.filter(post=post)
        user_likes_post = Like.objects.filter(post=post, user=self.request.user).exists()
        like_count = len(Like.objects.filter(post=post))

        context['post'] = post
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['user_likes_post'] = user_likes_post
        context['like_count'] = like_count

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

            like_count = len(Like.objects.filter(post=post))

            return JsonResponse({'success': True, 'liked': liked, 'like_am': like_count})

        return HttpResponseRedirect(request.path)


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


class RegistrationView(CreateView):
    template_name = 'registration.html'
    model = User
    form_class = RegistrationForm
    success_url = reverse_lazy('/')

    def get_success_url(self, **kwargs):
        response = HttpResponse()
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
    redirect_authenticated_user = False

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response


class LogoutPage(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class HomePageView(TemplateView):
    template_name = 'home.html'
    posts_per_page = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search', '')
        users = User.objects.filter(username__icontains=search_query)

        if users.exists():
            posts = Post.objects.filter(author__in=users)
        else:
            posts = Post.objects.all()

        paginator = Paginator(posts, self.posts_per_page)
        page = self.request.GET.get('page', 1)
        context['posts'] = paginator.get_page(page)
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
