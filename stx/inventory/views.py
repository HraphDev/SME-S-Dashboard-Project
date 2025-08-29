from io import TextIOWrapper
from django.utils import timezone
from datetime import datetime, timedelta
from unicodedata import category
from urllib import request
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from pydantic import ValidationError
from .models import Category, Product
from django.contrib import messages 
from decimal import Decimal, InvalidOperation 
from django.core.paginator import Paginator
from .models import Product, ProductMovement
from django.db.models import Count
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse , HttpResponse
import json
from django.utils.timezone import now as timezone_now
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models.functions import TruncDate
import json
import os
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
from .models import Product, Supplier
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Supplier, Product
from django.db import transaction
from django.db.models import Case, When, F, Sum
from django.db.models.functions import TruncDate
from django.db.models import Q
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.timezone import localtime

def category_list(request):
    categories = Category.objects.all().order_by('name')
    
    
    search_query = request.GET.get('q', '')
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(categories, 25) 
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'category': category
    }
    return render(request, 'dashboard/categories/list.html', context)


def category_detail(request,pk):
    category = get_object_or_404(Category,id=pk)
    products = Product.objects.filter(category=category)
    return render (request,'dashboard/categories/category_detail.html',{'category':category,'products':products})

def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
    
        if not name or not description:
            messages.error(request, "Category name and description are required.")
            return redirect('category_create')

        Category.objects.create(name=name, description=description)
        messages.success(request, "Category created.")
        return redirect('category_list')

    return render(request, 'dashboard/categories/form.html')


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk) # 2EME PK C'EST NBR DANS L URL DANS LE SEQUENCEMENT DE CATEGORIE EN TABLEAU SI 4 ... ET 4 EXIST IL VA TE DONNER LE CONTENU DE 4 
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            category.name = name
            category.description = description
            category.created_at = timezone.now() 
            category.save()
            messages.success(request, "Category updated.")
            return redirect('category_list')
        else:
            messages.error(request, "Name cannot be empty.")
    return render(request, 'dashboard/categories/form.html', {'category': category})




def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect('category_list')
    return render(request, 'dashboard/categories/confirm_delete.html', {
         'object': category,
         'cancel_url': reverse('category_list')
    })























