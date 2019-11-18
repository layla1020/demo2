from django.db import models
from imagekit.models import ProcessedImageField
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

# Create your models here.
class InstaUser(AbstractUser):
    profile_pic = ProcessedImageField(
        upload_to='static/images/profiles',
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True
        )

    #所有我创造的connections，这里用filter可以返回多个值，也就是我follow的所有的人
    def get_connections(self):
        connections = UserConnection.objects.filter(creator=self)
        return connections
    
    #别人follow我的connections，用set保存
    def get_followers(self):
        followers = UserConnection.objects.filter(following=self)
        return followers
    
    #我自己有没有被当前传进来的user所follow
    def is_followed_by(self, user):
        followers = UserConnection.objects.filter(following=self) #先找到我的followers
        return followers.filter(creator=user).exists() #然后再从这些followers中找到当前传进来的user
    
    def __str__(self):
        return self.username


class UserConnection(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
        )
    creator = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='frendship_creator_set'
        )
    following = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='friend_set'
        )
    
    # A follows B
    def __str__(self):
        return self.creator.username + ' follows ' + self.following.username


class Post(models.Model):
    #1. 当InstaUser删除的时候，Post关系也删除了
    #2. wentailai.my_posts -> ('post1', 'post2')
    author = models.ForeignKey(
        InstaUser,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='my_posts'
        )
    title = models.TextField(blank=True, null=True)
    image = ProcessedImageField(
        upload_to='static/images/posts',
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True
        )
    posted_on = models.DateTimeField(
        auto_now_add=True,
        editable=False
        )
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("post_detail", args=[str(self.id)])
    
    def get_like_count(self):
        #有多少人给这个post点过赞
        return self.likes.count()
    
    def get_comment_count(self):
        #有多少人给这个post写过评论
        return self.comments.count()

class Like(models.Model):
    #1. 当post删除的时候，like关系也被删除了
    #2. post1.likes -> (like1, like2)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
        )
    #1. 当InstaUser被删除的时候，like关系也被删除了
    #2. wentailai.likes -> ('like1')
    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='likes'
        )
    #每一个user只能给一个post点一个赞
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return 'Like: ' + self.user.username + 'likes ' + self.post.title

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    posted_on = models.DateTimeField(
        auto_now_add=True,
        editable=False
        )
    comment = models.CharField(max_length=100)

    def __str__(self):
        return self.comment
    