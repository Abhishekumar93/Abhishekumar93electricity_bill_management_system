from rest_framework import serializers

from .models import PortalUser


class PortalUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if not validated_data['is_staff']:
            return PortalUser.objects.create(**validated_data)
        else:
            return PortalUser.objects.create_superuser(**validated_data)

    class Meta:
        model = PortalUser
        fields = '__all__'


class PortalUserBasicDataSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(
        source='get_username')

    def get_username(self, instance) -> str:
        return instance.get_full_name()

    class Meta:
        model = PortalUser
        fields = ('id', 'username')


class PortalUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PortalUser
        fields = ('id', 'first_name', 'last_name', 'email',
                  'consumer_number', 'staff_id', 'is_active')
