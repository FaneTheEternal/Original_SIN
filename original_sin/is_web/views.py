from django.views.generic import TemplateView

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
