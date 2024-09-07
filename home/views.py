from rest_framework import viewsets, generics
from .models import House, Apartment, Meter, MeterType, Tariff
from .serializers import HouseSerializer, ApartmentSerializer, MeterSerializer, MeterTypeSerializer, HouseListSerializer

class HouseListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseListSerializer
    http_method_names = ['get']

class HouseDetailView(generics.RetrieveUpdateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    lookup_field = 'id'

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

    def get_queryset(self):
        house_id = self.request.query_params.get('house_id')
        if house_id:
            return self.queryset.filter(house_id=house_id)
        return self.queryset

class MeterViewSet(viewsets.ModelViewSet):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer

    def get_queryset(self):
        apartment_id = self.request.query_params.get('apartment_id')
        if apartment_id:
            return self.queryset.filter(apartment_id=apartment_id)
        return self.queryset

class MeterTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MeterType.objects.all()
    serializer_class = MeterTypeSerializer


