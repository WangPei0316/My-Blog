from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags
import markdown


class Category(models.Model):
    """
      Django 要求模型必须继承 models.Model 类。
      Category 只需要一个简单的分类名 name 就可以了。
      CharField 指定了分类名 name 的数据类型，CharField 是字符型，
      """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    文章的数据库表是涉及的字段多。
    """

    #标题
    title = models.CharField(max_length=70)

    #创建时间和最后一次修改时间.使用DateTimeField()
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField()

    # 文章正文，使用 TextField
    # 存储比较短的字符串可以使用 CharField，但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本。
    body = models.TextField()

    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField(max_length=200,blank=True)

    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以使用的是 ForeignKey，即一对多的关联关系。
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以使用 ManyToManyField，表明这是多对多的关联关系。
    # 文章可以没有标签，因此为标签 tags 指定了 blank=True。
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag,blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 Django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
    # 通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和 Category 类似。
    author = models.ForeignKey(User)

    #新增views字段记录阅读量
    views = models.PositiveIntegerField(default=0)
    #增加模型方法,先将自身对应的views字段值加一，再save到数据库
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    #reverse 函数，第一个参数的值是 'blog:detail'，是 blog下的 name=detail 的函数，由于在上面通过 app_name = 'blog' 告诉了 Django 这个 URL 模块是属于 blog 应用的，因此 Django 能够顺利地找到 blog 应用下 name 为 detail 的视图函数，于是 reverse 函数会去解析这个视图函数对应的 URL，这里 detail 对应的规则就是 post/(?P<pk>[0-9]+)/ 这个正则表达式，而正则表达式部分会被后面传入的参数 pk 替换，所以，如果 Post 的 id（或者 pk，这里 pk 和 id 是等价的） 是 255 的话，那么 get_absolute_url 函数返回的就是 /post/255/ ，这样 Post 自己就生成了自己的 URL。
    def get_absolute_url(self):
        return reverse('blog:detail',kwargs={'pk':self.pk})
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-create_time']

    def save(self, *args,**kwargs):
        #如果没有填写摘要
        if not self.excerpt:
            #先实例化一个Markdown类，用于渲染body的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            #先将Markdown文本渲染成html文本
            #strip_tags去掉HTML文本的全部HTML标签
            #从文本摘取前54个字符赋给excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        #调用父类的save方法将数据保存到数据库中
        super(Post,self).save(*args,**kwargs)