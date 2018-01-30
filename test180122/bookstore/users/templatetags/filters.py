from django.template import Library

# 创建一个Library对象
register = Library()

# 创建一个过滤器的函数
@register.filter
def order_status(status):
	'''返回订单信息对应的字符串'''
	print('==========,', status)
	status_dict = {
		1: "待支付",
		2: "待发货",
		3: "待收货",
		4: "待评价",
		5: "已完成",
	}
	return status_dict[status]
