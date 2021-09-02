from django.views.generic import TemplateView


class BaseView(TemplateView):
    tab = None

    def get_context_data(self, **kwargs):
        kwargs = super(BaseView, self).get_context_data(**kwargs)
        kwargs['tab'] = self.tab
        return kwargs


class NewsView(BaseView):
    tab = 'news'

    template_name = 'is_web/news.html'


class CatalogView(BaseView):
    tab = 'catalog'

    template_name = 'is_web/catalog.html'


class ContactsView(BaseView):
    tab = 'contacts'

    template_name = 'is_web/contacts.html'


class InfoView(BaseView):
    tab = 'info'

    template_name = 'is_web/info.html'
