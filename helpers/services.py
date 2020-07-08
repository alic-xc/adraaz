from ecommerce.models import *
# writing functions that can be used alone


def get_categories(request, limit=0):
    cats = Category.objects.all()
    if limit == 0:
        return cats
    else:
        return cats[:limit]


def get_product(request, limit=0):
    products = Product.objects.all()
    if limit == 0:
        return products
    else:
        return products[:limit]


def get_brands(request, limit=0):
    brands = Brand.objects.all()
    if limit == 0:
        return brands
    else:
        return brands[:limit]
