from rest_framework.generics import GenericAPIView
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from .seralizers import RequestDateSerializer
from datetime import datetime


class DateView(GenericAPIView):
    serializer_class = RequestDateSerializer
    holiday_list = []
    holiday_only_date = []

    def get(self, *args, **kwargs):
        url = requests.get(
            'https://holidayapi.com/v1/holidays?pretty&country=KZ-ALA&year=2020&key=b0e1b52f-38ca-46f3-bb58-cffdb793b976')
        if url.json().get('holidays'):
            url = url.json().get('holidays')
            for holiday in url:
                if holiday['public']:
                    self.holiday_list.append(
                        'Название праздника:{0}, {1} - {2}'.format(holiday['name'], holiday['date'],
                                                                   holiday['observed']))
                    self.holiday_only_date.append(holiday['date'])
                    self.holiday_only_date.append(holiday['observed'])

            return Response(self.holiday_list, status=status.HTTP_200_OK)
        return Response(False, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        month, day, year = data['date'].month, data['date'].day, data['date'].year
        date_payment = []

        if not 0 < data['month_count'] < 13:
            return Response('Указан неверный номер месяца', status=status.HTTP_400_BAD_REQUEST)

        if (data['date'].strftime('%Y-%m-%d') in self.holiday_only_date) or (data['date'].weekday() in [5, 6]):
            return Response('Выходной или праздничный день', status=status.HTTP_400_BAD_REQUEST)

        for i in range(1, data['month_count']):
            if month + 1 > 12:
              month = 1
              year += 1
            month += 1
            check_date = datetime(year, month, day).date()

            if check_date.strftime('%Y-%m-%d') in self.holiday_only_date or check_date.weekday() in [5, 6]:
                if check_date.weekday() in [5, 6]:
                  for p in range(1,7):
                    weekd = check_date.day + p
                    if weekd > 32:
                      month += 1
                      weekd = weekd - 31
                    weekd = datetime(year,month, weekd)
                    if not weekd.day in [5,6] or weekd in check_date.strftime('%Y-%m-%d') in self.holiday_only_date:
                      date_payment.append((year,month,weekd.day + 1))
                      break
            else:
              date_payment.append((year, month, day))

        return Response('Дата взятия кредита: {0}, последующие оплаты: {1}'.format(data['date'], date_payment), status=status.HTTP_200_OK)
