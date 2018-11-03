from rest_framework import serializers

from goods.models import *


class SKUSerializer(serializers.ModelSerializer):
    '''SKU序列'''

    class Meta:
        model = SKU
        fields = "__all__"


from drf_haystack.serializers import HaystackSerializer


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        from goods.search_indexes import SKUIndex
        index_classes = [SKUIndex]
        fields = ("id", 'text', 'object')


class UserGoodsHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        try:
            SKU.objects.get(pk=attrs["sku_id"])
        except:
            raise serializers.ValidationError("sku_id不正确")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        from django_redis import get_redis_connection
        conn = get_redis_connection("history")
        conn.lrem("history_%s" % user.id, 0, validated_data["sku_id"])
        conn.lpush("history_%s" % user.id, validated_data["sku_id"])
        conn.ltrim("history_%s" % user.id, 0, 4)
        return validated_data
