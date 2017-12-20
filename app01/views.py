from django.shortcuts import render,HttpResponse,redirect
from PIL import Image
# Create your views here.
from app01 import models
from utils.random_check_code import rd_check_code
from utils.pager import PageInfo
from io import BytesIO
from utils.FormInfo import LoginInfo,RegForm,ArticleForm
import os
from django.db.models import Count,Min,Max,Sum

#博客主页面
def index(request,*args,**kwargs):
    """

    :param obj: 主站分类，Python,Golang
    :param args:
    :param kwargs: 点击的主站ID
    :return:
    """
    user_id = request.session.get('user_id')
    if not user_id:
        userinfo = None
    # 登录过，传登录帐号信息
    else:
        userinfo = models.UserInfo.objects.filter(nid=user_id).first()
        #
    obj = models.Article.type_choices
    condition = {}
    type_id = int(kwargs.get('type_id')) if kwargs.get('type_id') else None
    if type_id:
        condition['article_type_id'] = type_id

    my_page = request.GET.get('page')
    count = models.Article.objects.filter(**condition).count()
    my_url = request.path_info
    #分页ul
    page_info = PageInfo(my_page, count, 3, my_url, 11)
    #页面显示的文章
    user_list = models.Article.objects.filter(**condition)[page_info.start():page_info.end()]
    return render(request,'index.html',{'tag':obj,'page_info':page_info,
                                        'user_list':user_list,'type_id':type_id,
                                        'userinfo':userinfo})

#验证码视图
def check_code(request):
    img, code = rd_check_code()
    stream = BytesIO()
    img.save(stream, 'png')
    request.session['code'] = code
    return HttpResponse(stream.getvalue())

#登录页面
def login(request):
    #获得跳转过来的URL
    if request.method == "GET":
        url = request.GET.get('url')
        obj = LoginInfo()
        return render(request,'login.html',{'obj':obj,'url':url})
    else:
        obj = LoginInfo(request.POST)
        url = request.POST.get('url')
        input_code = request.POST.get('code')
        session_code = request.session.get('code')
        if input_code.upper() == session_code.upper():
            if not obj.is_valid():
                return render(request,'login.html',{'obj':obj})
            else:
                user = obj.cleaned_data.get('username')
                pwd = obj.cleaned_data.get('password')
                res = models.UserInfo.objects.filter(username=user,password=pwd).first()
                if not res:
                    return render(request, 'login.html', {'msg': "用户名或密码错误！", 'obj': obj})
                else:
                    request.session['user_id'] = res.nid



                    try:
                        if url == 'None':
                            return redirect('/')
                        else:
                            return redirect(url)
                    except Exception as e:
                        return redirect('/')

        else:
            # return redirect('/login.html')
            return render(request,'login.html',{'msg':"验证码出错",'obj':obj})

#登出系统
def logout(request):
    request.session.clear()
    return redirect('/')

#注册页面
def reg(request):
    if request.method == 'GET':
        obj = RegForm(request)
        return render(request,'sign.html',{'obj':obj})

    else:
        obj = RegForm(request,request.POST)
        input_code = request.POST.get('code')
        session_code = request.session.get('code')
        if not input_code.upper() == session_code.upper():
            return render(request,'sign.html',{'msg':'验证码错误','obj':obj})

        if not obj.is_valid():  
            return render(request,'sign.html',{'obj':obj})
        else:
            obj.cleaned_data.pop('pwd_again')
            obj.cleaned_data.pop('code')
            models.UserInfo.objects.create(**obj.cleaned_data)
            return redirect('/login.html')

