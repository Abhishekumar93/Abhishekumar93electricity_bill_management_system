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
    user_role = serializers.SerializerMethodField(source='get_user_role')

    def get_username(self, instance) -> str:
        return instance.get_full_name()

    def get_user_role(self, instance) -> str:
        role_type = "consumer"

        if instance.is_staff == True:
            role_type = "staff"

        return role_type

    class Meta:
        model = PortalUser
        fields = ('id', 'username', 'email', 'user_role')


class PortalUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PortalUser
        fields = ('id', 'first_name', 'last_name', 'email',
                  'consumer_number', 'staff_id', 'is_active')


class PortalUserDetailSerializer(PortalUserUpdateSerializer):

    class Meta(PortalUserUpdateSerializer.Meta):
        fields = PortalUserUpdateSerializer.Meta.fields + \
            ('phone_number', 'date_joined', 'last_login')
