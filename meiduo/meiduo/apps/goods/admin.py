from django.contrib import admin

# Register your models here.
from goods.models import SKU, Goods


class SKUAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        print(obj)


admin.site.register(SKU, SKUAdmin)
admin.site.register(Goods, SKUAdmin)
