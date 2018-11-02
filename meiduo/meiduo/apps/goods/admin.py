from django.contrib import admin
from . import models
from celery_tasks.static_html.tasks import generate_static_list_search_html, generate_static_sku_detail_html
# Register your models here.
from goods.models import SKU, Goods


class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        obj.delete()

        generate_static_list_search_html.delay()


class GoodsAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay()


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)


admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.GoodsCategory)
admin.site.register(models.Goods, GoodsAdmin)
