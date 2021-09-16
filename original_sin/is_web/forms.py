from django import forms

from is_web.models import CardAbstract, News, CatalogItem


class CardFormMixin(forms.Form):
    class Meta:
        fields = ['header', 'title', 'links', 'text', 'img']

    def __init__(self, *args, **kwargs):
        super(CardFormMixin, self).__init__(*args, **kwargs)
        if self.initial.get('links', None):
            self.initial['links'] = self.initial['links']\
                .replace(CardAbstract.LINKS_SEPARATOR, '\n')\
                .replace(CardAbstract.LINK_CONTENT_SEPARATOR, '  ')

    def check_links(self, links):
        links = links.split(CardAbstract.LINKS_SEPARATOR)
        links = map(lambda x: x.split(CardAbstract.LINK_CONTENT_SEPARATOR), links)
        for link in links:
            try:
                name, link = link
            except ValueError:
                self.add_error(
                    'links',
                    'Ccылки должные быть разбиты по строкам и '
                    'название с ссылкой разделены 2 проблами'
                    '(example__https://example.com)')
                return

    def clean_links(self):
        links: str = self.cleaned_data.get('links', None)
        if links:
            links = links.replace('\n', CardAbstract.LINKS_SEPARATOR) \
                .replace('  ', CardAbstract.LINK_CONTENT_SEPARATOR)
            self.check_links(links)
        return links


class NewsForm(CardFormMixin, forms.ModelForm):
    class Meta(CardFormMixin.Meta):
        model = News


class CatalogItemForm(CardFormMixin, forms.ModelForm):
    class Meta(CardFormMixin.Meta):
        model = CatalogItem
