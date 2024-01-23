from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Post
from .models import User, Comment


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'class': "form_e", 'placeholder': 'Search'}))


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    bio = forms.CharField(max_length=200, required=False, label='Bio')
    gender = forms.CharField(max_length=50, required=False, label='Gender')
    website = forms.CharField(max_length=250, required=False, label='Website')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'bio', 'gender', 'website']
        widgets = {
            'username': forms.TextInput(attrs={'id': 'username'}),
            'email': forms.EmailInput(attrs={'id': 'email'}),
            'bio': forms.TextInput(attrs={'id': 'bio'}),
            'gender': forms.TextInput(attrs={'id': 'gender'}),
            'website': forms.TextInput(attrs={'id': 'website'}),}


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'id': 'username'}),
            'password': forms.PasswordInput(attrs={'id': 'password'}),
        }


class SendMessageForm(forms.Form):
    content = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'placeholder': 'Type your message...', 'required': True}))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']


class FollowForm(forms.Form):
    ACTIONS = [
        ('follow', 'Follow'),
        ('unfollow', 'Unfollow'),
    ]

    action = forms.ChoiceField(choices=ACTIONS, widget=forms.HiddenInput())
