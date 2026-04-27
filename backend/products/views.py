from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from .models import Product
from .serializers import ProductSerializer
import csv
from io import TextIOWrapper
from rest_framework.permissions import AllowAny, IsAuthenticated

# Bulk import products from CSV
class ProductBulkImportView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            csv_file = TextIOWrapper(file_obj.file, encoding="utf-8")
            reader = csv.DictReader(csv_file)
            products = []
            for row in reader:
                product = Product(
                    name=row.get("name", ""),
                    description=row.get("description", ""),
                    price=row.get("price", 0) or 0,
                    vat_rate=row.get("vat_rate", 0) or 0,
                    expiration_date=row.get("expiration_date") or None,
                    stock=row.get("stock", 0) or 0,
                    category=row.get("category", ""),
                    image_url=row.get("image_url", ""),
                )
                products.append(product)
            Product.objects.bulk_create(products)
            return Response(
                {"message": f"{len(products)} products imported."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


# Search endpoint for products
class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", "")
        if query:
            products = Product.objects.filter(
                models.Q(name__icontains=query) | models.Q(description__icontains=query)
            )
        else:
            products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
