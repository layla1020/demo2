import re
from django import template
from Insta.models import Like
from django.urls import NoReverseMatch, reverse

register = template.Library()

@register.simple_tag
def has_user_liked_post(post, user):
    try:
        like = Like.objects.get(post=post, user=user)
        return "fa-heart"
    except:
        return "fa-heart-o"

@register.simple_tag
def is_following(current_user, background_user):
    # 获得一下我的followers，然后看看有没有current_user follow过我
    return background_user.get_followers().filter(creator=current_user).exists()

@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''