def product_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    supplier_filter = request.GET.get('supplier', '') 

    products = Product.objects.select_related('category', 'supplier').order_by('name')  

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category__id=category_filter)
        
    if supplier_filter:  
        products = products.filter(supplier__id=supplier_filter)

    paginator = Paginator(products, 10) 
    page = request.GET.get('page')
    products = paginator.get_page(page)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()  

    return render(request, 'dashboard/products/list.html', {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,  
        'search_query': search_query,
        'category_filter': category_filter,
        'supplier_filter': supplier_filter,  
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('supplier'), id=pk) 
    return render(request, 'dashboard/products/detail.html', {
        'product': product
    })


def product_create(request):
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        supplier_id = request.POST.get('supplier')
        initial_quantity = request.POST.get('quantity') 

        if not all([name, category_id, price]):
            messages.error(request, "Nom, catégorie et prix sont obligatoires.")
            return render(request, 'dashboard/products/form.html', {
                'categories': categories,
                'suppliers': suppliers,
                'preserved_data': request.POST
            })

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Catégorie invalide.")
            return render(request, 'dashboard/products/form.html', {
                'categories': categories,
                'suppliers': suppliers,
                'preserved_data': request.POST
            })

        supplier = None
        if supplier_id:
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
            except Supplier.DoesNotExist:
                messages.warning(request, "Fournisseur invalide. Produit enregistré sans fournisseur.")

        try:
            price_decimal = Decimal(price)
        except (ValueError, InvalidOperation):
            messages.error(request, "Format du prix invalide.")
            return render(request, 'dashboard/products/form.html', {
                'categories': categories,
                'suppliers': suppliers,
                'preserved_data': request.POST
            })

        product = Product.objects.create(
            name=name,
            category=category,
            price=price_decimal,
            description=description,
            image=image,
            supplier=supplier
        )
        if initial_quantity:
            try:
                qty = int(initial_quantity)
                if qty > 0:
                    ProductMovement.objects.create(
                        product=product,
                        movement_type='in',
                        quantity=qty,
                        description="Stock initial"
                    )
            except ValueError:
                messages.warning(request, "Quantité initiale invalide. Produit créé sans stock.")

        messages.success(request, "Produit créé avec succès.")
        return redirect('product_list')

    return render(request, 'dashboard/products/form.html', {
        'categories': categories,
        'suppliers': suppliers
    })


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        supplier_id = request.POST.get('supplier')

        if not all([name, category_id, price]):
            messages.error(request, "Nom, catégorie et prix sont obligatoires.")
            return render(request, 'dashboard/products/form.html', {
                'product': product,
                'categories': categories,
                'suppliers': suppliers
            })

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Catégorie invalide.")
            return render(request, 'dashboard/products/form.html', {
                'product': product,
                'categories': categories,
                'suppliers': suppliers
            })

        supplier = None
        if supplier_id:
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
            except Supplier.DoesNotExist:
                messages.warning(request, "Fournisseur invalide. Supprimé.")

        try:
            price_decimal = Decimal(price)
        except (ValueError, InvalidOperation):
            messages.error(request, "Format du prix invalide.")
            return render(request, 'dashboard/products/form.html', {
                'product': product,
                'categories': categories,
                'suppliers': suppliers
            })

        product.name = name
        product.category = category
        product.price = price_decimal
        product.description = description
        product.supplier = supplier
        if image:
            product.image = image
        product.save()

        messages.success(request, "Produit modifié avec succès.")
        return redirect('product_list')

    return render(request, 'dashboard/products/form.html', {
        'product': product,
        'categories': categories,
        'suppliers': suppliers
    })


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('product_list')
    return render(request, 'dashboard/products/confirm_delete.html', {
         'object': product,
         'cancel_url': reverse('product_list')
    })


def product_movement_history(request, product_id):
    product = get_object_or_404(Product.objects.select_related('supplier'), pk=product_id)
    
    movements = ProductMovement.objects.filter(product=product).order_by('-date')
    
    paginator = Paginator(movements, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/products/product_history.html', {
        'product': product,
        'movements': page_obj,
    })










