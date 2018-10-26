from celery_tasks.main import app
from meiduo.libs.yuntongxun.sms import CCP


@app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code, ex):
    CCP().send_template_sms(mobile, [sms_code, ex], 1)