#个人博客主页面
def user(request,*args,**kwargs):
    site = kwargs.get('site')
    family = kwargs.get('family')

    my_page = request.GET.get('page')
    my_url = request.path_info
    #当有筛选
    if family:
        nid = kwargs.get('nid')
        if family=='tags':
            count = models.Article.objects.filter(blog__site=site,tags__nid=nid).count()
            page_info = PageInfo(my_page, count, 3, my_url, 11)
            obj = models.Article.objects.filter(blog__site=site,tags__nid=nid)[page_info.start():page_info.end()]
        elif family=='category':
            count = models.Article.objects.filter(blog__site=site,category__nid=nid).count()
            page_info = PageInfo(my_page, count, 3, my_url, 11)
            obj = models.Article.objects.filter(blog__site=site,category__nid=nid)[page_info.start():page_info.end()]
        else:
            count = models.Article.objects.filter(create_time__startswith=nid,blog__site=site).count()
            page_info = PageInfo(my_page, count, 3, my_url, 11)
            obj = models.Article.objects.filter(create_time__startswith=nid,blog__site=site)[page_info.start():page_info.end()]

    #没有筛选，个人全部博客
    else:
        count = models.Article.objects.filter(blog__site=site).count()
        page_info = PageInfo(my_page, count, 3, my_url, 11)
        obj = models.Article.objects.filter(blog__site=site)[page_info.start():page_info.end()]


    #分类函数
    cate_list = models.Article.objects.filter(blog__site=site).values('category__title','category__nid').annotate(c=Count('nid'))
    tags_list = models.Article.objects.filter(blog__site=site).values('tags__title','tags__nid').annotate(c=Count(1))
    #mysql查询
    # data_time = models.Article.objects.extra(select={'c':'date_fomat(create_time,"%%Y-%%m")'}).values('c').annotate(ct=Count('nid'))
    #sqlite3查询
    date_list = models.Article.objects.filter(blog__site=site).extra(select={'c':'strftime("%%Y-%%m",create_time)'}).\
        values('c').annotate(ct=Count('nid'))


    blog_msg = models.Blog.objects.filter(site=site).first()
    # blog_time = models.Article.objects.filter(blog__site=site,create_time__year=2017).values('create_time').annotate(c=Count(1))
    # print(blog_time)

    return render(request,'home.html',{'obj':obj,'blog_msg':blog_msg,'date_list':date_list,
                                       'cate_list':cate_list,'tags_list':tags_list,'page_info':page_info})

#文章详细
def page(request,*args,**kwargs):
    site = kwargs.get('site')
    nid = kwargs.get('nid')
    url = request.path_info
    user_id = request.session.get('user_id')
    if user_id:
        userinfo = models.UserInfo.objects.filter(nid=user_id).first()
    else:
        userinfo = False
    #文章内容
    obj = models.Article.objects.filter(blog__site=site,nid=nid).first()

    #分类列表
    cate_list = models.Article.objects.filter(blog__site=site).values('category__title', 'category__nid').annotate(
        c=Count('nid'))
    tags_list = models.Article.objects.filter(blog__site=site).values('tags__title', 'tags__nid').annotate(c=Count(1))
    date_list = models.Article.objects.filter(blog__site=site).extra(
        select={'c': 'strftime("%%Y-%%m",create_time)'}).values('c').annotate(ct=Count('nid'))
    #博客信息
    blog_msg = models.Blog.objects.filter(site=site).first()

    #获取评论内容，组成[[1, <Comment: Comment object>],]类似的列表
    # com_list = []
    # com = []
    # comment=enumerate(obj.comment_set.all())
    # for i,y in comment:
    #     com = []
    #     com.append(i+1)
    #     com.append(y)
    #     com_list.append(com)

    return render(request,'page.html',{'obj':obj,'blog_msg':blog_msg,'date_list':date_list,'userinfo':userinfo,
                                       'cate_list':cate_list,'tags_list':tags_list,'url':url})

#头像上传
def up_img(request):
    if request.method == 'GET':
        return HttpResponse('o12!')
    else:
        file_obj = request.FILES.get('avatar')  # 取文件时，需以FILES获取文件数据
        file_path = ('static/img/' + file_obj.name)
        f = open(file_path, 'wb')  # 写字节方式打开空文件，拼接文件路径
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        return HttpResponse(file_path)

#点赞功能
import json
def add_up(request):
    #信息列表
    ret = {}
    if request.method == 'POST':
        #当前用户id
        user_id = request.session.get('user_id')
        #没有登录
        if not user_id:
            ret['sta'] = None
        else:
            type1 = request.POST.get('res')
            num = int(request.POST.get('num'))  #目前赞数量
            url = request.POST.get('url')   #获取url
            x1,x = url.split('p/', )
            #取到文章id
            nid,y = x.split('.')   #/3.html
            #查询是否有点赞过
            obj = models.UpDown.objects.filter(user__nid=user_id,article_id=nid).count()
            if not obj:  #没有
                # 点赞
                from django.db import transaction
                with transaction.atomic():
                    if type1 == 'add-up':
                        models.UpDown.objects.create(up=True,article_id=nid,user_id=user_id)
                        #点赞数+1
                        models.Article.objects.filter(nid=nid).update(up_count=num + 1)
                        ret['stype'] = 'up'
                    else:
                        models.UpDown.objects.create(up=False, article_id=nid, user_id=user_id)
                        # 点赞数+1
                        models.Article.objects.filter(nid=nid).update(down_count=num + 1)
                        ret['stype'] = 'down'
                    print(ret['stype'])
                    ret['sta'] = True
                    ret['num']=num+1
                    ret['msg']=None
            else:
                ret['sta'] = True
                i = models.UpDown.objects.filter(user__nid=user_id, article_id=nid).values('up').first()
                if i['up']:
                    ret['msg'] = '您已经推荐过'
                else:
                    ret['msg'] = '您已经反对过'

        return HttpResponse(json.dumps(ret))

