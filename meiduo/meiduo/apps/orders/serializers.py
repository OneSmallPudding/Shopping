from datetime import timezone, datetime
from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKU
        fields = "__all__"


class OrdersSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    # freight = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = SKU
        fields = "__all__"


class SaveOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ["address", "pay_method", "order_id"]
        read_only_fields = ["order_id", ]
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        # 1 获取用户, 生成order_id address pay_method
        user = self.context["request"].user
        order_id = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user.id
        address = validated_data["address"]
        pay_method = validated_data["pay_method"]
        from django.db import transaction
        with transaction.atomic():
            save_ponit = transaction.savepoint()
            try:
                # 2 生成一个简单的订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 3　获取所有商品
                conn = get_redis_connection("carts")
                cart_dict = conn.hgetall('cart_%s' % user.id)  # 所有商品
                sku_ids = conn.smembers('cart_sele_%s' % user.id)  # 选中的ｉｄ
                cart_count = {}  # 所有选中的商品
                for sku_id, count in cart_dict.items():
                    if sku_id in sku_ids:
                        cart_count[int(sku_id)] = int(count)
                for sku_id in cart_count.keys():
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        # 、获取原始库存
                        old_stock = sku.stock
                        # 判断库存是否足够
                        if cart_count[sku.id] > old_stock:
                            raise serializers.ValidationError("库存不足")
                        # 、获取原始销量
                        old_sales = sku.sales
                        # 更新ｓｋｕ的库存销量
                        new_stock = old_stock - cart_count[sku.id]
                        new_sales = cart_count[sku.id] + old_sales
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()
                        ret = SKU.objects.filter(id=sku.id, stock=old_sales).update(stock=new_stock, sales=new_sales)
                        if ret == 0:
                            continue
                        # 更新ｓｐｕ的总销量
                        sku.goods.sales += cart_count[sku.id]
                        sku.goods.save()
                        # 订单表
                        order.total_amount = cart_count[sku.id] * sku.price
                        order.total_count += cart_count[sku.id]
                        # 4 生成一个商品
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=cart_count[sku.id],
                            price=sku.price
                        )
                        break
                # ５对订单信息进行修改
                order.total_amount += order.freight
                order.save()
            except:
                transaction.savepoint_rollback(save_ponit)
                raise serializers.ValidationError("数据有无")
            else:
                transaction.savepoint_commit(save_ponit)
                # 　６　删除ｒｅｄｉｓ缓存
                # 删除hash
                conn.hdel('cart_%s' % user.id, *sku_ids)
                # 删除集合
                conn.srem('cart_selseted_%s' % user.id, sku_ids)
                return order
