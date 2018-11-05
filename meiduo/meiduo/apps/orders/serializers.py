from rest_framework import serializers

from goods.models import SKU


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
