from ecommerce.models import *
# writing functions that can be used alone


class ContentMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['carts'] = self.request.session.get('cart', {})
        context['contact'] = Contact.objects.all()
        # calculations for cart
        if context['carts']:
            amount = 0
            qty = 0
            for cart_id, cart_items in context['carts'].items():
                amount += float(cart_items['amount'])
                qty += int(cart_items['qty'])

            context['cart_extra'] = {
                'total_amount': amount,
                'total_qty': qty,
                'total_items': len(context['carts'])
            }
        return context


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


