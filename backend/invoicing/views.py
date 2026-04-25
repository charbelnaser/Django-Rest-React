from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from authentication.permissions import IsAdminManagerWriteAdminDelete

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminManagerWriteAdminDelete]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
