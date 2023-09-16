from django.shortcuts import render,redirect

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from django.utils.safestring import mark_safe

from app01 import models
from app01.utils.pagination import Pagination

# Create your views here.
def depart_list(request):
    """部门列表"""
    #去数据库中获取所有的部门列表
    #[对象],[对象],[对象]
    queryset = models.Department.objects.all()

    #将queryset传给前端，前端写循环show出来
    return render(request,'depart_list.html',{'queryset':queryset})

def depart_add(request):
    """添加部门"""
    if request.method == "GET":
        return render(request,'depart_add.html')

    #获取用户POST的数据
    title = request.POST.get("title")
    #存入数据库
    models.Department.objects.create(title=title)
    #重定向部门列表页面
    return redirect("/depart/list/")

def depart_delete(request):
    """删除部门"""
    #获取ID
    #http://127.0.0.1:8000/depart/delete/?nid=1
    nid = request.GET.get('nid')
    #执行删除
    models.Department.objects.filter(id=nid).delete()
    #重定向回部门列表
    return redirect("/depart/list/")

def depart_edit(request,nid):
    """修改部门"""
    if request.method =="GET":
        #根据nid获取数据
        row_object = models.Department.objects.filter(id=nid).first()  # 获取的是query类型，所以用first取第一行对象
        return render(request, 'depart_edit.html', {"row_object": row_object})

    #获取用户提交的标题
    title = request.POST.get("title")
    #根据id查找数据库中数据并更新
    models.Department.objects.filter(id=nid).update(title=title)
    # 重定向回部门列表
    return redirect("/depart/list/")

def user_list(request):
    """用户管理"""
    queryset = models.UserInfo.objects.all()
    # for obj in queryset:
    #     print(obj.id,obj.name,obj.account,obj.create_time.strftime("%Y-%m-%d"),obj.get_gender_display(),obj.depart.title)
    #     #get_gender_display() 自动匹配

    return render(request,"user_list.html",{"queryset":queryset})

def user_add(request):
    """添加用户(原始方法)"""
    if request.method == "GET":
        context = {
            'gender_choice':models.UserInfo.gender_choices,
            'depart_list':models.Department.objects.all()
        }
        return render(request,'user_add.html' , context)

    #获取用户提交的数据
    name = request.POST.get('user')
    pwd = request.POST.get('pwd')
    age = request.POST.get('age')
    account = request.POST.get('ac')
    ctime = request.POST.get('ctime')
    gender = request.POST.get('gd')
    depart_id = request.POST.get('dp')

    #添加到数据库
    models.UserInfo.objects.create(name=name,password=pwd,age=age,
                                   account=account,create_time=ctime,
                                   gender=gender,depart_id=depart_id)

    #返回到用户列表页面
    return redirect("/user/list/")

################################ModelForm实例######################################

class UserModelForm(forms.ModelForm):
    name = forms.CharField(min_length=3,label="用户名")

    class Meta:
        model = models.UserInfo
        fields = ["name","password","age","account","create_time","gender","depart"]
        # widgets = {
        #     "name":forms.TextInput(attrs={"class":"form-control"}),
        #     "password": forms.PasswordInput(attrs={"class": "form-control"}),
        #}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
         #循环找到所有插件，添加class=form-control
        for name, field in self.fields.items():
         field.widget.attrs = {"class":"form-control","placeholder":field.label}

