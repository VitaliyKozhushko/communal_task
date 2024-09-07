from rest_framework import viewsets, generics
from .models import House, Apartment, Meter, MeterType, Tariff
from .serializers import HouseSerializer, ApartmentSerializer, ApartmentWithHouseSerializer, MeterByHouseSerializer, MeterSerializer, MeterTypeSerializer, HouseListSerializer

class HouseListViewSet(viewsets.ModelViewSet):
  queryset = House.objects.all()
  serializer_class = HouseListSerializer

class HouseDetailView(generics.RetrieveUpdateAPIView):
  queryset = House.objects.prefetch_related(
        'apartments__meters',
        'apartments__meters__meter_type'
  )
  serializer_class = HouseSerializer
  lookup_field = 'id'

class ApartmentCreateView(generics.CreateAPIView):
  queryset = Apartment.objects.all()
  serializer_class = ApartmentSerializer

class ApartmentDetailView(generics.RetrieveUpdateAPIView):
  queryset = Apartment.objects.all()
  serializer_class = ApartmentWithHouseSerializer
  lookup_field = 'id'

class MeterTypeViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = MeterType.objects.all()
  serializer_class = MeterTypeSerializer

class MetersByHouseView(generics.ListAPIView):
  serializer_class = MeterByHouseSerializer

  def get_queryset(self):
    house_id = self.kwargs['house_id']
    apartment_id = self.request.query_params.get('apartment_id', None)

    queryset = Meter.objects.filter(apartment__house_id=house_id)

    if apartment_id is not None:
      queryset = queryset.filter(apartment_id=apartment_id)

    return queryset


class MeterDetailView(generics.RetrieveUpdateAPIView):
    queryset = Meter.objects.all()
    serializer_class = MeterByHouseSerializer
    lookup_field = 'id'

class MeterViewSet(viewsets.ModelViewSet):
  queryset = Meter.objects.all()
  serializer_class = MeterSerializer
