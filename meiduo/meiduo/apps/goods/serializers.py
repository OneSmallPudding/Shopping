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
        fields = ("id",'text', 'object')
