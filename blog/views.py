import markdown
from django.shortcuts import render,get_object_or_404
from .models import Post,Category,Tag
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension

#首页视图
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    #指定paginate_by属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 2
    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        """

        #首先获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        #调用自己写的 pagination_data 方法获得显示分页导航条需要的数据
        pagination_data = self.pagination_data(paginator,page,is_paginated)

        # 将分页导航条的模板变量更新到 context 中， pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 此时 context 字典中已有了显示分页导航条所需的数据。
        return context
    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            #如果没有分页，则无需显示分页导航条，不用分页导航条的数据，返回空字典
            return {}

        #当前页左边连续的页码号，初始值为空
        left = []
        #当前页右边连续的页码号，初始值为空
        right = []
        #标签第1页页码后是否需要显示省略号
        left_has_more = False
        #标签最后一页页码后是否需要显示省略号
        right_has_more = False
        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False
        # 标示是否需要显示最后一页的页码号。
        last = False

        #获取当前用户请求的页码号
        page_number = page.number
        #获取分页后的总页数
        total_pages = paginator.num_pages
        #获取整个分页页码列表，比如分了4页，就是[1,2,3,4]
        page_range = paginator.page_range

        if page_number == 1:
            right = page_range[page_number:page_number+2]
            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

        else:
            left = page_range[(page_number - 3) if (page_number -3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }

        return data






# def index(request):
#     #首先接受了一个名为 request 的参数，这个 request 就是 Django 为我们封装好的 HTTP 请求，它是类 HttpRequest 的一个实例。然后我们便直接返回了一个 HTTP 响应给用户，这个 HTTP 响应也是 Django 帮我们封装好的，它是类 HttpResponse 的一个实例，只是我们给它传了一个自定义的字符串参数。
#     #return HttpResponse('欢迎访问我的博客首页！')
#     post_list = Post.objects.all().order_by('-create_time')
#     return render(request,'blog/index.html',context={
#         'post_list':post_list,
#     })


#归档视图
class ArchivesView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView,self).get_queryset().filter(create_time__year=year,create_time__month=month)

# def archives(request,year,month):
#     post_list = Post.objects.filter(create_time__year=year,
#                                     create_time__month=month).order_by('-create_time')
#     return render(request,'blog/index.html',context={'post_list':post_list})


#分类视图
class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category = cate)

# def category(request,pk):
#     cate = get_object_or_404(Category,pk=pk)
#     post_list = Post.objects.filter(category=cate).order_by('-create_time')
#     return render(request,'blog/index.html',context={'post_list':post_list})

# 标签视图
class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags = tag)


#详情页视图
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    def get(self,request,*args,**kwargs):
        #复写get方法目的是因为每当文章被访问就需要将阅读量+1
        #get方法返回的是一个HttpResponse实例
        #之所以要先调用父类的get方法，是因为只有当get方法被调用后
        #才有self.object属性，其值为Post模型实例，即被访问的文章post
        response =super(PostDetailView,self).get(request,*args,**kwargs)

        #将文章阅读量+1
        #注意self.object的值就是被访问的文章post
        self.object.increase_views()

        #视图必须返回一个HttpResponse对象
        return response

    def get_object(self, queryset=None):
        #复写get_object方法是为了对post的body值进行渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        md = markdown.markdown(extensions = [
                        'markdown.extensions.extra',
                        'markdown.extensions.codehilite',
                        TocExtension(slugify=slugify),
                                  ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        #复写get_context_data的目的是为了除了将post传递给模板外
        #还要将评论表单、post下的评论列表传递给模板
        context =super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list =self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list
        })
        return context


# def detail(request,pk):
#     #用到了从 django.shortcuts 模块导入的 get_object_or_404 方法，其作用就是当传入的 pk 对应的 Post 在数据库存在时，就返回对应的 post，如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。
#     post = get_object_or_404(Post,pk=pk)
#     #阅读量加1
#     post.increase_views()
#     post.body = markdown.markdown(post.body,
#                                   extensions = [
#                         'markdown.extensions.extra',
#                         'markdown.extensions.codehilite',
#                         'markdown.extensions.toc',
#                                   ])
#     form = CommentForm()
#     #获取这篇post下的全部评论
#     comment_list = post.comment_set.all()
#     # 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
#     context = {
#         'post':post,
#         'form':form,
#         'comment_list':comment_list
#     }
#     return render(request,'blog/detail.html',context=context)