from django.urls import path
from . import views
from .views import CreatePostView, PostView, UserProfileView

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('registration', views.RegistrationView.as_view(), name='register'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('login', views.LoginPage.as_view(), name='login'),
    path('create_post', CreatePostView.as_view(), name='create_post'),
    path('post/<int:pk>/', PostView.as_view(), name='post_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('user_profile/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
    # path('post/<int:pk>/like/', views.PostView.as_view(), name='like_post'),
    # path('comment/<int:comment_id>/like/', views.PostView.as_view(), name='like_comment'),

]

