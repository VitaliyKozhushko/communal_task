from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import House, Apartment, Meter, MeterType, CalculationProgress
from .serializers import (HouseSerializer,
                          ApartmentSerializer,
                          ApartmentWithHouseSerializer,
                          MeterByHouseSerializer,
                          MeterSerializer,
                          MeterTypeSerializer,
                          HouseListSerializer)
from celery.result import AsyncResult
from .celery_tasks import calculate_utility_bills_for_house_task

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

class UtilityBillCalculationView(APIView):
  def post(self, request, house_id):
    year = request.data.get('year')
    month = request.data.get('month')
    delay = request.data.get('delay', 0)

    if not all([year, month]):
      return Response({"error": "Необходимо указать год и месяц для расчета."}, status=status.HTTP_400_BAD_REQUEST)

    try:
      year = int(year)
      month = int(month)
      delay = int(delay)

      house = House.objects.get(id=house_id)
      if not house:
        return Response({"error": "Указанного дома не существует"}, status=status.HTTP_400_BAD_REQUEST)

      task = calculate_utility_bills_for_house_task.delay(house_id, year, month, delay)

      return Response({"task_id": task.id, 'status': 'Расчет квартплаты выполняется'}, status=status.HTTP_202_ACCEPTED)
    except House.DoesNotExist:
      return Response({"error": "Дом не найден."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
      return Response({"error": "Некорректный формат года или месяца."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({"error": f"Произошла ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskResultView(APIView):
  def get(self, request, task_id):
    task_result = AsyncResult(task_id)

    if task_result.state == 'PENDING':
      return Response({"status": "Расчет квартплаты в очереди на выполнение"}, status=status.HTTP_200_OK)

    elif task_result.state == 'STARTED':
      return Response({"status": "Расчет квартплаты выполняется"}, status=status.HTTP_200_OK)

    elif task_result.state == 'SUCCESS':
      result = task_result.result
      return Response({"status": "Расчет квартплаты выполнен", "data": result}, status=status.HTTP_200_OK)

    elif task_result.state == 'FAILURE':
      return Response({"status": "Ошибка выполнения расчета квартплаты", "error": str(task_result.result)},
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"status": "Неизвестное состояние расчета квартплаты"}, status=status.HTTP_400_BAD_REQUEST)