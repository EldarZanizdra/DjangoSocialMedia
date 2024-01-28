from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('registration/', views.RegistrationView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('get_followers/', views.get_followers, name='get_followers'),
    path('get_following/', views.get_following, name='get_following'),
    path('logout/', views.LogoutPage.as_view(), name='logout'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('post/<int:pk>/', views.PostView.as_view(), name='post_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('edit_post/<int:pk>/', views.PostEditView.as_view(), name='edit_post'),
    path('user_profile/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
    path('chatNew/<int:id>/', views.ChatNewView.as_view(), name='chatNew'),
    path('chat/<int:id>/', views.ChatView.as_view(), name='chat')
]

