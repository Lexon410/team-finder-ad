from django.core.paginator import Paginator
from constants import PAGE_SIZE

def paginate_queryset(request, queryset, per_page=PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)