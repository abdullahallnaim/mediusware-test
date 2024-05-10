from django.views import generic

from product.models import Variant, ProductVariant, ProductVariantPrice
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.views.generic.list import ListView
from product.models import Product

class ProductList(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # getting the query parameters

        title = self.request.GET.get('title')
        variant = self.request.GET.get('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')

        # Filter products based on search parameters
        queryset = self.get_queryset()
        if title:
            queryset = queryset.filter(title__icontains=title)
        if variant:
            product_ids = ProductVariant.objects.filter(variant_title=variant).values_list('product_id', flat=True)
            queryset = queryset.filter(id__in=product_ids)
        if price_from and price_to:
            queryset = queryset.filter(productvariantprice__price__range=(price_from, price_to))
        if date:
            queryset = queryset.filter(created_at__date=date)



        # Pagination
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            paged_products = paginator.page(page)
        except PageNotAnInteger:
            paged_products = paginator.page(1)
        except EmptyPage:
            paged_products = paginator.page(paginator.num_pages)
        for product in paged_products:
            product.variants = ProductVariant.objects.filter(product=product)
            variants_price = ProductVariantPrice.objects.filter(product=product)
            product.variant_info_list = []
            for variant in product.variants:
                variant_info = {
                    "variant_type": variant.variant.title,
                    "variant_title": variant.variant_title,
                    "description": variant.variant.description,
                    "active": variant.variant.active,
                    "prices": [],
                    "in_stock": []
                }
                
                variant_prices = ProductVariantPrice.objects.filter(product=product, product_variant_one=variant)
                for price_info in variant_prices:
                    variant_info["prices"].append(price_info.price)
                    variant_info["in_stock"].append(price_info.stock)
                product.variant_info_list.append(variant_info)
            product.variant_info_list.append({"variant_prices" : variants_price})

        grouped_variants = {}
        unique_variants = ProductVariant.objects.values_list('variant_title', flat=True).distinct()
        
        # Group variant titles by their type

        for variant in unique_variants:
            variant_obj = ProductVariant.objects.filter(variant_title=variant).first()
            variant_type = variant_obj.variant.title
            grouped_variants.setdefault(variant_type, []).append(variant)
        context['grouped_variants'] = grouped_variants
        context['paginator'] = paginator
        context['paged_products'] = paged_products
        context['variants'] = ProductVariant.objects.all()
        return context
    

    def get_queryset(self):
        return super().get_queryset().distinct()
    
    
class CreateProductView(generic.TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        print(variants)
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


