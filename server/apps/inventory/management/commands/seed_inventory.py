"""
Management command to seed inventory module with demo data.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.core.models import Organization
from apps.inventory.models import (
    Category, Brand, Unit, Warehouse, Product, ProductStock
)
from apps.inventory.services import add_opening_balance


class Command(BaseCommand):
    help = 'Seed inventory module with demo data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Organization name to seed data for (default: Demo Organization)',
            default='Demo Organization'
        )
    
    def handle(self, *args, **options):
        org_name = options['organization']
        
        try:
            organization = Organization.objects.get(name=org_name)
        except Organization.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Organization "{org_name}" not found. Creating it...')
            )
            organization = Organization.objects.create(
                name=org_name,
                description='Demo organization for testing',
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org_name}'))
        
        self.stdout.write(f'Seeding inventory data for organization: {organization.name}')
        
        with transaction.atomic():
            # Create Categories
            self.stdout.write('Creating categories...')
            electronics = Category.objects.create(
                organization=organization,
                code='ELEC',
                name='Electronics',
                description='Electronic items and devices',
                is_active=True
            )
            
            computers = Category.objects.create(
                organization=organization,
                code='COMP',
                name='Computers',
                description='Computer systems and accessories',
                parent=electronics,
                is_active=True
            )
            
            furniture = Category.objects.create(
                organization=organization,
                code='FURN',
                name='Furniture',
                description='Office and home furniture',
                is_active=True
            )
            
            stationery = Category.objects.create(
                organization=organization,
                code='STAT',
                name='Stationery',
                description='Office stationery and supplies',
                is_active=True
            )
            
            consumables = Category.objects.create(
                organization=organization,
                code='CONS',
                name='Consumables',
                description='Consumable items',
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Created 5 categories'))
            
            # Create Brands
            self.stdout.write('Creating brands...')
            dell = Brand.objects.create(
                organization=organization,
                code='DELL',
                name='Dell',
                country='United States',
                website='https://www.dell.com',
                is_active=True
            )
            
            hp = Brand.objects.create(
                organization=organization,
                code='HP',
                name='HP',
                country='United States',
                website='https://www.hp.com',
                is_active=True
            )
            
            samsung = Brand.objects.create(
                organization=organization,
                code='SAMS',
                name='Samsung',
                country='South Korea',
                website='https://www.samsung.com',
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Created 3 brands'))
            
            # Create Units
            self.stdout.write('Creating units of measurement...')
            pieces = Unit.objects.create(
                organization=organization,
                code='PCS',
                name='Pieces',
                symbol='pcs',
                is_active=True
            )
            
            boxes = Unit.objects.create(
                organization=organization,
                code='BOX',
                name='Box',
                symbol='box',
                is_active=True
            )
            
            kg = Unit.objects.create(
                organization=organization,
                code='KG',
                name='Kilogram',
                symbol='kg',
                is_active=True
            )
            
            liters = Unit.objects.create(
                organization=organization,
                code='LTR',
                name='Liter',
                symbol='L',
                is_active=True
            )
            
            sets = Unit.objects.create(
                organization=organization,
                code='SET',
                name='Set',
                symbol='set',
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Created 5 units'))
            
            # Create Warehouses
            self.stdout.write('Creating warehouses...')
            main_warehouse = Warehouse.objects.create(
                organization=organization,
                code='WH-MAIN',
                name='Main Warehouse',
                address='123 Industrial Area',
                city='Karachi',
                state='Sindh',
                country='Pakistan',
                postal_code='75500',
                phone='+92-21-1234567',
                email='warehouse.main@example.com',
                is_active=True
            )
            
            branch_warehouse = Warehouse.objects.create(
                organization=organization,
                code='WH-BRANCH',
                name='Branch Warehouse',
                address='456 Commercial Avenue',
                city='Lahore',
                state='Punjab',
                country='Pakistan',
                postal_code='54000',
                phone='+92-42-7654321',
                email='warehouse.branch@example.com',
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Created 2 warehouses'))
            
            # Create Products
            self.stdout.write('Creating products...')
            products_data = [
                {
                    'code': 'PROD-001',
                    'name': 'Dell Latitude 5420 Laptop',
                    'barcode': '123456789001',
                    'description': '14" FHD, Intel i5, 8GB RAM, 256GB SSD',
                    'product_type': 'GOODS',
                    'category': computers,
                    'brand': dell,
                    'unit': pieces,
                    'cost_price': Decimal('75000.00'),
                    'selling_price': Decimal('95000.00'),
                    'reorder_level': Decimal('5.00'),
                    'reorder_quantity': Decimal('10.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-002',
                    'name': 'HP LaserJet Pro Printer',
                    'barcode': '123456789002',
                    'description': 'Monochrome laser printer with duplex printing',
                    'product_type': 'GOODS',
                    'category': electronics,
                    'brand': hp,
                    'unit': pieces,
                    'cost_price': Decimal('25000.00'),
                    'selling_price': Decimal('32000.00'),
                    'reorder_level': Decimal('3.00'),
                    'reorder_quantity': Decimal('5.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-003',
                    'name': 'Samsung 24" LED Monitor',
                    'barcode': '123456789003',
                    'description': 'Full HD LED monitor with HDMI',
                    'product_type': 'GOODS',
                    'category': computers,
                    'brand': samsung,
                    'unit': pieces,
                    'cost_price': Decimal('15000.00'),
                    'selling_price': Decimal('19500.00'),
                    'reorder_level': Decimal('10.00'),
                    'reorder_quantity': Decimal('15.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-004',
                    'name': 'Office Desk',
                    'barcode': '123456789004',
                    'description': 'Wooden office desk with drawers',
                    'product_type': 'GOODS',
                    'category': furniture,
                    'brand': None,
                    'unit': pieces,
                    'cost_price': Decimal('12000.00'),
                    'selling_price': Decimal('16000.00'),
                    'reorder_level': Decimal('2.00'),
                    'reorder_quantity': Decimal('5.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-005',
                    'name': 'Office Chair',
                    'barcode': '123456789005',
                    'description': 'Ergonomic office chair with lumbar support',
                    'product_type': 'GOODS',
                    'category': furniture,
                    'brand': None,
                    'unit': pieces,
                    'cost_price': Decimal('8000.00'),
                    'selling_price': Decimal('11000.00'),
                    'reorder_level': Decimal('5.00'),
                    'reorder_quantity': Decimal('10.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-006',
                    'name': 'A4 Paper Ream',
                    'barcode': '123456789006',
                    'description': '500 sheets of A4 white paper',
                    'product_type': 'CONSUMABLE',
                    'category': stationery,
                    'brand': None,
                    'unit': boxes,
                    'cost_price': Decimal('450.00'),
                    'selling_price': Decimal('600.00'),
                    'reorder_level': Decimal('20.00'),
                    'reorder_quantity': Decimal('50.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-007',
                    'name': 'Ballpoint Pen Box',
                    'barcode': '123456789007',
                    'description': 'Box of 50 blue ballpoint pens',
                    'product_type': 'CONSUMABLE',
                    'category': stationery,
                    'brand': None,
                    'unit': boxes,
                    'cost_price': Decimal('250.00'),
                    'selling_price': Decimal('350.00'),
                    'reorder_level': Decimal('10.00'),
                    'reorder_quantity': Decimal('20.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-008',
                    'name': 'Whiteboard Markers Set',
                    'barcode': '123456789008',
                    'description': 'Set of 4 colored whiteboard markers',
                    'product_type': 'CONSUMABLE',
                    'category': stationery,
                    'brand': None,
                    'unit': sets,
                    'cost_price': Decimal('180.00'),
                    'selling_price': Decimal('250.00'),
                    'reorder_level': Decimal('15.00'),
                    'reorder_quantity': Decimal('30.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
                {
                    'code': 'PROD-009',
                    'name': 'IT Support Service',
                    'description': 'Hourly IT support and maintenance service',
                    'product_type': 'SERVICE',
                    'category': electronics,
                    'brand': None,
                    'unit': pieces,
                    'cost_price': Decimal('0.00'),
                    'selling_price': Decimal('1500.00'),
                    'reorder_level': Decimal('0.00'),
                    'reorder_quantity': Decimal('0.00'),
                    'can_be_sold': True,
                    'can_be_purchased': False,
                    'is_active': True,
                },
                {
                    'code': 'PROD-010',
                    'name': 'Coffee Sachets',
                    'barcode': '123456789010',
                    'description': 'Instant coffee sachets box of 100',
                    'product_type': 'CONSUMABLE',
                    'category': consumables,
                    'brand': None,
                    'unit': boxes,
                    'cost_price': Decimal('800.00'),
                    'selling_price': Decimal('1100.00'),
                    'reorder_level': Decimal('5.00'),
                    'reorder_quantity': Decimal('10.00'),
                    'can_be_sold': True,
                    'can_be_purchased': True,
                    'is_active': True,
                },
            ]
            
            products = []
            for data in products_data:
                product = Product.objects.create(organization=organization, **data)
                products.append(product)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(products)} products'))
            
            # Create Opening Stock Balance (only for goods and consumables, not services)
            self.stdout.write('Creating opening stock balances...')
            stock_data = [
                (products[0], main_warehouse, Decimal('15.00')),  # Laptops
                (products[1], main_warehouse, Decimal('8.00')),   # Printers
                (products[2], main_warehouse, Decimal('25.00')),  # Monitors
                (products[2], branch_warehouse, Decimal('10.00')), # Monitors in branch
                (products[3], main_warehouse, Decimal('12.00')),  # Office Desks
                (products[4], main_warehouse, Decimal('20.00')),  # Office Chairs
                (products[5], main_warehouse, Decimal('100.00')), # A4 Paper
                (products[5], branch_warehouse, Decimal('50.00')), # A4 Paper in branch
                (products[6], main_warehouse, Decimal('30.00')),  # Pens
                (products[7], main_warehouse, Decimal('40.00')),  # Whiteboard Markers
                (products[9], main_warehouse, Decimal('20.00')),  # Coffee
            ]
            
            # Note: Product at index 8 is a SERVICE, so no stock
            
            for product, warehouse, qty in stock_data:
                add_opening_balance(
                    product=product,
                    warehouse=warehouse,
                    quantity=qty,
                    user=None,  # System generated
                    organization=organization,
                    reference_number='OPEN-2026'
                )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(stock_data)} stock records'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Inventory Module Seeded Successfully ==='))
        self.stdout.write(f'Organization: {organization.name}')
        self.stdout.write(f'Categories: 5')
        self.stdout.write(f'Brands: 3')
        self.stdout.write(f'Units: 5')
        self.stdout.write(f'Warehouses: 2')
        self.stdout.write(f'Products: 10')
        self.stdout.write(f'Stock Records: {len(stock_data)}')
