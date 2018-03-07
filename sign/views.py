from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

# Create your views here.
def index(request):
	return render(request,"index.html")

def login_action(request):
	if request.method=='POST':
		username=request.POST.get('username','')
		password=request.POST.get('password','')
		user=auth.authenticate(username=username,password=password)
		if user is not None:
			auth.login(request,user)
			response=HttpResponseRedirect('/event_manage/')
			request.session['user']=username#将session信息记录在浏览器
			#response.set_cookie('user',username,3600)#添加浏览器cookie,cookie名user，由用户在登录页上输入的用户名admin，cookie在浏览器中的保持时间			
			return response
		else:
			return render(request,'index.html',{'error':'username or password error!'})

@login_required
def event_manage(request):
	event_list=Event.objects.all()#获取所有数据
	username=request.session.get('user','')#读取浏览器session
	return render(request,'event_manage.html',{'user':username,'events':event_list})

@login_required
def guest_manage(request):
	guest_list=Guest.objects.all()#获取所有数据
	username=request.session.get('user','')#读取浏览器session
	paginator=Paginator(guest_list,10)
	page=request.GET.get('page')#获得页码数请求
	try:
		contacts=paginator.page(page)#翻到该页
	except PageNotAnInteger:
		contacts=paginator.page(1)
	except EmptyPage:
		contacts=paginator.page(paginator.num_pages)
	return render(request,'guest_manage.html',{'user':username,'guests':contacts})

@login_required
def search_name(request):
	username=request.session.get('user','')#获取当前登录的用户名
	search_name=request.GET.get("name","")#获取搜索关键字
	event_list=Event.objects.filter(name__contains=search_name)#从数据库寻找匹配的数据
	return render(request,"event_manage.html",{"user":username,"events":event_list})#渲染页面，并传递参数

@login_required
def search_guest_name(request):
	username=request.session.get('user','')#获取当前登录的用户名
	search_guest_name=request.GET.get("name","")#获取搜索关键字
	guest_list=Guest.objects.filter(realname__contains=search_guest_name)#从数据库寻找匹配的数据
	return render(request,"guest_manage.html",{"user":username,"guests":guest_list})#渲染页面，并传递参数
#签到页面
@login_required
def sign_index(request,eid):
	event=get_object_or_404(Event,id=eid)
	return render(request,'sign_index.html',{'event':event})
#签到操作
@login_required
def sign_index_action(request,eid):
	event=get_object_or_404(Event,id=eid)
	phone=request.POST.get('phone','')#获取签到手机号码
	print(phone)
	result=Guest.objects.filter(phone=phone)#根据手机号查找用户
	#如果没有找到用户，提示手机号错误
	if not result:
		return render(request,'sign_index.html',{'event':event,'hint':'phone error'})
	#如果手机号和发布会id都不对，提示手机号与发布会不匹配
	result=Guest.objects.filter(phone=phone,event_id=eid)
	if not result:
		return render(request,'sign_index.html',{'event':event,'hint':'event id or phone error'})

	result=Guest.objects.filter(phone=phone)
	if result[0].sign:
		return render(request,'sign_index.html',{'event':event,'hint':'user has sign in'})

	else:
		result=Guest.objects.filter(phone=phone,event_id=eid).update(sign='1')
		return render(request,'sign_index.html',{'event':event,'hint':'sign in success','guest':result})

@login_required
def logout(request):
	auth.logout(request)
	response=HttpResponseRedirect('/index/')
	return response