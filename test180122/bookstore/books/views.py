from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from books.models import Books
from books.enums import *
from django.http import HttpResponse
from PIL import Image,ImageDraw,ImageFont
import random
import io
from django_redis import get_redis_connection

# Create your views here.

def index(request):
	'''显示首页'''
	# 查询每个种类的3个新品信息和4个销量最好的信息
	python_new = Books.object.get_books_by_type(PYTHON,3,sort='new')
	python_hot = Books.object.get_books_by_type(PYTHON,4,sort='hot')

	javascript_new = Books.object.get_books_by_type(JAVASCRIPT,3,sort='new')
	javascript_hot = Books.object.get_books_by_type(JAVASCRIPT,4,sort='hot')

	algorithms_new = Books.object.get_books_by_type(ALGORITHMS,3,sort='new')
	algorithms_hot = Books.object.get_books_by_type(ALGORITHMS,4,sort='hot')

	machinelearning_new = Books.object.get_books_by_type(MACHINELEARNING,3,sort='new')
	machinelearning_hot = Books.object.get_books_by_type(MACHINELEARNING,4,sort='hot')

	operatingsystem_new = Books.object.get_books_by_type(OPERATINGSYSTEM,3,sort='new')
	operatingsystem_hot = Books.object.get_books_by_type(OPERATINGSYSTEM,4,sort='hot')

	database_new = Books.object.get_books_by_type(DATABASE,3,sort='new')
	database_hot = Books.object.get_books_by_type(DATABASE,4,sort='hot')

	# 定义模板上下文
	context = {
		'python_new':python_new,
		'python_hot':python_hot,
		'javascript_new':javascript_new,
		'javascript_hot':javascript_hot,
		'algorithms_new':algorithms_new,
		'algorithms_hot':algorithms_hot,
		'machinelearning_new':machinelearning_new,
		'machinelearning_hot':machinelearning_hot,
		'operatingsystem_new':operatingsystem_new,
		'operatingsystem_hot':operatingsystem_hot,
		'database_new':database_new,
		'database_hot':database_hot,
	}

	# 将数据传去页面
	return render(request,'books/index.html',context)

def detail(request,books_id):
	'''实现页面商品的详情页'''

	# 获取书籍的详细信息
	books = Books.object.get_books_by_id(books_id=books_id)
	if books is None:
		# 商品不存在跳转到主页
		return redirect(reverse('books:index'))

	# 新品推荐
	books_li = Books.object.get_books_by_type(type_id=books.type_id,limit=2,sort='new')

	# 用户登录之后才实现浏览记录功能
	# 每个用户浏览记录对应redis中的一条信息 格式:'history_用户id':[10,9,2,3,4]
	# [9, 10, 2, 3, 4]
	if request.session.has_key('islogin'):
		# 用户已经登录
		conn = get_redis_connection('default')
		key = 'history_%d' % request.session.get('passport_id')

		# 从redis 里面移除books.id 的数据
		conn.lrem(key,0,books.id)
		conn.lpush(key,books.id)

		# 保存最近浏览的5个商品
		conn.ltrim(key,0,4)


	context = {'books':books,'books_li':books_li}

	return render(request,'books/detail.html',context)




