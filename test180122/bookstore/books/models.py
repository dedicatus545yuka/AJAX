from django.db import models
from DB.BaseModel import BaseModel
from books.enums import *
from tinymce.models import HTMLField
# Create your models here.
class BooksManager(models.Manager):
	'''商品模型管理类'''
	def get_books_by_type(self,type_id,limit = None,sort='default'):
		'''根据商品类型id查询商品信息'''
		if sort == 'new': # 按照创建时间进行排序
			order_by = ('-create_time',) # 元组  '-' == 代表的是降序排列
		elif sort == 'hot': # 按照商品销量进行排序
			order_by = ('-sales',)
		elif sort == 'price': # 按照商品价格进行排序
			order_by = ('price',)
		else:
			order_by = ('-pk',) # 按照primary_key 降序排列

		# 查询数据 -- sql 查询语句
		books_li = self.filter(type_id=type_id).order_by(*order_by) # ‘*’把元组展开

		# 查询结果集的限制
		if limit:
			books_li = books_li[:limit] # 切片截取数据

		return books_li

	def get_books_by_id(self,books_id):
		'''根据商品id查询商品信息'''
		try:
			books = self.get(id= books_id)
		except self.model.DoesNotExist:
			books = '没有您要找的书'

		return books


class Books(BaseModel):
	'''商品模型类'''
	book_type_choices = ((k,v) for k,v in BOOK_TYPE.items()) # 迭代器遍历出数据
	status_choices = ((k, v) for k, v in STATUS_CHOICE.items())

	# 对于django来讲，该字段值在 -32768 至 32767这个范围内对所有可支持的数据库都是安全的。
	type_id = models.SmallIntegerField(default=PYTHON,choices=book_type_choices,verbose_name='商品种类')
	status = models.SmallIntegerField(default=ONLINE,choices=status_choices,verbose_name='商品状态')

	name = models.CharField(max_length=20,verbose_name='商品名称')
	desc = models.CharField(max_length=128,verbose_name='商品简介')
	price = models.DecimalField(decimal_places=2,max_digits=10,verbose_name='商品价格')
	unit = models.CharField(max_length=20,verbose_name='商品单位')
	stock = models.IntegerField(default=1,verbose_name='商品库存')
	sales = models.IntegerField(default=0,verbose_name='商品销量')
	detail = HTMLField(verbose_name='商品详情')
	image = models.ImageField(upload_to='books',verbose_name='商品图片')

	object = BooksManager()

	class Meta:
		db_table = 's_books'
