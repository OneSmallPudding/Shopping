from rest_framework import serializers

from goods.models import *


class SKUSerializer(serializers.ModelSerializer):
    '''SKU序列'''

    class Meta:
        model = SKU
        fields = "__all__"
