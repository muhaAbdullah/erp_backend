"""
Filters for Product model.
"""
import django_filters
from apps.inventory.models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Filter class for Product model.
    
    Supports filtering by:
    - Name (contains search)
    - Code (contains search)
    - Barcode (exact match)
    - Category
    - Brand
    - Product type
    - Active status
    - Can be sold/purchased flags
    - Price range
    """
    
    # Text search filters
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    barcode = django_filters.CharFilter(lookup_expr='exact')
    
    # Relationship filters
    category = django_filters.NumberFilter(field_name='category__id')
    brand = django_filters.NumberFilter(field_name='brand__id')
    unit = django_filters.NumberFilter(field_name='unit__id')
    
    # Choice filters
    product_type = django_filters.ChoiceFilter(choices=Product.PRODUCT_TYPE_CHOICES)
    
    # Boolean filters
    is_active = django_filters.BooleanFilter()
    can_be_sold = django_filters.BooleanFilter()
    can_be_purchased = django_filters.BooleanFilter()
    
    # Price range filters
    cost_price_min = django_filters.NumberFilter(field_name='cost_price', lookup_expr='gte')
    cost_price_max = django_filters.NumberFilter(field_name='cost_price', lookup_expr='lte')
    selling_price_min = django_filters.NumberFilter(field_name='selling_price', lookup_expr='gte')
    selling_price_max = django_filters.NumberFilter(field_name='selling_price', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('code', 'code'),
            ('cost_price', 'cost_price'),
            ('selling_price', 'selling_price'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'barcode',
            'category', 'brand', 'unit',
            'product_type', 'is_active',
            'can_be_sold', 'can_be_purchased'
        ]
