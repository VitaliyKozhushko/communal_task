from rest_framework import viewsets, generics
from .models import House, Apartment, Meter, MeterType, Tariff
from .serializers import HouseSerializer, ApartmentWithHouseSerializer, MeterSerializer, MeterTypeSerializer, HouseListSerializer

class HouseListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseListSerializer
    http_method_names = ['get']

class HouseDetailView(generics.RetrieveUpdateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    lookup_field = 'id'

class ApartmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentWithHouseSerializer
    lookup_field = 'id'

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