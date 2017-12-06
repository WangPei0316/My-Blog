import xadmin
from xadmin import  views
from .models import Post,Category,Tag


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

class GlobalSetting(object):
    site_title="我的博客"
    site_footer="我的博客"


class PostAdmin(object):
    list_display = ['title','create_time','modified_time','category','author']


xadmin.site.register(Post,PostAdmin)
xadmin.site.register(Category)
xadmin.site.register(Tag)
xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView,GlobalSetting)