#评论
from django.db.models import F
def comment(request):
    nid = request.session.get('user_id')
    rep_id = request.POST.get('rep_id')
    content = request.POST.get('content')
    url = request.POST.get('w-url')
    x1, x = url.split('p/', )
    # 取到文章id
    aid, y = x.split('.')
    models.Comment.objects.create(content=content,article_id=aid,user_id=nid,reply_id=rep_id)
    models.Article.objects.filter(nid=aid).update(comment_count=F('comment_count')+1)
    return HttpResponse(json.dumps('ok'))

#删除评论
def del_comment(request):
    url = request.POST.get('w-url')
    x1, x = url.split('p/', )
    # 取到文章id
    aid, y = x.split('.')
    reply_id = request.POST.get('reply_id')
    models.Comment.objects.filter(nid=reply_id).delete()
    models.Article.objects.filter(nid=aid).update(comment_count=F('comment_count')-1)

    return HttpResponse(json.dumps('ok'))

def check_comment(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/')
    nid = request.GET.get('id')
    #获取评论
    ret = {'status':True,'data':None}
    try:
        c_list = models.Article.objects.filter(blog__user_id=user_id,nid=nid).values('comment__nid', 'comment__content',
                                                                                'comment__reply_id')
        co_list = {}
        res = []
        for item in c_list:
            item['child'] = []
            co_list[item['comment__nid']] = item

        for row in c_list:
            rid = row['comment__reply_id']
            if rid:
                co_list[rid]['child'].append(row)
            else:
                res.append(row)
        print(res)
        ret['data'] = res
    except Exception as e:
        ret['status'] = False
        ret['data'] = str(e)
    # print(ret)
    return HttpResponse(json.dumps(ret))
    # def foo(res):
    #     com_str = "<div class='outer-com'>"
    #     for row in res:
    #         com_str += "<div class='tab-com'>%s</div>" % (row['comment__content'])
    #         if row['child']:
    #             com_inner = foo(row['child'])
    #             com_str += com_inner
    #     com_str += "</div>"
    #     return com_str



def control(request):
    nid = request.session.get('user_id')
    if not nid:
        return redirect('/')
    blog = models.Blog.objects.filter(user_id=nid).first()
    return render(request,'control.html',{'blog':blog})

def article_manage(request,*args,**kwargs):
    nid = request.session.get('user_id')
    if not nid:
        return redirect('/')
    blog = models.Blog.objects.filter(user_id=nid).first()

    condition = {}
    for k,v in kwargs.items():
        kwargs[k] = int(v)
    for k,v in kwargs.items():
        if v != 0:
            condition[k] = v
    condition["blog__user__nid"] = nid
    # print(condition)
    type_list = models.Article.type_choices
    # 个人分类
    category_list = models.Category.objects.filter(blog__user__nid=nid)
    # 个人标签
    tag_list = models.Tag.objects.filter(blog__user__nid=nid)

    #分页
    my_page = request.GET.get('page')
    my_url = request.path_info
    obj_count = models.Article.objects.filter(**condition).count()
    page_info = PageInfo(my_page, obj_count, 5, my_url, 11)
    obj = models.Article.objects.filter(**condition)[page_info.start():page_info.end()]

    return render(request,'article_manage.html',{'res':kwargs,'obj':obj,'type_list':type_list,'obj_count':obj_count,
                                                 'category_list':category_list,'tag_list':tag_list,
                                                 'page_info':page_info,'blog':blog})

def add_article(request):
    nid = request.session.get('user_id')
    if not nid:
        return redirect('/')
    if request.method == 'GET':
        obj = ArticleForm(request)
        return render(request,'add_article.html',{'obj':obj})

    else:
        obj = ArticleForm(request,request.POST)
        print(obj.is_valid())
        if not obj.is_valid():
            return render(request, 'add_article.html', {'obj': obj})

        else:
            content = obj.cleaned_data.pop('content')
            tags_id = obj.cleaned_data.pop('tags_id')
            print(tags_id)
            blog = models.Blog.objects.filter(user_id=nid).first()
            obj.cleaned_data['blog_id'] = blog.nid
            res = models.Article.objects.create(**obj.cleaned_data)
            for i in tags_id:
                models.Article2Tag.objects.create(article_id=res.nid,tag_id=int(i))
            models.ArticleDetail.objects.create(content=content,article_id=res.nid)
            return redirect('/control.html')





def upload_img(request):
    import os
    upload_type = request.GET.get('dir')  #可以判断媒体类型
    file_obj = request.FILES.get('imgFile')
    file_path = os.path.join('static/img', file_obj.name)
    with open(file_path, 'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    dic = {
        'error': 0,
        'url': '/' + file_path,
        'message': '错误了...'
    }
    import json
    return HttpResponse(json.dumps(dic))
