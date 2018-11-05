import base64
import pickle

from rest_framework.response import Response


def merge_cart_cookie_to_redis(reqeust, response, user):
    '''合并用户购物车'''
    cart_cookie = reqeust.COOKIES.get("cart_cookie", None)
    if not cart_cookie:
        return response
    try:
        cart = pickle.loads(base64.b64decode(cart_cookie))
    except:
        return Response({"errors": "cart_cookie不正确"})
    if not cart:
        return response
    cart_dict = {}
    cart_list = []
    cart_delete_list = []
    for sku_id, value in cart.items():
        cart_dict[int(sku_id)] = value['count']
        if value["selected"]:
            cart_list.append(int(sku_id))
        else:
            cart_delete_list.append(sku_id)
    from django_redis import get_redis_connection
    conn = get_redis_connection("carts")
    if cart_dict:
        conn.hmset('cart_%s' % user.id, cart_dict)
    if cart_list:
        conn.sadd('cart_selected_%s' % user.id, *cart_list)
    if cart_delete_list:
        conn.srem('cart_selected_%s' % user.id, *cart_delete_list)
    response.delete_cookie("cart_cookie")
    return response
