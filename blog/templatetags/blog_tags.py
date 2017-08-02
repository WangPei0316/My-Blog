from ..models import Post,Category
from django import template
from django.db.models.aggregates import Count

register = template.Library()

# 最新文章模板标签
@register.simple_tag()
def get_recent_posts(num = 5):
    return Post.objects.all().order_by('-create_time')[:num]

# 归档模板标签
@register.simple_tag()
def archives():
    return Post.objects.dates('create_time','month',order='DESC')

# 分类模板标签
@register.simple_tag()
def get_categories():
    return Category.objects.annotate(num_posts = Count('post')).filter(num_posts__gt = 0)
