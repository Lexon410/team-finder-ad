from django import forms
from urllib.parse import urlparse

def validate_github_url(url):
    if not url:
        return url
    parsed = urlparse(url)
    if parsed.netloc not in ('github.com', 'www.github.com'):
        raise forms.ValidationError('Ссылка должна вести на GitHub')
    return url