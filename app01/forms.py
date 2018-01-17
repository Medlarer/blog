__author__ = 'Arai'


from django.forms import Form,widgets,forms,fields
from django import forms
from django.forms import ValidationError
from app01 import models


class RegForm(forms.Form):
    """
    注册表单
    """
    username=forms.CharField(
        min_length=2,
        max_length=8,
        error_messages={
            "required":"用户名不能为空",
        },
        widget=widgets.TextInput(attrs={"class":"form-control","placeholder":"用户名"})
    )

    password=forms.CharField(
        min_length=4,
        max_length=12,
        error_messages={
            "required":"密码不能为空",
        },
        widget=widgets.PasswordInput(attrs={"class":"form-control","placeholder":"密码"})
    )

    reg_pwd = forms.CharField(
        min_length=4,
        max_length=12,
        error_messages={
            "required": "密码不能为空",
        },
        widget=widgets.PasswordInput(attrs={"class":"form-control","placeholder":"确认密码"})
    )

    email=forms.EmailField(error_messages={"required":"邮箱不能为空"},
       widget=widgets.EmailInput(attrs={"class":"form-control","placeholder":"邮箱"})
    )

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    def clean_username(self):
        """
        钩子函数，验证用户名
        :return:
        """
        user=models.UserInfo.objects.filter(username=self.cleaned_data.get("username"))
        if not user:
            return self.cleaned_data.get("username")
        else:
            raise ValidationError("用户名已存在")

    def clean_password(self):
        pwd=self.cleaned_data.get("password")
        if pwd.isdigit():
            raise  ValidationError("密码不能权威数字")
        else:
            return pwd

    # def clean_validCode(self):
    #     if self.cleaned_data.get("validCode")==self.request.session.get("keepValid"):
    #         return self.cleaned_data.get("validCode")
    #     else:
    #         raise ValidationError("验证码错误")

    def clean(self):
        if self.cleaned_data.get("password")==self.cleaned_data.get("reg_pwd"):
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致")

from app01.plugins import xss_plugin

class ArticleForm(forms.Form):
    """
    后台管理
    """
    title=forms.CharField(max_length=20,
                          error_messages={
                              "required":"标题不能为空",})
    content = forms.CharField(max_length=20,
                            error_messages={
                                "required": "标题不能为空",},
                              widget=widgets.Textarea())

    def clean_content(self):
        html_str=self.cleaned_data.get("content")
        clean_content=xss_plugin.filter_xss(html_str)
        self.cleaned_data["content"]=clean_content

        return self.clean_data.get("content")


