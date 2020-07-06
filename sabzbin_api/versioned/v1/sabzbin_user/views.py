import bleach
from django.contrib.auth import get_user_model, login
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, \
    CreateModelMixin
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from sabzbin_user import functions
from sabzbin_user.models import UserAddress, UserScore
from . import serializers
from .serializers import ScoreSerialize

USER = get_user_model()


class VerificationViewSet(GenericViewSet):
    serializer_class = None

    @swagger_auto_schema(
        operation_description="Register new user then send sms or Detect old user then send sms",
        responses={200: 'Already registered. Authentication SMS sent',
                   201: 'Authentication SMS sent',
                   500: 'OopS,An error has occurred. SMS not sent', })
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=serializers.RegisterSerializer,
    )
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data["last_name"]
        try:
            # Duplicates should be prevented.
            with transaction.atomic():
                USER.objects.create_user(phone_number=phone_number,
                                         first_name=bleach.clean(first_name),
                                         last_name=bleach.clean(last_name), )
            message = _("Authentication SMS sent")
            status_code = 201
            code = functions.send_sms_verify_code(phone_number)
        except IntegrityError:
            USER.objects.get(phone_number=phone_number)
            message = _("already registered. Authentication SMS sent")
            status_code = 200
            code = functions.send_sms_verify_code(phone_number)
        return Response(data={"message": message,
                              'verify_code': code, }, status=status_code)

    @swagger_auto_schema(
        operation_description="Send sms to old user to login ",
        responses={200: 'Authentication SMS sent',
                   404: "This phone number is not registered. Please register now",
                   500: "OopS,An error has occurred. SMS not sent", })
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny],
            serializer_class=serializers.LoginSerializer,
            )
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        try:
            USER.objects.get(phone_number=phone_number)
            message = _("Authentication SMS sent")
            status_code = 200
            code = functions.send_sms_verify_code(phone_number)
            return Response(data={"message": message, 'verify_code': code, }, status=status_code)
        except USER.DoesNotExist:
            message = _("This phone number is not registered. Please register now")
            status_code = 404
            return Response(data={"message": message, }, status=status_code)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    @swagger_auto_schema(operation_description="Verify sand sms to login and register ",
                         responses={200: 'Security code is valid.',
                                    400: 'Security code is NOT valid or has expired.'})
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny],
            serializer_class=serializers.SMSVerificationSerializer, )
    def verify(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data["phone_number"]
            security_code = serializer.validated_data["security_code"]
            user = USER.objects.filter(phone_number=phone_number).first()
            if user:
                if user.authenticate(str(security_code)):
                    user.verified = True
                    user.save()
                    login(request, user)  # for SessionAuthentication
                    refresh = self.get_token(user)
                    return Response(status=status.HTTP_200_OK,
                                    data={"message": _("Security code is valid."),
                                          "refresh": str(refresh),
                                          'access': str(refresh.access_token)})

        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"message": _("Security code is NOT valid or has expired.")})


class ProfileAPIViewSet(RetrieveModelMixin,
                        GenericViewSet):
    """
        Retrieve or update User Profile.
    """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = serializers.UserProfilePublicSerializer
    pagination_class = None
    queryset = USER.objects.filter(is_active=True)

    @action(detail=False, methods=['GET'], url_path='view', url_name='view',
            permission_classes=[IsAuthenticated],
            serializer_class=serializers.UserProfileSerializer)
    def view(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=['PATCH', 'PUT'], url_path='edit', url_name='edit',
            permission_classes=[IsAuthenticated],
            serializer_class=serializers.UserProfileSerializer)
    def edit(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            valid_response = Response(serializer.data)
        else:
            valid_response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return valid_response

    @swagger_auto_schema(
        operation_description="Send sms to verify before delete",
        responses={
            200: 'Authentication SMS sent',
            500: 'OopS,An error has occurred. SMS not sent'
        })
    @action(detail=False, methods=['DELETE'], permission_classes=[IsAuthenticated], )
    def delete_account(self, request):
        code = functions.send_sms_verify_code(request.user.phone_number)
        message = _("Authentication SMS sent")
        return Response(status=200, data={'message': message,
                                          'verify_code': code, })

    @swagger_auto_schema(
        operation_description="Verify then delete account",
        responses={204: 'Your Account Deleted',
                   400: 'Security code is NOT valid or has expired.'})
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated],
            serializer_class=serializers.SecurityCodeSerializer)
    def delete_account_verification(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            security_code = serializer.validated_data["security_code"]
            if user.authenticate(str(security_code)):
                USER.objects.get(pk=user.pk).delete()
                return Response(status=status.HTTP_204_NO_CONTENT,
                                data={'massage': _("Your Account Deleted")})
        return Response(status=400,
                        data={"message": _("Security code is NOT valid or has expired.")})

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated],
            url_path='my_addresses', url_name='my-addresses',
            serializer_class=serializers.AddressesDetailSerializer, pagination_class=CursorPagination)
    def my_addresses(self, request):
        instance = request.user
        queryset = UserAddress.objects.filter(user=instance)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated],
            url_path='add_address', url_name='add-address',
            serializer_class=serializers.AddressesDetailSerializer, )
    def add_address(self, request):
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _scores(user):
        points = UserScore.objects.filter(user=user)
        referral_points = points.filter(type='Referral').aggregate(Sum('point'))
        profile_points = points.filter(type='Profile').aggregate(Sum('point'))
        return Response(data={'referral_points': referral_points['point__sum'],
                              'profile_points': profile_points['point__sum']},
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='user_score', url_name='user-scores', serializer_class=ScoreSerialize)
    def user_scores(self, request, id):
        instance = self.get_object()
        return self._scores(instance)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated],
            url_path='my_score', url_name='my-scores', serializer_class=ScoreSerialize)
    def my_scores(self, request):
        instance = request.user
        return self._scores(instance)


class AddressAPIViewSet(ListModelMixin,
                        CreateModelMixin,
                        RetrieveModelMixin,
                        UpdateModelMixin,
                        DestroyModelMixin,
                        GenericViewSet, ):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = serializers.AddressesListSerializer
    pagination_class = CursorPagination

    def get_queryset(self):
        queryset = UserAddress.objects.filter(user=self.request.user)
        return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        if self.action == 'create' or self.detail:
            serializer_class = serializers.AddressesDetailSerializer
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
