from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from sabzbin_user.models import UserAddress

USER = get_user_model()


class ActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ("id", "first_name", "last_name", 'avatar_thumbnail')


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(min_length=3, max_length=50, label=_('name'), required=True)
    last_name = serializers.CharField(min_length=3, max_length=50, label=_('name'), required=True)
    phone_number = PhoneNumberField(label=_('mobile number'), required=True)

    class Meta:
        model = USER
        fields = ("first_name",
                  "last_name",
                  'phone_number')


# noinspection PyMissingOrEmptyDocstring
class LoginSerializer(serializers.Serializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    phone_number = PhoneNumberField(label=_('phone number'), required=True)


class SMSVerificationSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    phone_number = PhoneNumberField(label=_('phone number'), required=True)
    security_code = serializers.CharField(min_length=settings.SMS_VERIFY_CODE_LENGTH,
                                          max_length=settings.SMS_VERIFY_CODE_LENGTH,
                                          label=_('security code'), required=True, )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            int(attrs.get("security_code", None), )
        except ValueError:
            raise serializers.ValidationError(_("Security code is not valid"))

        return attrs


class ActiveUserProfileSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(source='avatar_thumbnail', read_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = USER
        fields = ("first_name",
                  "last_name",
                  "avatar",
                  'thumbnail')


class UserProfilePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = ("id",
                  "first_name",
                  "last_name",
                  "avatar",
                  "avatar_thumbnail",
                  # "address",
                  )
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(source='avatar_thumbnail', read_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = USER
        fields = ("id",
                  "first_name",
                  "last_name",
                  "avatar",
                  "thumbnail",
                  "phone_number",
                  # "address",
                  )
        read_only_fields = ("thumbnail",
                            "phone_number",)


class SecurityCodeSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    security_code = serializers.CharField(min_length=settings.SMS_VERIFY_CODE_LENGTH,
                                          max_length=settings.SMS_VERIFY_CODE_LENGTH,
                                          label=_('security code'),
                                          required=True, )

    def validate_security_code(self, security_code: str) -> str:
        try:
            int(security_code)
        except ValueError:
            raise serializers.ValidationError(_("Security code is not valid"))

        return security_code


class AddressesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('id', 'address',)
        read_only_fields = "id",


class AddressesDetailSerializer(AddressesListSerializer):
    class Meta(AddressesListSerializer.Meta):
        fields = ('id', 'address', 'coordinates',)


class ScoreSerialize(serializers.Serializer):
    referral_points = serializers.CharField(read_only=True)
    profile_points = serializers.CharField(read_only=True)
