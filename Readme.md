## Примечания

- в карточке дома можно посмотреть список квартир, относящихся к дому и сразу перейти в нужную
  кликнув на ссылку
- в карточке квартиры можно посмотреть список счетчиков, относящихся к квартире
- список квартир можно сортировать также по площади и дому
- список квартир можно фильтровать по дому
- доавлена модель для создания типов счетчиков (ХВС, ГВС и т.д.)
- для простоты выполнения тестового задания показания счетчика должны иметь вид:
{
    "2024-01": 120.5,
    "2024-02": 135.7,
    "2024-03": 142.9
}
- счетчики можно фильтровать по квартире и по дому
- при добавлении тарифа можно выбрать либо тип счетчика, либо указать название:
  - если выбран тип счетчика, то необходимо указать только цену. Ед. измерения автоматически подтянется из данных по счетчику
  - если указать название, то необходимо указать и единицу измерения