def movement_list(request):
    products = Product.objects.all()

    product_id = request.GET.get('product')
    movement_type = request.GET.get('movement_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    movements = ProductMovement.objects.select_related('product').all()

    if product_id:
        movements = movements.filter(product_id=product_id)
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    if start_date:
        parsed_date = parse_date(start_date)
        if parsed_date:
            start_datetime = timezone.datetime.combine(parsed_date, timezone.datetime.min.time())
            movements = movements.filter(date__gte=timezone.make_aware(start_datetime))
    
    if end_date:
        parsed_date = parse_date(end_date)
        if parsed_date:
            end_datetime = timezone.datetime.combine(parsed_date, timezone.datetime.max.time())
            movements = movements.filter(date__lte=timezone.make_aware(end_datetime))
    movements = movements.order_by('-date')
    paginator = Paginator(movements, 10)
    page = request.GET.get('page')
    movements = paginator.get_page(page)

    chart_queryset = (
    ProductMovement.objects
    .annotate(date_only=TruncDate('date'))  
    .values('date_only')
    .annotate(total=Count('id'))
    .order_by('date_only')
)

    chart_data = [
    {
        'date': item['date_only'].strftime('%Y-%m-%d') if item['date_only'] else '',
        'total': item['total']
    }
    for item in chart_queryset
]

    return render(request, 'dashboard/movements/list.html', {
        'movements': movements,
        'products': products,
        'selected_product': product_id,
        'selected_type': movement_type,
        'start_date': start_date,
        'end_date': end_date,
        'chart_data_json': json.dumps(chart_data), 
    })

def movement_create(request):
    products = Product.objects.all()
    error = None

    if request.method == 'POST':
        product_id = request.POST.get('product')
        movement_type = request.POST.get('movement_type')
        quantity_str = request.POST.get('quantity')
        description = request.POST.get('description')

        if not product_id or not movement_type or not quantity_str:
            error = "Veuillez remplir tous les champs obligatoires."
        else:
            try:
                quantity = int(quantity_str)
                product = get_object_or_404(Product, pk=product_id)

              
                if movement_type == 'out' and product.quantity < quantity:
                    error = "Stock insuffisant pour cette sortie."
                else:
                    ProductMovement.objects.create(
                        product=product,
                        movement_type=movement_type,
                        quantity=quantity,
                        description=description,
                        date=timezone_now()
                    )
                    return redirect('movement_list')
            except ValueError:
                error = "La quantité doit être un nombre entier."

    return render(request, 'dashboard/movements/form.html', {
        'products': products,
        'error': error,
    })

 

def movement_update(request, pk):
    movement = get_object_or_404(
        ProductMovement.objects.select_related('product'),
        pk=pk
    )
    products = Product.objects.all().order_by('name')

    if request.method == 'GET':
        return render(request, 'dashboard/movements/form.html', {
            'products': products,
            'movement': movement,
            'error': None,
        })

    product_id = request.POST.get('product')
    movement_type = request.POST.get('movement_type')
    quantity_str = request.POST.get('quantity')
    description = request.POST.get('description', '')

    if not product_id or not movement_type or not quantity_str:
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return render(request, 'dashboard/movements/form.html', {
            'products': products,
            'movement': movement,
            'error': "Veuillez remplir tous les champs obligatoires.",
        })

    allowed_types = dict(ProductMovement.MOVEMENT_TYPES).keys()
    if movement_type not in allowed_types:
        messages.error(request, "Type de mouvement invalide.")
        return render(request, 'dashboard/movements/form.html', {
            'products': products,
            'movement': movement,
            'error': "Type de mouvement invalide.",
        })

    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "La quantité doit être un entier positif.")
        return render(request, 'dashboard/movements/form.html', {
            'products': products,
            'movement': movement,
            'error': "La quantité doit être un entier positif.",
        })

    product = get_object_or_404(Product, pk=product_id)

    movement.product = product
    movement.movement_type = movement_type
    movement.quantity = quantity
    movement.description = description
    movement.date = timezone_now()

    try:
        with transaction.atomic():
            if hasattr(movement, 'full_clean'):
                movement.full_clean()
            movement.save()
        messages.success(request, "Mouvement mis à jour avec succès.")
        return redirect('movement_list')
    except (ValidationError, ValueError) as e:
        err_msg = getattr(e, 'message', None) or getattr(e, 'messages', [str(e)])[0] if hasattr(e, 'messages') else str(e)
        messages.error(request, err_msg)
        return render(request, 'dashboard/movements/form.html', {
            'products': products,
            'movement': movement,
            'error': err_msg,
        })

def movement_delete(request, pk):
    movement = get_object_or_404(ProductMovement, pk=pk)

    if request.method == 'POST':
        movement.delete()
        return redirect('movement_list')

    return render(request, 'dashboard/movements/confirm_delete.html', {
        'movement': movement,
    })






def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Quantity', 'Price'])

    for product in Product.objects.all():
        try:
            category_name = product.category.name
        except Category.DoesNotExist:
            category_name = 'No Category'
        except AttributeError:  
            category_name = 'No Category'
            
        writer.writerow([product.name, category_name, product.quantity, product.price])

    return response

def export_products_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="products_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, "Rapport des Produits")
    y -= 40

    pdf.setFont("Helvetica", 12)
    for product in Product.objects.all():
        line = f"{product.name} | {product.category.name} | Stock: {product.quantity} | Prix: {product.price} DH"
        pdf.drawString(40, y, line)
        y -= 20
        if y < 50:
            pdf.showPage()
            y = height - 50

    pdf.save()
    return response
























def stock_alerts(request):
    threshold = 10  

    all_products = list(Product.objects.all())

    low_stock = [p for p in all_products if p.quantity < threshold]

    low_stock.sort(key=lambda p: p.quantity)

    context = {
        'products': low_stock,
        'threshold': threshold,
        'low_stock_count': len(low_stock),
    }

    return render(request, 'dashboard/stock_alerts.html', context)


