from annoying.decorators import ajax_request
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from Insta.models import Post, Like, InstaUser, UserConnection, Comment
from django.urls import reverse_lazy
from Insta.forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class PostView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'index.html'
    login_url = 'login'

    def get_queryset(self):
        current_user = self.request.user
        following = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            following.add(conn.following)
        return Post.objects.filter(author__in=following)

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = '__all__'
    login_url = 'login'

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]

class UserProfileView(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'user_profile.html'
    login_url = 'login'

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name = 'edit_profile.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'
    success_url = reverse_lazy('login')

#创建这个view的目的是为了建/insta/like这个页面，它需要一个view
@ajax_request
def addLike(request):
    #拿到post_id，post_pk是从index.js中传过来的key
    post_pk = request.POST.get('post_pk')
    #根据post_id拿到post
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user) #创建一个新的Like的object
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user) #如果已经存在了一个like
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }

#创建这个view的目的是为了建/insta/togglefollow这个页面，它需要一个view
@ajax_request
def toggleFollow(request):
    #拿到follow_user_id，follow_user_pk是从index.js中传过来的key
    follow_user_pk = request.POST.get('follow_user_pk')
    #根据follow_user_id拿到follow_user
    follow_user = InstaUser.objects.get(pk=follow_user_pk)
    current_user = InstaUser.objects.get(pk=request.user.pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user, following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                connection = UserConnection.objects.filter(creator=current_user, following=follow_user)
                connection.delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result': result,
        'follow_user_pk': follow_user_pk,
        'type': request.POST.get('type') 
    }

#创建这个view的目的是为了建/insta/comment这个页面，它需要一个view
@ajax_request
def addComment(request):
    #拿到post_pk, comment_text是从index.js中传过来的key
    post_pk = request.POST.get('post_pk')
    comment_text = request.POST.get('comment_text')
    #根据post_id拿到post
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}
    try:
        comment = Comment(post=post, user=request.user, comment=comment_text)
        comment.save()

        username = request.user.username

        commenter_info = {
            'username': username,
            'comment_text': comment_text
        }
        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }
