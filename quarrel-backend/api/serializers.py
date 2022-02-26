from rest_framework import serializers
from .models import Quarreler, Game


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quarreler
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
        depth = 1


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
