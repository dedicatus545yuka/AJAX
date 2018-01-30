from django.shortcuts import render,redirect
from utils.decorators import login_required
from django.core.urlresolvers import reverse
from users.models import Address
from books.models import Books
from django_redis import get_redis_connection
from django.db	import transaction #??? 事务
from django.http import JsonResponse
from order.models import OrderInfo,OrderGoods
from datetime import datetime

@login_required
def order_place(request):
	'''显示提交订单页面'''
	# 接受数据
	books_ids = request.POST.getlist('books_ids')

	# 校验数据
	if not all([books_ids]):
		# 跳转回购物车页面
		return redirect(reverse('cart:show'))

	# 用户收货地址
	passport_id = request.session.get('passport_id')
	addr = Address.object.get_default_address(passport_id=passport_id)

	# 用户要购买的商品的信息
	books_li = []

	# 商品的总数目和总金额
	total_count = 0
	total_price = 0

	# 与redis库连接
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id

	for id in books_ids:
		# 根据id获取商品信息
		books = Books.object.get_books_by_id(books_id=id)
		# 从redis获取用户要购买的商品的数量
		count = conn.hget(cart_key,id)
		books.count = count
		# 计算商品中的小计
		amount = int(count) * books.price
		books.amount = amount
		books_li.append(books)
		# 累积计算商品的总数目和总金额
		total_count += int(count)
		total_price += books.amount

	# 商品运费和实付款
	transit_price = 10
	total_pay = total_price + transit_price

	print('-----------------------------')
	print(books_ids)
	# 字符串的组合
	books_ids = ','.join(books_ids)
	print(books_ids)

	# 组织模板上下文
	context = {
		'addr':addr,
		'books_li':books_li,
		'total_count':total_count,
		'total_price':total_price,
		'total_pay':total_pay,
		'transit_price':transit_price,
		'books_ids':books_ids,
	}

	# 使用模板
	return render(request,'order/place_order.html',context)

@transaction.atomic
def order_commit(request):
	'''提交订单--》生成订单信息'''
	# 验证用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	# 接受数据
	addr_id = request.POST.get('addr_id')
	books_ids = request.POST.get('books_ids')
	pay_method = request.POST.get('pay_method')

	# 进行数据校验
	if not all([addr_id,books_ids,pay_method]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	try:
		addr = Address.object.get(id=addr_id)

	except:
		return JsonResponse({'res':2,'errmsg':'地址信息错误'})

	if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
		return JsonResponse({'res':3,'errmsg':'不支持的支付方式'})

	# 订单创建
	# 组织订单信息
	passport_id = request.session.get('passport_id')

	# 订单的信息 --》 日期时间+passport_id
	order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)

	# 运费
	transit_price = 10
	# 商品总数和商品总价格
	total_count = 0
	total_price = 0

	# 创建一个保存点
	sid = transaction.savepoint()

	try:
		order = OrderInfo.objects.create(
			order_id = order_id,
			passport_id = passport_id,
			addr_id = addr_id,
			total_price = total_price,
			total_count = total_count,
			transit_price = transit_price,
			pay_method = pay_method,
		)
		# 向订单商品表中添加订单商品的记录
		books_ids = books_ids.split(',')
		conn = get_redis_connection('default')
		cart_key = 'cart_%d' % passport_id

		# 遍历获取用户购买的商品信息
		for id in books_ids:
			books = Books.object.get_books_by_id(books_id=id)
			if books is None:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res':4,'errmsg':'商品信息错误'})

			# 获取商品的数量
			count = conn.hget(cart_key,id)

			# 判断商品的库存
			if int(count) > books.stock:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res':5,'errmsg':'商品库存不足'})

			# 创建一条订单商品信息
			OrderGoods.objects.create(
				order_id = order_id,
				count = count,
				books_id = id,
				price = books.price,
			)

			# 增加商品销量，减小商品库存
			books.sales += int(count)
			books.stock -= int(count)
			books.save()

			# 累计计算出商品的总数量和商品的总额
			total_count += int(count)
			total_price += int(count) * books.price

		# 更新订单商品的总数目和总金额
		order.total_price = total_price
		order.total_count = total_count
		order.save()

	except Exception as info:
		# 操作数据库出错，进行回滚操作
		print(info)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'res':7,'errmsg':'服务器错误'})

	# 清除购物车对应记录
	conn.hdel(cart_key,*books_ids)

	# 事务提交
	transaction.savepoint_commit(sid)

	# 返回应答
	return JsonResponse({'res':6})





