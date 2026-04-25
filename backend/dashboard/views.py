from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Product
from invoicing.models import Invoice


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        product_count = Product.objects.count()
        active_product_count = Product.objects.filter(is_active=True).count()
        invoice_count = Invoice.objects.count()

        data = {
            "role": request.user.role,
            "products": {
                "total": product_count,
                "active": active_product_count,
            },
            "invoices": {
                "total": invoice_count,
                "draft": Invoice.objects.filter(
                    status=Invoice.InvoiceStatus.DRAFT
                ).count(),
                "sent": Invoice.objects.filter(
                    status=Invoice.InvoiceStatus.SENT
                ).count(),
                "paid": Invoice.objects.filter(
                    status=Invoice.InvoiceStatus.PAID
                ).count(),
            },
        }
        return Response(data)
