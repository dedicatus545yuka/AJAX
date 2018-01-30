from django.db import models
from DB.BaseModel import BaseModel
from hashlib import sha1
# Create your models here.
def get_hash(str):
	'''去一个字符串的哈希值'''
	sh = sha1()
	# 转码
	sh.update(str.encode('utf8'))
	return sh.hexdigest()

class PassportManager(models.Manager):
	'''用户管理器'''
	def add_one_passport(self,username,password,email):
		# 添加一个用户信息
		passport = self.create(username=username,password=get_hash(password),email=email)
		return passport

	def get_one_passport(self,username,password):
		# 获取一个用户的信息
		try:
			passport = self.get(username=username,password=get_hash(password))
		except self.model.DoesNotExist:
			passport = None

		return passport

class Passport(BaseModel):
	'''用户模型类'''
	username = models.CharField(max_length=20,verbose_name='用户名')
	password = models.CharField(max_length=40,verbose_name='密码')
	email = models.EmailField(verbose_name='邮箱')
	is_active = models.BooleanField(default=False,verbose_name='激活状态')

	# 用户表的管理器
	object = PassportManager()

	class Meta:
		db_table = 's_user_account' # 给数据库的表单命名

# 用户中心的管理器 --
class AddressManager(models.Manager):
	'''地址模型管理类'''
	def get_default_address(self,passport_id):
		'''查询指定用户的默认地址'''
		try:
			addr = self.get(passport_id=passport_id,is_default=True)
		except self.model.DoesNotExist:
			# 没有地址
			addr = None
		return addr

	def add_one_address(self,passport_id,recipient_name,recipient_addr,zip_code,recipient_phone):
		'''添加收货地址'''
		# 判断用户是否有收货地址
		addr = self.get_default_address(passport_id=passport_id)

		if addr:
			# 有默认收货地址
			is_default = False
		else:
			# 不存在默认收货地址
			is_default = True

		# 添加一个地址
		addr = self.create(
			passport_id=passport_id,
			recipient_name=recipient_name,
			recipient_addr=recipient_addr,
			zip_code=zip_code,
			recipient_phone=recipient_phone,
			is_default=is_default,
		)
		return addr

# 用户中心 --
class Address(BaseModel):
	'''地址模型类'''
	recipient_name = models.CharField(max_length=20,verbose_name='收件人')
	recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
	zip_code = models.CharField(max_length=6,verbose_name='邮政编码')
	recipient_phone = models.CharField(max_length=11,verbose_name='联系电话')
	is_default = models.BooleanField(default=False,verbose_name='是否默认')
	passport = models.ForeignKey('Passport',verbose_name='账户')

	object = AddressManager()

	class Meta:
		db_table = 's_user_address'

