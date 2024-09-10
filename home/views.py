from rest_framework import viewsets, generics, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import House, Apartment, Meter, MeterType
from .serializers import (HouseSerializer,
                          ApartmentSerializer,
                          ApartmentWithHouseSerializer,
                          MeterByHouseSerializer,
                          MeterSerializer,
                          MeterTypeSerializer,
                          HouseListSerializer)
from celery.result import AsyncResult
from .celery_tasks import calculate_utility_bills_for_house_task
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class HouseListViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
  queryset = House.objects.all()
  serializer_class = HouseListSerializer
  http_method_names = ['get', 'post']

  @swagger_auto_schema(
    operation_description='Получить список домов',
    operation_summary='Список домов',
    tags=['Управление домом'],
    responses={200: HouseListSerializer(many=True)},
  )
  def list(self, request, *args, **kwargs):
    """
    Возвращает список всех доступных домов.
    """
    return super().list(request, *args, **kwargs)

  @swagger_auto_schema(
    operation_description='Создать новый дом',
    operation_summary='Дбавление дома',
    tags=['Управление домом'],
    request_body=HouseListSerializer,
    responses={201: HouseListSerializer}
  )
  def create(self, request, *args, **kwargs):
    """
    Создает новый дом с уникальным адресом.
    """
    return super().create(request, *args, **kwargs)

class HouseDetailView(generics.RetrieveUpdateAPIView):
  queryset = House.objects.prefetch_related(
        'apartments__meters',
        'apartments__meters__meter_type'
  )
  serializer_class = HouseSerializer
  lookup_field = 'id'
  http_method_names = ['get', 'put']

  @swagger_auto_schema(
    operation_description='Получить детали дома с его квартирами и счётчиками',
    operation_summary='Данные по дому (квартиры, счетчики)',
    tags=['Управление домом'],
    responses={200: HouseSerializer}
  )
  def get(self, request, *args, **kwargs):
    """
    Возвращает детали дома, включая связанные квартиры и счётчики.
    """
    return super().get(request, *args, **kwargs)

  @swagger_auto_schema(
    operation_description='Обновить детали дома',
    operation_summary='Редактирование дома',
    tags=['Управление домом'],
    request_body=HouseSerializer,
    responses={200: HouseSerializer}
  )
  def put(self, request, *args, **kwargs):
    """
    Обновляет информацию о доме
    """
    return super().put(request, *args, **kwargs)

class ApartmentCreateView(generics.CreateAPIView):
  queryset = Apartment.objects.all()
  serializer_class = ApartmentSerializer

  @swagger_auto_schema(
    operation_description='Создать новую квартиру',
    operation_summary='Добавление квартиры',
    tags=['Управление квартирой'],
    request_body=ApartmentSerializer,
    responses={201: ApartmentSerializer}
  )
  def post(self, request, *args, **kwargs):
    """
    Создает новую квартиру. Параметры должны включать номер дома, номер квартиры и площадь.
    """
    return super().post(request, *args, **kwargs)

class ApartmentDetailView(generics.RetrieveUpdateAPIView):
  queryset = Apartment.objects.all()
  serializer_class = ApartmentWithHouseSerializer
  lookup_field = 'id'
  http_method_names = ['get', 'put']

  @swagger_auto_schema(
    operation_description='Получить информацию о квартире с деталями счётчиков и ID дома',
    operation_summary='Данные по квартире (счетчики, дом)',
    tags=['Управление квартирой'],
    responses={200: ApartmentWithHouseSerializer}
  )
  def get(self, request, *args, **kwargs):
    """
    Возвращает детали квартиры, включая ID дома и список счётчиков.
    """
    return super().get(request, *args, **kwargs)

  @swagger_auto_schema(
    operation_description='Обновить данные о квартире',
    operation_summary='Редактирование квартиры',
    tags=['Управление квартирой'],
    request_body=ApartmentWithHouseSerializer,
    responses={200: ApartmentWithHouseSerializer}
  )
  def put(self, request, *args, **kwargs):
    """
    Обновляет информацию о квартире (номер, площадь, и счётчики).
    """
    return super().put(request, *args, **kwargs)

class MeterTypeViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = MeterType.objects.all()
  serializer_class = MeterTypeSerializer

  @swagger_auto_schema(
    operation_description='Получить список всех типов счётчиков',
    operation_summary='Список типов счётчика',
    tags=['Управление счётчиками'],
    responses={200: MeterTypeSerializer(many=True)}
  )
  def list(self, request, *args, **kwargs):
    """
    Возвращает список всех доступных типов счётчиков.
    """
    return super().list(request, *args, **kwargs)

  @swagger_auto_schema(
    operation_description='Получить данные типа счётчика',
    operation_summary='Данные по типу счётчика',
    tags=['Управление счётчиками'],
    responses={200: MeterTypeSerializer}
  )
  def retrieve(self, request, *args, **kwargs):
    """
    Возвращает данные типа счётчика по ID.
    """
    return super().retrieve(request, *args, **kwargs)

class MetersByHouseView(generics.ListAPIView):
  serializer_class = MeterByHouseSerializer

  def get_queryset(self):
    house_id = self.kwargs['house_id']
    apartment_id = self.request.query_params.get('apartment_id', None)

    queryset = Meter.objects.filter(apartment__house_id=house_id)

    if apartment_id is not None:
      queryset = queryset.filter(apartment_id=apartment_id)

    return queryset

  @swagger_auto_schema(
    operation_description='Получить список счётчиков для дома. Можно отфильтровать по квартире.',
    operation_summary='Список счётчиков по дому (фильтрация по квартире)',
    tags=['Управление счётчиками'],
    manual_parameters=[
      openapi.Parameter(
        'apartment_id',
        openapi.IN_QUERY,
        description='ID квартиры для фильтрации',
        type=openapi.TYPE_INTEGER
      )
    ],
    responses={200: MeterByHouseSerializer(many=True)}
  )
  def get(self, request, *args, **kwargs):
    """
    Возвращает список всех счётчиков, связанных с домом по `house_id`.
    Дополнительно можно фильтровать по `apartment_id`.
    """
    return super().get(request, *args, **kwargs)


class MeterDetailView(generics.RetrieveUpdateAPIView):
    queryset = Meter.objects.all()
    serializer_class = MeterByHouseSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'put']

    @swagger_auto_schema(
      operation_description='Получить информацию о счётчике',
      operation_summary='Данные по счётчику',
      tags=['Управление счётчиками'],
      responses={200: MeterByHouseSerializer}
    )
    def get(self, request, *args, **kwargs):
      """
      Возвращает детали счётчика по его ID.
      """
      return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
      operation_description='Обновить данные счётчика',
      operation_summary='Редактирование счётчика',
      tags=['Управление счётчиками'],
      request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
          'id': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='ID счётчика',
            example=1
          ),
          'meter_number': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Номер счётчика',
            example='123456789'
          ),
          'meter_type': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='ID типа счётчика',
            example=2
          ),
          'readings': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Показания счётчика',
            example={
              '2024-09': 150.0
            }
          )
        },
        required=['id', 'meter_number', 'meter_type']
      ),
      responses={
        200: openapi.Response(
          description='Успешное обновление данных счётчика',
          examples={
            'application/json': {
              'id': 1,
              'meter_number': '123456789',
              'meter_type': 2,
              'readings': {
                '2024-09': 150.0
              }
            }
          }
        ),
        400: openapi.Response(
          description='Неправильный запрос',
          examples={
            'application/json': {
              'error': 'Некорректные данные.'
            }
          }
        ),
        404: openapi.Response(
          description='Счётчик не найден',
          examples={
            'application/json': {
              'error': 'Счётчик не найден.'
            }
          }
        )
      }
    )
    def put(self, request, *args, **kwargs):
      """
      Обновляет информацию о счётчике (номер, тип, показания).
      """
      return super().put(request, *args, **kwargs)

class MeterViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
  queryset = Meter.objects.all()
  serializer_class = MeterSerializer
  http_method_names = ['get', 'post']

  @swagger_auto_schema(
    operation_description='Получить список всех счётчиков',
    operation_summary='Список счётчиков',
    tags=['Управление счётчиками'],
    responses={200: MeterSerializer(many=True)}
  )
  def list(self, request, *args, **kwargs):
    """
    Возвращает список всех счётчиков.
    """
    return super().list(request, *args, **kwargs)

  @swagger_auto_schema(
    operation_description='Создать новый счётчик',
    operation_summary='Добавление счётчика',
    tags=['Управление счётчиками'],
    request_body=MeterSerializer,
    responses={201: MeterSerializer}
  )
  def create(self, request, *args, **kwargs):
    """
    Создаёт новый счётчик.
    """
    return super().create(request, *args, **kwargs)

