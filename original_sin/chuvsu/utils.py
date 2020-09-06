def home_code():
    from .models import ProxyStep
    proxy = ProxyStep.objects.get(type=ProxyStep.HOME)
    return proxy.to.code