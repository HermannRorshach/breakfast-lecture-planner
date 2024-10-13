from django import template


register = template.Library()


@register.filter
def get_item_by_index(sequence, index):
    try:
        return sequence[int(index)]
    except (IndexError, ValueError):
        return None


import re
import requests
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Регулярное выражение для поиска URL
url_regex = re.compile(r'(https?://[^\s]+)')

# Список oEmbed провайдеров (например, YouTube, Twitter и т.д.)
OEMBED_PROVIDERS = {
    'youtube': 'https://www.youtube.com/oembed',
    'vimeo': 'https://vimeo.com/api/oembed.json',
    'twitter': 'https://publish.twitter.com/oembed',
}

def fetch_oembed_content(url, provider_url):
    try:
        response = requests.get(provider_url, params={'url': url, 'format': 'json'})
        if response.status_code == 200:
            return response.json().get('html', '')  # Получаем HTML для встраивания
    except requests.exceptions.RequestException:
        return None
    return None

@register.filter
def render_oembed(value):
    """
    Ищет URL в тексте и заменяет их на встроенные медиа, если URL поддерживается через oEmbed.
    """
    def replace_url(match):
        url = match.group(0)

        # Проверяем, какой провайдер может обработать ссылку
        for provider, provider_url in OEMBED_PROVIDERS.items():
            if provider in url:
                oembed_html = fetch_oembed_content(url, provider_url)
                if oembed_html:
                    return oembed_html

        # Если провайдер не найден, возвращаем оригинальный URL
        return url

    # Ищем все URL в тексте и заменяем их через replace_url
    rendered_content = re.sub(url_regex, replace_url, value)

    # Возвращаем результат как безопасный HTML
    return mark_safe(rendered_content)