def bulk_import(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  
            try:
                if not row.get('name') or not row.get('category_id'):
                    errors.append(f"Row {row_num}: Missing required fields (name or category_id)")
                    continue
                
                supplier = None
                supplier_id = row.get('supplier_id')
                if supplier_id:
                    try:
                        supplier = Supplier.objects.get(id=supplier_id)
                    except Supplier.DoesNotExist:
                        errors.append(f"Row {row_num}: Supplier with ID {supplier_id} does not exist")
                        continue
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid supplier ID format '{supplier_id}'")
                        continue
                
             
                Product.objects.create(
                    name=row['name'],
                    category_id=row['category_id'],
                    price=float(row.get('price', 0)),
                    description=row.get('description', ''),
                    supplier=supplier
                )
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error importing '{row.get('name', 'Unknown')}' - {str(e)}")
        
        if created_count > 0:
            messages.success(request, f"Successfully imported {created_count} products!")
        if errors:
            for error in errors:
                messages.error(request, error)
        
        return redirect('product_list')
    
    suppliers = Supplier.objects.all().order_by('name')
    
    return render(request, 'dashboard/bulk_import.html', {
        'suppliers': suppliers
    })



def supplier_list(request):
    suppliers = Supplier.objects.all()
    
    search_query = request.GET.get('q', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    sort = request.GET.get('sort', 'name')
    if sort == 'name':
        suppliers = suppliers.order_by('name')
    elif sort == '-name':
        suppliers = suppliers.order_by('-name')
    
    active_suppliers_count = suppliers.count()  
    total_products_supplied = Product.objects.filter(supplier__isnull=False).count()
    
    paginator = Paginator(suppliers, 25)  
    page_number = request.GET.get('page')
    suppliers_page = paginator.get_page(page_number)
    
    context = {
        'suppliers': suppliers_page,
        'search_query': search_query,
        'active_suppliers_count': active_suppliers_count,
        'total_products_supplied': total_products_supplied,
    }
    return render(request, 'dashboard/suppliers/list.html', context)

def supplier_create(request):
    if request.method == 'POST':
        required_fields = ['name', 'phone']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        
        if missing_fields:
            messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
        else:
            try:
                supplier = Supplier.objects.create(
                    name=request.POST.get('name'),
                    contact=request.POST.get('contact', ''),
                    email=request.POST.get('email', ''),
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address', '')
                )
                messages.success(request, f"Supplier '{supplier.name}' created successfully!")
                return redirect('supplier_detail', pk=supplier.pk)
            except Exception as e:
                messages.error(request, f"Error creating supplier: {str(e)}")
    
    return render(request, 'dashboard/suppliers/create.html')

def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier_products = Product.objects.filter(supplier=supplier)
    
    return render(request, 'dashboard/suppliers/detail.html', {
        'supplier': supplier,
        'products': supplier_products,
        'products_count': supplier_products.count()
    })

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        required_fields = ['name', 'phone']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        
        if missing_fields:
            messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
        else:
            try:
                supplier.name = request.POST.get('name')
                supplier.contact = request.POST.get('contact', '')
                supplier.email = request.POST.get('email', '')
                supplier.phone = request.POST.get('phone')
                supplier.address = request.POST.get('email', '')
                supplier.save()
                
                messages.success(request, f"Supplier '{supplier.name}' updated successfully!")
                return redirect('supplier_detail', pk=supplier.pk)
            except Exception as e:
                messages.error(request, f"Error updating supplier: {str(e)}")
    
    return render(request, 'dashboard/suppliers/update.html', {
        'supplier': supplier
    })

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    related_products = Product.objects.filter(supplier=supplier)
    
    if request.method == 'POST':
        try:
            related_products.update(supplier=None)
            supplier_name = supplier.name
            supplier.delete()
            
            messages.success(request, f"Supplier '{supplier_name}' and product references removed successfully!")
            return redirect('supplier_list')
        except Exception as e:
            messages.error(request, f"Error deleting supplier: {str(e)}")
            return redirect('supplier_detail', pk=pk)
    
    return render(request, 'dashboard/suppliers/confirm_delete.html', {
        'supplier': supplier,
        'products_count': related_products.count()
    })





def report_list(request):
    products = Product.objects.all().annotate(
        stock=Sum(
            F('movements__quantity') * 
            Case(
                When(movements__movement_type='in', then=1),
                When(movements__movement_type='out', then=-1),
                default=0
            )
        )
    )

    low_stock_products = [p for p in products if (p.stock or 0) < 10]
    low_stock_count = len(low_stock_products)

    product_stock_chart_data = [
        {'name': p.name, 'quantity': p.stock or 0} for p in products
    ]

    movement_queryset = (
        ProductMovement.objects
        .annotate(date_only=TruncDate('date'))
        .values('date_only')
        .annotate(total=Count('id'))
        .order_by('date_only')
    )
    movement_chart_labels = [item['date_only'].strftime('%Y-%m-%d') for item in movement_queryset]
    movement_chart_values = [item['total'] for item in movement_queryset]

    suppliers = Supplier.objects.all()
    supplier_labels = []
    supplier_values = []
    for supplier in suppliers:
        if hasattr(supplier, 'products'):
            count = supplier.products.count()
        else:
            count = supplier.product_set.count()
        supplier_labels.append(supplier.name)
        supplier_values.append(count)

    context = {
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'product_stock_data': json.dumps(product_stock_chart_data),
        'movement_chart_labels': json.dumps(movement_chart_labels),
        'movement_chart_values': json.dumps(movement_chart_values),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'total_products': products.count(),
        'total_movements': ProductMovement.objects.count(),
        'total_suppliers': suppliers.count(),
    }

    return render(request, 'dashboard/reports/report_list.html', context)


@require_POST
def delete_all_categories(request):
    Category.objects.all().delete()
    messages.success(request, "Toutes les catégories ont été supprimées avec succès.")
    return redirect('category_list')

@require_POST
def delete_all_products(request):
    Product.objects.all().delete()
    messages.success(request, "Tous les produits ont été supprimés avec succès.")
    return redirect('product_list')

@require_POST
def delete_all_movements(request):
    ProductMovement.objects.all().delete()
    messages.success(request, "Tous les mouvements ont été supprimés avec succès.")
    return redirect('movement_list')

@require_POST
def delete_all_suppliers(request):
    Supplier.objects.all().delete()
    messages.success(request, "Tous les fournisseurs ont été supprimés avec succès.")
    return redirect('supplier_list')










def export_reports_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading3']
    normal_style = styles['BodyText']

    elements.append(Paragraph("Inventory Report", title_style))
    elements.append(Spacer(1, 12))

    products = Product.objects.annotate(
        stock=Sum(
            F('movements__quantity') * 
            Case(
                When(movements__movement_type='in', then=1),
                When(movements__movement_type='out', then=-1),
                default=0
            )
        )
    )

    elements.append(Paragraph("Products Stock", subtitle_style))
    data = [["Name", "Category", "Supplier", "Stock", "Price (DH)"]]

    for p in products:
        supplier_name = p.supplier.name if p.supplier else "No Supplier"
        category_name = p.category.name if p.category else "No Category"
        data.append([p.name, category_name, supplier_name, p.stock or 0, f"{p.price}"])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3B82F6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F3F4F6")])
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    low_stock_products = [p for p in products if (p.stock or 0) < 10]
    elements.append(Paragraph("Low Stock Alerts (threshold <10)", subtitle_style))
    if low_stock_products:
        data = [["Name", "Stock", "Status"]]
        for p in low_stock_products:
            status = "Critical" if (p.stock or 0) < 5 else "Low"
            data.append([p.name, p.stock or 0, status])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EF4444")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FEE2E2")])
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No low stock products found.", normal_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Product Movements", subtitle_style))
    movements = ProductMovement.objects.select_related('product').order_by('-date')
    data = [["Date", "Product", "Type", "Quantity", "Description"]]
    for m in movements:
        data.append([localtime(m.date).strftime("%Y-%m-%d %H:%M"), m.product.name, m.movement_type.title(), m.quantity, m.description or ""])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#10B981")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#D1FAE5")])
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Suppliers", subtitle_style))
    suppliers = Supplier.objects.all()
    data = [["Name", "Phone", "Email", "Products Supplied"]]
    for s in suppliers:
        product_count = s.products.count() if hasattr(s, 'products') else s.product_set.count()
        data.append([s.name, s.phone, s.email or "-", product_count])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8B5CF6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#EDE9FE")])
    ]))
    elements.append(table)

    doc.build(elements)
    return response
