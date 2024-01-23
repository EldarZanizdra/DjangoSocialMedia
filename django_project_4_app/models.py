from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


class User(AbstractUser):
    bio = models.CharField(max_length=200, default='', null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, default='', blank=True)
    website = models.CharField(max_length=250, null=True, default='', blank=True)
    image = models.ImageField(upload_to='media/profs/', default='media/profs/default.png')


class Follow(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)


class Abstract(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(Abstract):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='media/photo', null=True, blank=True)

    likes = models.ManyToManyField('Like', related_name='posts_likes', blank=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.author.username} - {self.body}'


class Like(Abstract):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)


class Chat(models.Model):
   user1 = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE)
   user2 = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE)


class Message(models.Model):
   text = models.CharField(max_length=1024)
   chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
   user = models.ForeignKey(User, on_delete=models.CASCADE)
