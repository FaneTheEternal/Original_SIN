from django.conf import settings

token = getattr(settings, 'CHUVSU_VK_TOKEN')
# confirmation token issued on the VK group web-administration page in "Callback API" section
confirmation_token = getattr(settings, 'CHUVSU_VK_CONFIRMATION_TOKEN')
# secret key for cross site request forgery protection. It will be in each VK server request
secret_key = getattr(settings, 'CHUVSU_VK_SECRET_KEY')
