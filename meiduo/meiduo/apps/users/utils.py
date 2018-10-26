def jwt_response_payload_handler(token, user=None, request=None):
    '''自定义ｊｗｔ返回结果'''
    return {
        "token": token, "user_id": user.id, "username": user.username
    }