class UtilityBillCalculationView(APIView):
  @swagger_auto_schema(
    operation_description='Запуск задачи расчета квитанций за коммунальные услуги для указанного дома',
    operation_summary='Запуск расчета квитанции',
    tags=['Расчет ком. услуг'],
    request_body=openapi.Schema(
      type=openapi.TYPE_OBJECT,
      required=['year', 'month'],
      properties={
        'year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Год расчета'),
        'month': openapi.Schema(type=openapi.TYPE_INTEGER, description='Месяц расчета'),
        'delay': openapi.Schema(type=openapi.TYPE_INTEGER, description='Задержка в секундах перед началом расчета',
                                default=0)
      }
    ),
    responses={
      202: openapi.Response(description='Задача по расчету квитанций запущена', examples={
        'application/json': {
          'task_id': '1234567890',
          'status': 'Расчет квартплаты выполняется'
        }
      }),
      400: openapi.Response(description='Неправильный запрос', examples={
        'application/json': {
          'error': 'Некорректный формат года или месяца.'
        }
      }),
      404: openapi.Response(description='Дом не найден', examples={
        'application/json': {
          'error': 'Дом не найден.'
        }
      }),
    }
  )

  def post(self, request, house_id):
    year = request.data.get('year')
    month = request.data.get('month')
    delay = request.data.get('delay', 0)

    if not all([year, month]):
      return Response({'error': 'Необходимо указать год и месяц для расчета.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      year = int(year)
      month = int(month)
      delay = int(delay)

      house = House.objects.get(id=house_id)
      if not house:
        return Response({'error': 'Указанного дома не существует'}, status=status.HTTP_400_BAD_REQUEST)

      task = calculate_utility_bills_for_house_task.delay(house_id, year, month, delay)

      return Response({'task_id': task.id, 'status': 'Расчет квартплаты выполняется'}, status=status.HTTP_202_ACCEPTED)
    except House.DoesNotExist:
      return Response({'error': 'Дом не найден.'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
      return Response({'error': 'Некорректный формат года или месяца.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({'error': f'Произошла ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskResultView(APIView):
  @swagger_auto_schema(
    operation_description='Получить статус выполнения задачи расчета квартплаты',
    operation_summary='Получение готовой квитанции',
    tags=['Расчет ком. услуг'],
    manual_parameters=[
      openapi.Parameter(
        'task_id',
        openapi.IN_PATH,
        description='ID задачи для получения статуса',
        type=openapi.TYPE_STRING
      )
    ],
    responses={
      200: openapi.Response(
        description='Статус выполнения задачи',
        examples={
          'application/json': {
            'status': 'Расчет квартплаты выполнен',
            'data': [
              {
                'apartment_id': 0,
                'apartment_number': 0,
                'house_id': 0,
                'address': 'string',
                'date': 'string',
                'calc_rent': [
                  {
                    'id': 0,
                    'name': 'string',
                    'consumption': 0,
                    'unit': 'string',
                    'cost': 0
                  }
                ],
                'absent_meters': [
                  {
                    'id': 0,
                    'name': 'name'
                  }
                ]
              }
            ]
          }
        }
      ),
      202: openapi.Response(
        description='Задача по расчету квитанций запущена',
        examples={
          'application/json': {
            'task_id': '1234567890',
            'status': 'Расчет квартплаты выполняется'
          }
        },
      ),
      400: openapi.Response(description='Неизвестное состояние расчета квартплаты', examples={
        'application/json': {
          'status': 'Неизвестное состояние расчета квартплаты'
        }
      })
    }
  )

  def get(self, request, task_id):
    task_result = AsyncResult(task_id)

    if task_result.state == 'PENDING':
      return Response({'status': 'Расчет квартплаты в очереди на выполнение'}, status=status.HTTP_200_OK)

    elif task_result.state == 'STARTED':
      return Response({'status': 'Расчет квартплаты выполняется'}, status=status.HTTP_200_OK)

    elif task_result.state == 'SUCCESS':
      result = task_result.result
      return Response({'status': 'Расчет квартплаты выполнен', 'data': result}, status=status.HTTP_200_OK)

    elif task_result.state == 'FAILURE':
      return Response({'status': 'Ошибка выполнения расчета квартплаты', 'error': str(task_result.result)},
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'Неизвестное состояние расчета квартплаты'}, status=status.HTTP_400_BAD_REQUEST)