def user_model_form_add(request):
    """添加用户（ModelForm版本）"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request,'user_model_form_add.html',{"form":form})

    #用户POST提交数据，数据的校验
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        #如果数据合法，保存到数据库(ModelForm方法)
        # print(form.cleaned_data)
        form.save()
        return redirect('/user/list/')

        #校验失败(在页面上写错误信息)
    return render(request,'user_model_form_add.html',{"form":form})

def user_edit(request, nid):
    """编辑用户"""
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
    # 根据ID去数据库获取要编辑的那一行数据（对象）
        form = UserModelForm(instance=row_object)
        return render(request,'user_edit.html',{"form":form})

    form = UserModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        #默认保存的是用户输入的所有数据
        #如果想在用户输入之外增加一点值  form.instance.字段名 = 值
        form.save()
        return redirect('/user/list/')
    return render(request, 'user_edit.html', {"form": form})

def user_delete(request,nid):
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('/user/list/')

def pretty_list(request):
    """靓号列表"""

    data_dict = {}
    search_data = request.GET.get('q',"")
    if search_data:
        data_dict = {"mobile__contains": search_data}

    # q1 = models.PrettyNum.objects.filter(mobile="15534065210",id=1)
    # print(q1)
    # # <QuerySet [<PrettyNum: PrettyNum object (1)>]>
    #
    # data_dict = {"mobile":"15534065210","id":1}
    # q2 = models.PrettyNum.objects.filter(**data_dict)
    # print(q2)
    # #<QuerySet [<PrettyNum: PrettyNum object (1)>]>

    from app01.utils.pagination import Pagination

    Pagination(request)
    #1.根据哟用户输入的页码计算起止位置
    page = int(request.GET.get('page',1))
    page_size = 10
    start = (page-1) * page_size
    end = page * page_size

    #获取并按级别倒序排列
    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level")[start:end]

    # 数据总条数
    total_count = models.PrettyNum.objects.filter(**data_dict).order_by("-level").count()
    #计算总页码
    total_page_count,div = divmod(total_count,page_size)
    if div:
        total_page_count += 1

    # 页码
    page_str_list = []
    for i in range(1,total_page_count + 1):
        ele = '<li><a href="?page={}">{}</a></li>'.format(i,i)
        page_str_list.append(ele)
    page_string = mark_safe("".join(page_str_list))



    return render(request,'pretty_list.html',{"queryset":queryset,"search_data":search_data,"page_string":page_string})

class PrettyModelForm(forms.ModelForm):

    #验证方式1:
    # mobile = forms.CharField(
    #     label="手机号",
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$','手机号格式错误')],
    # )

    class Meta:

        model = models.PrettyNum
        fields = ['mobile','price','level','status']

        # fields = "__all__"
        #与上面等效

        # exclude = ['level']
        # #除开level


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
         #循环找到所有插件，添加class=form-control
        for name, field in self.fields.items():
         field.widget.attrs = {"class":"form-control","placeholder":field.label}

    #验证方式2（钩子方法）:
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]

        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")

        if len(txt_mobile) != 11:
            #验证失败报错
            raise ValidationError("格式错误")
        #验证成功返回值
        return txt_mobile

class PrettyEditModelForm(forms.ModelForm):

    # mobile = forms.CharField(
    #     label="手机号",
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    # )

    # 锁定不可修改
    # mobile = forms.CharField(disabled=True,label="手机号")
    class Meta:
        model = models.PrettyNum
        fields = ['mobile','price', 'level', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有插件，添加class=form-control
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

    def clean_mobile(self):
        # print(self.instance.pk)

        txt_mobile = self.cleaned_data["mobile"]

        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")

        return txt_mobile

def pretty_add(request):
    """添加靓号"""
    form = PrettyModelForm()
    if request.method == "GET":
        form = PrettyModelForm()
        return render(request, 'pretty_add.html', {"form": form})
    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法，保存到数据库(ModelForm方法)
        # print(form.cleaned_data)
        form.save()
        return redirect('/pretty/list/')
    #校验失败(在页面上写错误信息)
    return render(request,'pretty_add.html',{"form":form})

def pretty_edit(request, nid):
    """编辑靓号"""
    row_object = models.PrettyNum.objects.filter(id=nid).first()

    if request.method == "GET":
    # 根据ID去数据库获取要编辑的那一行数据（对象）
        form = PrettyEditModelForm(instance=row_object)
        return render(request,'pretty_edit.html',{"form":form})

    form = PrettyEditModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        #默认保存的是用户输入的所有数据
        #如果想在用户输入之外增加一点值  form.instance.字段名 = 值
        form.save()
        return redirect('/pretty/list/')
    return render(request, 'pretty_edit.html', {"form": form})

def pretty_delete(request,nid):
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect('/pretty/list/')

def admin(request):
    """管理员列表"""
    queryset = models.Admin.objects.all()

    page_object = Pagination(request,queryset)
    context = {
        'queryset':queryset,
        'page_string':page_object.html(),
    }
    return render(request,'admin_list.html',context)