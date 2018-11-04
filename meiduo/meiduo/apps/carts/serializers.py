from rest_framework import serializers

from goods.models import SKU


class CartSerialzers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        try:
            SKU.objects.get(pk=attrs["sku_id"])
        except:
            raise serializers.ValidationError("sku_id不正确")
        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(min_value=1, label="“数量")
    selected = serializers.BooleanField(default=True, label="是否勾选")

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')
