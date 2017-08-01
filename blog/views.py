import markdown
from django.shortcuts import render,get_object_or_404
from .models import Post,Category
from comments.forms import CommentForm
#首页视图
def index(request):

    #首先接受了一个名为 request 的参数，这个 request 就是 Django 为我们封装好的 HTTP 请求，它是类 HttpRequest 的一个实例。然后我们便直接返回了一个 HTTP 响应给用户，这个 HTTP 响应也是 Django 帮我们封装好的，它是类 HttpResponse 的一个实例，只是我们给它传了一个自定义的字符串参数。
    #return HttpResponse('欢迎访问我的博客首页！')

    post_list = Post.objects.all().order_by('-create_time')
    return render(request,'blog/index.html',context={
        'post_list':post_list,
    })

#归档视图
def archives(request,year,month):
    post_list = Post.objects.filter(create_time__year=year,
                                    create_time__month=month).order_by('-create_time')
    return render(request,'blog/index.html',context={'post_list':post_list})

#分类视图
def category(request,pk):
    cate = get_object_or_404(Category,pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-create_time')
    return render(request,'blog/index.html',context={'post_list':post_list})


#详情页视图
def detail(request,pk):
    #用到了从 django.shortcuts 模块导入的 get_object_or_404 方法，其作用就是当传入的 pk 对应的 Post 在数据库存在时，就返回对应的 post，如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。
    post = get_object_or_404(Post,pk=pk)
    #阅读量加1
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions = [
                        'markdown.extensions.extra',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    #获取这篇post下的全部评论
    comment_list = post.comment_set.all()
    # 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
    context = {
        'post':post,
        'form':form,
        'comment_list':comment_list
    }
    return render(request,'blog/detail.html',context=context)