from rest_framework import serializers

class RequestDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    month_count = serializers.IntegerField()



