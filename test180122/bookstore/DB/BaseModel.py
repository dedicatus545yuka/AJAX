from django.db import models

class BaseModel(models.Model):
	'''模型抽象基类'''
	is_delete = models.BooleanField(default=False,verbose_name='逻辑删除标志')
	create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建的时间')
	update_time = models.DateTimeField(auto_now=True,verbose_name='更新的时间')

	class Meta:
		abstract = True #抽象