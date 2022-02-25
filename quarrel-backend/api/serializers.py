from rest_framework import serializers
from .models import FarmBoy, FarmVegetable, VegetableOrder, Order, Market, Farm, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quarreler
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
        depth = 1


class MainTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainTable
        fields = '__all__'
