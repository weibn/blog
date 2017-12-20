from app01 import models
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Count
class LoginInfo(Form):
    username = fields.CharField(required=True,min_length=6,max_length=12,strip=True,
        widget=widgets.TextInput(attrs={"class":"form-control","placeholder":"请输入用户名","name":"username"}),
        # validators = [RegexValidator(r'^.(\S){6,10}$', '帐号不能包含空白字符'),],
        error_messages = {'required': '帐号不能为空!','min_length': '帐号最少为6个字符',
       'max_length': '帐号最多不超过为12个字符!', },)
    def clean_username(self):
        v = self.cleaned_data['username']
        if not models.UserInfo.objects.filter(username=v).count():
# 判断获取到的user在数据库已经存在，主动抛出异常，内部捕获到异常则将异常添加到obj.errors里。
            raise ValidationError('用户名或密码错误！')
        return self.cleaned_data['username']
    password = fields.CharField(required=True,min_length=6,max_length=12,strip=True,
        widget=widgets.PasswordInput(
            attrs={"class": "form-control", "placeholder": "请输入密码",
                   "name": "password"},render_value=True),
        # validators = [RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),],
        error_messages = {'required': '密码不能为空!','min_length': '密码最少为6个字符',
       'max_length': '密码最多不超过为12个字符!', },)

class RegForm(Form):
    username = fields.CharField(
    widget = widgets.TextInput(attrs={'class': "form-control", 'placeholder': '用户名为6-12个字符','name':'username'}),
    required=True,
    min_length = 6,
    max_length = 12,
    error_messages = {'required': '用户名不能为空',
        'min_length': '用户名最少为6个字符',
        'max_length': '用户名最不超过为12个字符'},
             )

    email = fields.EmailField(
    widget = widgets.TextInput(attrs={'class': "form-control", 'placeholder': '请输入邮箱','name':'email'}),
    error_messages = {'required': '邮箱不能为空',
         'invalid':'请输入正确的邮箱格式'},
         )

    password = fields.CharField(
    widget = widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请输入密码','name':'password'},
                                   render_value=True),
    required = True,
    min_length = 6,
    max_length = 12,
    # strip = True,
    # validators = [
    #    # 下面的正则内容一目了然，我就不注释了
    #       RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
    #       RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
    #       RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
    #       RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
    #  ],  # 用于对密码的正则验证
    error_messages = {'required': '密码不能为空!',
                      'min_length': '密码最少为6个字符',
    'max_length': '密码最多不超过为12个字符!', },)

    pwd_again = fields.CharField(
    widget = widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请再次输入密码!','name':'pwd_again'}
                                   , render_value=True),
    required = True,
    strip = True,
    error_messages = {'required': '请再次输入密码!', }
        )

    nickname = fields.CharField(max_length=20,
        widget=widgets.TextInput(
            attrs={'class': "form-control", 'placeholder': '请输入昵称', 'name': 'nickname'}),)

    #验证码
    code = fields.CharField(widget=widgets.TextInput(
                            attrs={'class': "form-control", 'placeholder': '验证码'}), )

    avatar = fields.CharField(
        required=True,
        widget = widgets.TextInput(attrs={"style":"display: none"}),
        error_messages = {'required': '头像上传未成功!'})

    # widget=widgets.FileInput(attrs={'name': 'avatar'}),

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_code(self):
        session_code = self.request.session.get('code')
        input_code = self.cleaned_data.get('code')
        if session_code == input_code:
            return input_code
        raise ValidationError('验证码错误')

    def clean_username(self):
# 对username的扩展验证，查找用户是否已经存在
        username = self.cleaned_data.get('username')
        users = models.UserInfo.objects.filter(username=username).count()
        if users:
            raise ValidationError('用户已经存在！')
        return self.cleaned_data['username']

    def clean_email(self):
              # 对email的扩展验证，查找用户是否已经存在
        email = self.cleaned_data.get('email')
        email_count = models.UserInfo.objects.filter(email=email).count()  # 从数据库中查找是否用户已经存在
        if email_count:
            raise ValidationError('该邮箱已经注册！')
        return self.cleaned_data['email']

    def clean_pwd_again(self):  # 查看两次密码是否一致
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('pwd_again')
        if password1 and password2:
            if password1 != password2:
                  # self.error_dict['pwd_again'] = '两次密码不匹配'
                raise ValidationError('两次密码不匹配！')

    # def clean(self):
    #           # 是基于form对象的验证，字段全部验证通过会调用clean函数进行验证
    #     self._clean_new_password2()  # 简单的调用而已

class ArticleForm(Form):
    title = fields.CharField(max_length=64,
        widget=widgets.TextInput(attrs={'class':"form-control"}))

    summary = fields.CharField(max_length=128,
        widget=widgets.Textarea(attrs={'class':"form-control","rows":"3"}))
    content = fields.CharField(
        widget=widgets.Textarea(attrs={'class':"form-control",'id':'c1'}))

    article_type_id = fields.ChoiceField(
        choices=models.Article.type_choices,
        initial=1,
        widget=widgets.RadioSelect(attrs={'class':'radio-inline'})
    )
    category_id = fields.ChoiceField(
        initial=1,
        widget=widgets.RadioSelect(attrs={'class':'radio-inline'}))

    tags_id = fields.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}))

    def clean_content(self):
        old = self.cleaned_data['content']
        from utils.xss import xss
        return xss(old)

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request
        nid = self.request.session.get('user_id')
        category_list = models.Article.objects.filter(blog__user_id=nid).values_list('category__nid',
                         'category__title').distinct()
        self.fields['category_id'].choices = category_list

        tag_list = models.Article.objects.filter(blog__user_id=nid).values_list('tags__nid', 'tags__title').distinct()
        self.fields['tags_id'].choices = tag_list