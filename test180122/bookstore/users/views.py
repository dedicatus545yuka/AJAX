from django.shortcuts import render,redirect
from django.http import JsonResponse
from users.models import Passport,Address
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from PIL import Image,ImageDraw,ImageFont
import random
import io
import re
from utils.decorators import login_required
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from books.models import Books
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from users.tasks import send_active_mail

def register(request):
	'''显示用户注册页面'''
	return render(request,'users/register.html')

def register_handle(request):
	'''进行用户注册处理'''
	# 获取从页面传来的数据
	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')

	# 进行注册数据的校验
	if not all([username,password,email]):
		# 数据不能为空
		return render(request,'users/register.html',{'errmsg': '数据不能为空'})
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
		# 邮箱不正确
		return render(request,'users/register.html',{'errmsg': '邮箱格式错误'})
	# 往数据库中添加用户注册的账户信息 -- 使用用户管理器
	passport = Passport.object.add_one_passport(username=username,password=password,email=email)

	# 生成激活的token itsdangerous
	serializer = Serializer(settings.SECRET_KEY, 3600)
	token = serializer.dumps({'confirm': passport.id})  # 返回bytes
	token = token.decode()

	# 给用户的邮箱发激活邮件
	# send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email],
	# html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
	send_active_mail.delay(token, username, email)

	# 注册完成返回注册的页面 -- 改成主页面
	return redirect(reverse('books:index'))

def register_active(request, token):
    '''用户账户激活'''
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        passport_id = info['confirm']
        # 进行用户激活
        passport = Passport.objects.get(id=passport_id)
        passport.is_active = True
        passport.save()
        # 跳转的登录页
        return redirect(reverse('user:login'))
    except SignatureExpired:
        # 链接过期
        return HttpResponse('激活链接已过期')

def login(request):
	'''显示登录界面'''
	username = request.COOKIES.get('username','')
	checked = ''

	context = {
		'username':username,
		'checked':checked
	}

	return render(request,'users/login.html',context)

def login_check(request):
	'''登录信息的校验'''
	# 获取数据
	username = request.POST.get('username')
	password = request.POST.get('password')
	remember = request.POST.get('remember')
	verifycode = request.POST.get('verifycode')

	# 校验数据
	if not all([username,password,remember,verifycode]):
		# 数据是否为空
		return JsonResponse({'res':2})

	if verifycode.upper() != request.session['verifycode']:
		# 验证码错误
		return JsonResponse({'res':2})

	# 根据用户名和密码查找数据库中的账号信息
	passport = Passport.object.get_one_passport(username=username,password=password)

	if passport:
		# 用户名和密码正确
		next_url = request.session.get('url_path',reverse('books:index'))
		jres = JsonResponse({'res':1,'next_url':next_url}) # 返回Json格式的数据给前端
		# if not passport.is_active:
		# 	# 请通过邮箱激活账户
		# 	return JsonResponse({'res':3})

		# 判断是否需要记住用户名
		if remember == 'true':
			jres.set_cookie('username',username,max_age=7*24*3600) # 记住用户名7天
		else:
			jres.delete_cookie('usrname')

		# 记住用户的登录状态
		request.session['username']= username
		request.session['islogin']= True
		request.session['passport_id']= passport.id

		return jres

	else:

		return JsonResponse({'res':0}) # 用户名或者密码错误

def logout(request):
	'''用户退出登录'''
	# 清空用户的session数据
	request.session.flush()
	# 返回到主页
	return redirect(reverse('books:index'))


def verifycode(request):
	'''验证码图形模块'''
	# 定义变量，用于画面的背景色、宽、高
	print('===========')
	try:
		bgcolor = (random.randrange(20, 100), random.randrange(
			20, 100), 255)
		width = 100
		height = 25
		# 创建画面对象
		im = Image.new('RGB', (width, height), bgcolor)
		# 创建画笔对象
		draw = ImageDraw.Draw(im)
		# 调用画笔的point()函数绘制噪点
		for i in range(0, 100):
			xy = (random.randrange(0, width), random.randrange(0, height))
			fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
			draw.point(xy, fill=fill)
		# 定义验证码的备选值
		str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
		# 随机选取4个值作为验证码
		rand_str = ''
		for i in range(0, 4):
			rand_str += str1[random.randrange(0, len(str1))]
		# 构造字体对象
		font = ImageFont.truetype("/usr/share/fonts/truetype/Gargi/Gargi.ttf", 15)
		# 构造字体颜色
		fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
		# 绘制4个字
		draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
		draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
		draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
		draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
		# 释放画笔
		del draw
		# 存入session，用于做进一步验证
		request.session['verifycode'] = rand_str
		# 内存文件操作
		buf = io.BytesIO()
		# 将图片保存在内存中，文件类型为png
		im.save(buf, 'png')
		# 将内存中的图片数据返回给客户端，MIME类型为图片png
		print("--------------------")
	except Exception as e:
		print('e: ', e)
	return HttpResponse(buf.getvalue(), 'image/png')

@login_required # 把下面函数扔进装饰的函数里
def user(request):
	'''用户中心--信息页'''
	passport_id = request.session.get('passport_id')
	# 获取用户的基本信息
	addr = Address.object.get_default_address(passport_id=passport_id)

	# 获取用户最近浏览的数据
	conn = get_redis_connection('default')
	key = 'history_%d' % passport_id

	# 取出用户最近浏览的5个id
	history_li = conn.lrange(key,0,4)



	books_li = []

	for id in history_li:
		books = Books.object.get_books_by_id(books_id=id)
		books_li.append(books)

	context = {
		'addr':addr,
		'books_li':books_li,
		'page':'user'
	}
	return render(request,'users/user_center_info.html',context)

@login_required
def address(request):
	'''用户中心--地址页'''
	#获取登录用户的id
	passport_id = request.session.get('passport_id')

	if request.method == 'GET':
		# 查询用户的默认地址
		addr = Address.object.get_default_address(passport_id=passport_id)
		return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})

	else:
		# 添加收货地址
		recipient_name = request.POST.get('username')
		recipient_addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		recipient_phone = request.POST.get('phone')

		# 进行校验
		if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
			return render(request,'users/user_center_site.html',{'errmsg':'参数不能为空！'})

		Address.object.add_one_address(
			passport_id=passport_id,
			recipient_name=recipient_name,
			recipient_addr=recipient_addr,
			zip_code=zip_code,
			recipient_phone=recipient_phone,
		)

		return redirect(reverse('user:address'))

@login_required
def order(request):
	'''用户中心--》订单页'''
	# 查询用户的订单信息
	passport_id = request.session.get('passport_id')

	# 获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)

	# 遍历获取订单的商品信息
	# order->OrderInfo实例对象
	for order in order_li:
		# 根据订单id查询订单商品信息
		order_id = order.order_id
		order_books_li = OrderGoods.objects.filter(order_id=order_id)

		# 计算商品的小计
		# order_books ->OrderBooks实例对象
		for order_books in order_books_li:
			count = order_books.count
			price = order_books.price
			amount = count * price
			# 保存订单中每一个商品的小计
			order_books.amount = amount

		# 给order对象动态增加一个属性order_goods_li,保存订单中商品的信息
		order.order_books_li = order_books_li

	context = {
		'order_li': order_li,
		'page': 'order'
	}

	return render(request,'users/user_center_order.html',context)






