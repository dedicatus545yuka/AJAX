# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from django_redis import get_redis_connection
from utils.decorators import login_required

# 要用到前端传来的数据 -- 商品id 商品数目 books_id books_count

def cart_add(request):
	'''向购物车中添加数据'''

	# 判断用户是否登录状态
	if not request.session.has_key('islogin'):
		# 没有登录
		return JsonResponse({'rec':0,'errmsg':'请先登录'})

	# 接受数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count') # 数量

	# 进行数据校验
	if not all([books_id,books_count]):
		return JsonResponse({'rec':1,'errmsg':'数据不完整'})

	book = Books.object.get_books_by_id(books_id)
	if book is None:
		return JsonResponse({'rec':2,'errmsg':'数据不存在'})

	try:
		count = int(books_count)
	except:
		return JsonResponse({'rec':3,'errmsg':'商品数量不合法'})

	# 添加商品到购物车
	# 每个用户的购物车记录用一条hash数据保存，格式:cart_用户id: 商品id 商品数量
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id') # users/views/login --> passport_id

	res = conn.hget(cart_key,books_id) # 根据用户id和书的id来找到数据
	if res is None:
		# 如果用户的购车中没有添加过该商品，则添加数据
		res = count
	else:
		# 如果用户的购车中已经添加过该商品，则累计商品数目
		res = int(res) + count

	# 判断商品的库存
	if res>book.stock:
		return JsonResponse({'rec':4,'errmsg':'库存不足'})
	else:
		conn.hset(cart_key,books_id,res) # 向数据库中增加数据

	return JsonResponse({'res':5}) # 返回结果

def card_count(request):
	'''获取用户购物车中商品的数目'''
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0})

	# 计算用户购物车商品的数量
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	res = 0
	res_list = conn.hvals(cart_key)

	for i in res_list:
		res += int(i)

	return JsonResponse({'res':res})

@login_required
def card_show(request):
	'''显示用户购物车页面'''
	# 获取用户购物车的记录
	passport_id = request.session.get('passport_id')
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	res_dict = conn.hgetall(cart_key)

	books_li = []
	# 保存所有商品的总数
	total_count = 0
	# 保存所有商品的价钱
	total_price = 0

	# 遍历获取商品的信息
	for id,count in res_dict.items():
		# 根据id获得商品的信息
		books = Books.object.get_books_by_id(books_id=id)

		# 保存商品的数量
		books.count = count

		# 保存商品的小计
		books.amount = int(count)*books.price # ???没有什么用

		# 把商品放入列表
		books_li.append(books)

		total_count += int(count)
		total_price += int(count)* books.price

	context = {
		'books_li':books_li,
		'total_count':total_count,
		'total_price':total_price,
	}

	return render(request,'cart/cart.html',context)

def cart_del(request):
	'''删除购物车中商品的内容'''
	# 前端传过来的参数: 商品ID , books_id
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	# 接收数据
	books_id = request.POST.get('books_id')

	# 校验商品是否存放
	if not all([books_id]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.object.get_books_by_id(books_id=books_id)

	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	# 删除购物车商品信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	conn.hdel(cart_key,books_id)

	# 返回结果

	return JsonResponse({'res':3})

def cart_update(request):
	'''更新购物车商品数目'''
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	# 接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	# 数据的校验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.object.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try:
		books_count = int(books_count)
	except:
		return JsonResponse({'res':3,'errmsg':'商品必须为数字'})

	# 判断库存

	if books_count > books.stock:
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})

	# 更新操作

	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	conn.hset(cart_key,books_id,books_count)

	return JsonResponse({'res':5})










