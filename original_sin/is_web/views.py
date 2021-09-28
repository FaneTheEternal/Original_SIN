from datetime import timedelta
from uuid import UUID

from django.utils import timezone
from django.views.generic import TemplateView
from ninja import Schema, NinjaAPI

from core.decor import SafeWrapper
from is_web.models import News, CatalogItem


class BaseView(TemplateView):
    tab = None

    def get_context_data(self, **kwargs):
        kwargs = super(BaseView, self).get_context_data(**kwargs)
        kwargs['tab'] = self.tab
        return kwargs


class NewsView(BaseView):
    tab = 'news'

    template_name = 'is_web/news.html'

    def get_context_data(self, **kwargs):
        kwargs = super(NewsView, self).get_context_data(**kwargs)
        kwargs['news'] = News.objects.all().order_by('-created')
        return kwargs


class CatalogView(BaseView):
    tab = 'catalog'

    template_name = 'is_web/catalog.html'

    def get_context_data(self, **kwargs):
        kwargs = super(CatalogView, self).get_context_data(**kwargs)
        kwargs['items'] = CatalogItem.objects.all().order_by('-created')
        return kwargs


class ContactsView(BaseView):
    tab = 'contacts'

    template_name = 'is_web/contacts.html'


class InfoView(BaseView):
    tab = 'info'

    template_name = 'is_web/info.html'


# API card verbose time
class CardSchema(Schema):
    uid: str


api = NinjaAPI(urls_namespace='is_web')


@api.post('/get_time')
@SafeWrapper(CardSchema)
def get_time(obj: CardSchema):
    uid = UUID(hex=obj.uid)
    if News.objects.filter(uid=uid).exists():
        news = News.objects.get(uid=uid)
        created = news.created
    elif CatalogItem.objects.filter(uid=uid).exists():
        item = CatalogItem.objects.get(uid=uid)
        created = item.created
    else:
        return dict()
    now = timezone.now()
    if now < (created + timedelta(minutes=1)):
        created = 'Меньше минуты назад'
    elif now < (created + timedelta(minutes=5)):
        created = 'Минуту назад'
    elif now < (created + timedelta(minutes=10)):
        created = '10 минут назад'
    elif now < (created + timedelta(hours=1)):
        created -= now
        created = f'{created.seconds // 60 % 60} минут назад'
    elif now < (created + timedelta(hours=2)):
        created = 'Час назад'
    elif now < (created + timedelta(days=1)):
        created -= now
        created = f'{created.seconds // 3600} часов назад'
    else:
        created = created.strftime('%H:%M %d.%m.%Y')
    return dict(created=str(created))
