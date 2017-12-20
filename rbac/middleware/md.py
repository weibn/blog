from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from rbac import config
import re

class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request,*args,**kwargs):
        #查询白名单，如是config白名单文件里的url则不做权限限定
        for pattern in config.VALID_URL:
            if re.match(pattern,request.path_info):
                return None

        #特殊url需在url后面添加如?url=get借此查询是否有权限
        action = request.GET.get('md')
        #对于登录用户会有写入'user_permission_dict' session的操作 如果没有则视为未登录
        user_permission_dict = request.session.get('user_permission_dict')
        if not user_permission_dict:
            return  HttpResponse('无权限')

        #设定一个标志位
        flag = False
        #由session取到写入的权限表，k为url, v为[get,post....]类似的列表
        for k,v in user_permission_dict.items():
        #通过正则匹配当前请求的url是否在用户权限url中，以及请求的方式是否在在用户权限操作中，都满足的时候才会让用户访问
            if re.match(k,request.path_info):
                if action in v:
                    flag = True
                    break
        if not flag:
            return HttpResponse('无权限')


