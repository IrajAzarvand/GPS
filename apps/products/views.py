from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q
from .models import Product, Category


class HomeView(TemplateView):
    """
    Home page view
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured products
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]

        # Get all active categories
        context['categories'] = Category.objects.filter(is_active=True)

        return context


class ProductListView(ListView):
    """
    Product listing view with filtering
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Search filter
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )

        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter options
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q')
        context['min_price'] = self.request.GET.get('min_price')
        context['max_price'] = self.request.GET.get('max_price')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')

        return context


class ProductDetailView(DetailView):
    """
    Product detail view
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]

        # Product images
        context['product_images'] = product.images.all()

        return context


class CategoryListView(ListView):
    """
    Category listing view
    """
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(DetailView):
    """
    Category detail view
    """
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Products in this category
        context['products'] = Product.objects.filter(
            category=category,
            is_active=True
        )

        # Subcategories if any
        context['subcategories'] = category.subcategories.filter(is_active=True)

        return context
