from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
from PIL import Image,ImageDraw,ImageFont
import random,os,json,datetime
from io import BytesIO
from django.db import transaction
from django.contrib import auth
from app01 import models
from app01.forms import RegForm,ArticleForm
# Create your views here.
from django.db.models import Count,Sum,F





def login(request):
    """
    登录函数
    :param request:
    :return:
    """
    if request.is_ajax():
        username=request.POST.get("username")
        password=request.POST.get("password")
        validCode=request.POST.get("validCode")
        login_response={"is_login":False,"error_msg":None}
        if validCode.upper()==request.session["keepValidCode"].upper():
            user=auth.authenticate(username=username,password=password)
            auth.login(request,user)
            if user:
                login_response["is_login"]=True
            else:
                login_response["error_msg"]="username or password error"
        else:
            login_response["error_msg"]="validCode error"
        return HttpResponse(json.dumps(login_response))
    else:
        return render(request,"login.html")

def log_out(request):
    """
    注销
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect("/login/")

def validCode_img(request):
    """
    获取验证码
    :param request:
    :return:
    """
    #方法1
    # path=os.path.join(settings.BASE_DIR,"static/img/1.png")
    # path=os.path.join(settings.BASE_DIR,"static","img","1.png")
    # with open(path,"rb") as f:
    #     data=f.read()


    #方法2
    # img=Image.new(mode="RGB",size=(120,40),color="green")
    # f=open("validCode.png","wb")
    # img.save(f,"png")
    # with open("validCode.png","rb") as f:
    #     data=f.read()
    #     return HttpResponse(data)


    #方式3
    # img=Image.new(mode="RGB",size=(120,40),color="blue")
    # f=BytesIO()
    # img.save(f,"png")
    # data=f.getvalue()
    # return HttpResponse(data)

    #方式4
    img=Image.new(mode="RGB",size=(120,40),color=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    draw=ImageDraw.Draw(img,"RGB")
    font=ImageFont.truetype("static/font/kumo.ttf",25)
    print(font)
    valid_list=[]
    for i in range(4):
        random_num=str(random.randint(0,9))
        random_lower_alpha=chr(random.randint(65,90))
        random_upper_alpha=chr(random.randint(97,122))
        random_char=random.choice([random_lower_alpha,random_num,random_upper_alpha])
        draw.text((10+i*24,10),random_char,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),font=font)
        valid_list.append(random_char)
    print("ok")
    f = BytesIO()
    img.save(f,"png")
    data=f.getvalue()

    valid_code="".join(valid_list)
    print(valid_code)

    request.session["keepValidCode"]=valid_code
    return HttpResponse(data)

def index(request,**kwargs):
    """
    先验证session
    :param request:
    :return:
    """
    print(kwargs)
    if kwargs:
        article_list=models.Article.objects.filter(site_cate__name=kwargs.get("site_cate"))
    else:
        article_list = models.Article.objects.all()
    web_list=models.WebCate.objects.all()

    return render(request,"index.html",{"article_list":article_list,"web_list":web_list})

def reg(request):
    """
    注册页面
    :param request:
    :return:
    """

    if request.method=="GET":
        form_obj=RegForm(request)
        return render(request,"reg.html",{"form_obj":form_obj})
    else:
        response_dict={"user":None,"error_msg":None}
        print("hello")
        form_obj=RegForm(request,data=request.POST)
        print(request.POST)
        if not form_obj.is_valid():
            response_dict["error_msg"] = form_obj.errors
        else:
            name = form_obj.cleaned_data.get("username")
            pwd = form_obj.cleaned_data.get("password")
            email = form_obj.cleaned_data.get("email")
            avatar_img=request.FILES.get("avatar_img")
            if not avatar_img:
                user_obj = models.UserInfo.objects.create_user(username=name, password=pwd, email=email,
                                                               nickname=name)
            else:
                user_obj = models.UserInfo.objects.create_user(username=name,password=pwd, email=email,
                                                               nickname=name,avatar=avatar_img)
            print(user_obj.avatar, "---")
            response_dict["user"] = user_obj.nickname
        print(response_dict)
        return HttpResponse(json.dumps(response_dict))

def homeSite(request,username,**kwargs):
    current_user=models.UserInfo.objects.filter(username=username).first()
    if not current_user:
        return render(request,"notfound.html")
    current_blog=current_user.blog
    # print(current_blog)
    #找个人博客下面的所有的文章分类和每个分类下的文章个数
    cate_list=models.Category.objects.all().filter(blog=current_blog).annotate(c=Count("article__nid")).values_list("title","c")
    article_list=models.Article.objects.filter(user=current_user)
    ##找个人博客下面的所有的标签分类和每个标签下的文章个数
    tag_list=models.Tag.objects.all().filter(blog=current_blog).annotate(c=Count("article__nid")).values_list("title","c")
    date_list=models.Article.objects.filter(user=current_user).extra(select={"filter_create_time":"strftime('%%Y/%%m',create_time)"}).values_list("filter_create_time").annotate(c=Count("nid"))
    # print(kwargs)
    if kwargs:
        if kwargs.get("condition")=="cate":
            article_list=models.Article.objects.filter(user=current_user,category__title=kwargs.get("para"))
        elif kwargs.get("condition")=="tag":
            article_list=models.Article.objects.filter(user=current_user,tags__title=kwargs.get("para"))
        elif kwargs.get("condition")=="date":
            year,month=kwargs.get("para").split("/")
            print(year,month)
            article_list=models.Article.objects.filter(user=current_user,create_time__year=year,create_time__month=month)
    print(cate_list)
    print(date_list)
    print(article_list)
    return render(request,"homeSite.html",locals())


def article_detail(request,username,article_id):
    """
    文章内容
    :param request:
    :return:
    """
    username=username
    article_obj=models.Article.objects.filter(nid=article_id).first()
    current_user = models.UserInfo.objects.filter(username=username).first()
    if not current_user:
        return render(request, "notfound.html")
    current_blog = current_user.blog
    # print(current_blog)
    # 找个人博客下面的所有的文章分类和每个分类下的文章个数
    cate_list = models.Category.objects.all().filter(blog=current_blog).annotate(c=Count("article__nid")).values_list(
        "title", "c")
    article_list = models.Article.objects.filter(user=current_user)
    ##找个人博客下面的所有的标签分类和每个标签下的文章个数
    tag_list = models.Tag.objects.all().filter(blog=current_blog).annotate(c=Count("article__nid")).values_list("title",
                                                                                                                "c")
    date_list = models.Article.objects.filter(user=current_user).extra(
        select={"filter_create_time": "strftime('%%Y/%%m',create_time)"}).values_list("filter_create_time").annotate(
        c=Count("nid"))
    # print(kwargs)
    comment_list=models.Comment.objects.filter(article_id=article_id)

    return render(request,"article_detail.html",locals())


def up_down(request):
    """
    点赞
    :param request:
    :return:
    """
    response={"is_poll":False}
    article_id=request.POST.get("article_id")
    user_id=request.user.nid
    print(article_id,user_id)
    comment=models.ArticleUp.objects.filter(article_id=article_id,user_id=user_id)
    if comment:
        response["is_poll"]=True
    else:
        models.ArticleUp.objects.create(article_id=article_id,user_id=user_id)
        models.Article.objects.filter(nid=article_id).update(up_count=F("up_count")+1)
    return HttpResponse(json.dumps(response))


def down_up(request):
    """
    踩
    :param request:
    :return:
    """
    response={"is_poll":False}
    article_id=request.POST.get("article_id")
    user_id=request.user.nid
    print(article_id,user_id)
    comment=models.ArticleDown.objects.filter(article_id=article_id,user_id=user_id)
    if comment:
        response["is_poll"]=True
    else:
        models.ArticleDown.objects.create(article_id=article_id,user_id=user_id)
        models.Article.objects.filter(nid=article_id).update(down_count=F("down_count")+1)
    return HttpResponse(json.dumps(response))


def comment(request):
    """
    评论表
    :param request:
    :return:
    """
    response={}
    user_id=request.user.nid
    article_id=request.POST.get("article_id")
    comment_con=request.POST.get("comment_con")
    parent_id=request.POST.get("parent_id")
    #print(article_id,comment_con,parent_id)
    if article_id:
        if parent_id:
            with transaction.atomic():
                comment_obj = models.Comment.objects.create(user_id=user_id, content=comment_con, article_id=article_id,
                                                            parent_comment_id=parent_id)
                response["parent_comment_username"]=comment_obj.parent_comment.user.username
                response["parent_comment_content"]=comment_obj.parent_comment.content
        else:
            with transaction.atomic():
                comment_obj=models.Comment.objects.create(user_id=user_id,content=comment_con,article_id=article_id)
                models.Article.objects.filter(nid=article_id).update(comment_count=F("comment_count")+1)
        response["create_time"] = str(comment_obj.create_time)
        response["comment_id"]=comment_obj.nid
        print(response)

    return HttpResponse(json.dumps(response))


def commentTree(request,article_id):
    """
    评论数
    :param request:
    :return:
    """
    comment_dict={}
    comment_tree=[]
    print("------------",article_id)
    comment_list=models.Comment.objects.filter(article_id=article_id).values("nid","parent_comment","content","user__nickname","create_time","user__avatar")
    # print(comment_list)
    for comment in comment_list:
        comment_dict[comment["nid"]]=comment
        pid=comment.get("parent_comment")
        comment["create_time"]=str(comment["create_time"])
        comment["children_commentList"]=[]
        if pid:
            comment_dict[pid]["children_commentList"].append(comment)
        else:
            comment_tree.append(comment)
    print(comment_tree)
    return HttpResponse(json.dumps(comment_tree))


def backendIndex(request):
    """
    后台管理
    :param request:
    :return:
    """
    user=request.user
    if not user.is_authenticated():
        return redirect("/login/")
    article_list=models.Article.objects.filter(user=user).all()
    return render(request,"backendIndex.html",{"article_list":article_list})

def addArticle(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method=="GET":
        article_forms = ArticleForm()
        return render(request,"addArticle.html",{"article_forms":article_forms})
    else:
        article_forms=ArticleForm(data=request.POST)
        if article_forms.is_valid():
            title=article_forms.cleaned_data.get("title")
            content=article_forms.cleaned_data.get("content")
            article_obj=models.Article.objects.create(title=title,desc=content[30],create_time=datetime.datetime.now(),user=request.user)
            models.ArticleDetail.objects.create(content=content,article=article_obj)
        else:
            pass
        return HttpResponse("添加成功")


def uploadFile(request):
    """
    上传文件
    :param request:
    :return:
    """
    print("POST",request.POST)
    print("Files",request.FILES)
    file_obj=request.FILES.get("imgFile")
    file_name=file_obj.name

    path=os.path.join(settings.MEDIA_ROOT,"article_uploads",file_name)
    with open(path,"wb") as f:
        for i in file_obj.chunks():
            f.write(i)
    response={
        "error":0,
        "url":"/media/article_uploads"+file_name+"/"
    }

    return HttpResponse(json.dumps(response))

def queryTest(request):
    """
    （1）惰性机制
    （2）缓存机制
    :param request:
    :return:
    """
    return HttpResponse("OK")