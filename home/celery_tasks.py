from celery import shared_task
from .models import CalculationProgress
from .services.calc_tarif import calculate_utility_bills_for_house
import time

@shared_task(bind=True)
def calculate_utility_bills_for_house_task(self, house_id, year, month, delay=0):
  try:
    time.sleep(delay)

    progress = CalculationProgress.objects.create(house_id=house_id, year=year, month=month, status="в работе")

    result = calculate_utility_bills_for_house(house_id, year, month)

    progress.status = "готово"
    progress.save()

    return result
  except Exception as e:
    progress.status = "ошибка"
    progress.error_message = str(e)
    progress.save()
    raise e
