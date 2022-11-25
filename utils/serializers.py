from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
