from django.conf.urls import url
from cart import views

urlpatterns = [
	url(r'^add/$',views.cart_add,name='add'), # 添加商品
	url(r'^count/$', views.card_count, name='count'),# 计算商品数量
	url(r'^$',views.card_show,name='show'),# 显示购物车信息
	url(r'^del/$', views.cart_del, name='delete'),  # 从购物车中删除商品信息
	url(r'^update/$', views.cart_update, name='update'),  # 更新购物车的商品信息
]