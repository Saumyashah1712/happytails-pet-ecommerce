from django.contrib import admin
from django.contrib.auth import login
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from .models import Order
from .models import Product
from textwrap import wrap
from .models import Customer

# Register your models here.
from .models import Category,Sub_Category

admin.site.register(Category)
admin.site.register(Sub_Category)

class AdminUser(admin.ModelAdmin):
    list_display = ['first_name','last_name','email_address','password','mobile_number']

admin.site.register(Customer, AdminUser)


def generate_order_pdf(modeladmin, request, queryset):
    """
    Generate a PDF report for selected orders.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Company Name
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, height - 40, "HappyTails")

    # Report Date
    pdf.setFont("Helvetica", 12)
    pdf.drawString(400, height - 60, f"Date: {datetime.today().strftime('%Y-%m-%d')}")

    # Report Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, height - 80, "Order Report")

    # Table Headers
    pdf.setFont("Helvetica-Bold", 12)
    y_position = height - 110
    pdf.drawString(30, y_position, "ID")
    pdf.drawString(80, y_position, "Product")
    pdf.drawString(250, y_position, "Customer")
    pdf.drawString(370, y_position, "Qty")
    pdf.drawString(410, y_position, "Price")
    pdf.drawString(470, y_position, "Total Price")
    pdf.drawString(550, y_position, "Date")

    pdf.line(30, y_position - 5, 580, y_position - 5)

    # Table Data
    pdf.setFont("Helvetica", 10)
    y_position -= 20

    for order in queryset:
        pdf.drawString(30, y_position, str(order.id))

        # Wrap product name
        product_lines = wrap(order.product.name, width=20)
        for i, line in enumerate(product_lines):
            pdf.drawString(80, y_position - (i * 12), line)

        # Display Customer Name (Truncated if necessary)
        pdf.drawString(250, y_position, order.customer.first_name[:15])

        pdf.drawString(370, y_position, str(order.quantity))
        pdf.drawString(410, y_position, str(order.price))
        pdf.drawString(470, y_position, str(order.total_price))

        # Ensuring date is fully visible
        pdf.drawString(520, y_position, order.date.strftime('%Y-%m-%d'))

        # Adjusting for multi-line product names
        y_position -= 20 + (len(product_lines) - 1) * 12

        # Add new page if needed
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)  # Change from 10 to 9
            y_position = height - 50

    pdf.showPage()
    pdf.save()
    return response

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'sub_category', 'price', 'date']
    search_fields = ['name', 'category__name', 'sub_category__name']
    list_filter = ['category', 'sub_category', 'date']
    actions = ['generate_product_pdf']

    def generate_product_pdf(modeladmin, request, queryset):
        """
        Generate a PDF report for selected products in Django Admin.
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="product_report.pdf"'

        pdf = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Add Company Name
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(200, height - 40, "HappyTails")  # Company Name

        # Add Date
        pdf.setFont("Helvetica", 12)
        pdf.drawString(400, height - 60, f"Date: {datetime.today().strftime('%Y-%m-%d')}")

        # Add Report Title
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, height - 80, "Product Report")

        # Table Headers
        pdf.setFont("Helvetica-Bold", 12)
        y_position = height - 110
        pdf.drawString(30, y_position, "ID")
        pdf.drawString(80, y_position, "Product Name")
        pdf.drawString(250, y_position, "Category")
        pdf.drawString(350, y_position, "Sub-Category")
        pdf.drawString(450, y_position, "Price")
        pdf.drawString(520, y_position, "Date")

        pdf.line(30, y_position - 5, 570, y_position - 5)

        # Table Data
        pdf.setFont("Helvetica", 9)
        y_position -= 20

        for product in queryset:
            pdf.drawString(30, y_position, str(product.id))

            # Wrap long product names
            product_name_lines = wrap(product.name, width=25)
            for i, line in enumerate(product_name_lines):
                pdf.drawString(80, y_position - (i * 12), line)

            pdf.drawString(250, y_position, product.category.name[:15])
            pdf.drawString(350, y_position, product.sub_category.name[:15])
            pdf.drawString(450, y_position, str(product.price))
            pdf.drawString(520, y_position, product.date.strftime('%Y-%m-%d'))

            y_position -= 20 + (len(product_name_lines) - 1) * 12

            if y_position < 50:  # Add a new page if needed
                pdf.showPage()
                pdf.setFont("Helvetica", 9)
                y_position = height - 50

        pdf.showPage()
        pdf.save()
        return response

    generate_product_pdf.short_description = "Download Selected Products as PDF"

admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'customer', 'quantity', 'price', 'total_price', 'date']
    actions = [generate_order_pdf]  # Add the PDF action to admin
admin.site.register(Order,OrderAdmin)