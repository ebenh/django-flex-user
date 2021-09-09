from django.contrib.auth import get_user_model, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status, generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from drf_multiple_model.views import ObjectMultipleModelAPIView

from social_django.models import UserSocialAuth

from .models.otp import EmailDevice, PhoneDevice, VerificationTimeout
from .validators import FlexUserUnicodeUsernameValidator

from .serializers import FlexUserSerializer, AuthenticationSerializer, UserSocialAuthSerializer, \
    EmailDeviceSerializer, PhoneDeviceSerializer

UserModel = get_user_model()


# Create your views here.

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    return Response(status=status.HTTP_204_NO_CONTENT)


class FlexUsers(generics.GenericAPIView):
    serializer_class = FlexUserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user, backend='django_flex_user.backends.FlexUserModelBackend')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlexUser(generics.GenericAPIView):
    serializer_class = FlexUserSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # note eben: the interface below is for debugging purposes only
    # def put(self, request):
    #     return self.patch(request)


class OAuthProviders(generics.GenericAPIView):
    serializer_class = UserSocialAuthSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSocialAuth.objects.filter(user_id=self.request.user)

    def get(self, request):
        user_social_auths = self.get_queryset()
        serializer = self.get_serializer(user_social_auths, many=True)
        return Response(serializer.data)


class Sessions(generics.GenericAPIView):
    serializer_class = AuthenticationSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


# class OTPDevices(generics.GenericAPIView):
#     serializer_class = EmailDeviceSerializer
#     authentication_classes = [SessionAuthentication]
#     permission_classes = [AllowAny]
#     queryset = UserModel.objects.all()
#
#     def get_object(self):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         filter_kwargs = {}
#
#         username = self.request.query_params.get('username', None)
#         if username is not None:
#             filter_kwargs.update({'username': UserModel.normalize_username(username)})
#
#         email = self.request.query_params.get('email', None)
#         if email is not None:
#             filter_kwargs.update({'email': UserModel.objects.normalize_email(email)})
#
#         phone = self.request.query_params.get('phone', None)
#         if phone is not None:
#             filter_kwargs.update({'phone': phone})
#
#         if not username and not email and not phone:
#             raise Http404  # todo: this should be 400 bad request
#
#         obj = get_object_or_404(queryset, **filter_kwargs)
#
#         if not obj:
#             raise Http404
#
#         # May raise a permission denied
#         self.check_object_permissions(self.request, obj)
#
#         return obj
#
#     @method_decorator(csrf_protect)
#     def get(self, request):
#         user = self.get_object()
#         email_devices = EmailDevice.objects.devices_for_user(user)
#         serializer = self.get_serializer(email_devices, many=True)
#         return Response({'email': serializer.data}, status.HTTP_200_OK)


# class OTPDevice(generics.GenericAPIView):
#     serializer_class = OTPSerializer
#     authentication_classes = [SessionAuthentication]
#     permission_classes = [AllowAny]
#
#     @staticmethod
#     def get(request, pk):
#         pk = unquote(pk)
#         device = Device.from_persistent_id(pk)
#
#         if not device:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         if not device.is_interactive():
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             device.generate_challenge()
#         except ConnectionRefusedError:
#             # return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             pass
#
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def post(self, request, pk):
#         pk = unquote(pk)
#         device = Device.from_persistent_id(pk)
#
#         if not device:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             verify_is_allowed, extra = device.verify_is_allowed()
#             if verify_is_allowed:
#                 if device.verify_token(serializer.validated_data['pin']):
#                     jwt = RefreshToken.for_user(device.user)
#                     return Response({'refresh': str(jwt), 'access': str(jwt.access_token)}, status=status.HTTP_200_OK)
#                 else:
#                     return Response(status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 if 'reason' in extra and extra['reason'] == VerifyNotAllowed.N_FAILED_ATTEMPTS:
#                     return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
#                 if 'error_message' in extra:
#                     raise Response(extra['error_message'], status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def my_filter(queryset, request, *args, **kwargs):
    my_filter.username_validator = FlexUserUnicodeUsernameValidator()

    q = request.query_params.get('search')

    if not q:
        return queryset.model.objects.none()

    try:
        my_filter.username_validator(q)
    except ValidationError:
        if '@' in q:
            s = {'user__email': UserModel.objects.normalize_email(q)}
        else:
            s = {'user__phone': q}
    else:
        s = {'user__username': UserModel.normalize_username(q)}

    return queryset.filter(**s)


class OTPDevices(ObjectMultipleModelAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    querylist = (
        {'queryset': EmailDevice.objects.all(), 'serializer_class': EmailDeviceSerializer, 'filter_fn': my_filter},
        {'queryset': PhoneDevice.objects.all(), 'serializer_class': PhoneDeviceSerializer, 'filter_fn': my_filter},
    )


class OTPEmailDevice(generics.GenericAPIView):
    queryset = EmailDevice.objects.all()
    serializer_class = EmailDeviceSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, pk):
        email_device = self.get_object()
        email_device.generate_challenge()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        email_device = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                if email_device.verify_challenge(serializer.validated_data['challenge']):
                    jwt = RefreshToken.for_user(email_device.user)
                    return Response({'refresh': str(jwt), 'access': str(jwt.access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except VerificationTimeout:
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPPhoneDevice(OTPEmailDevice):
    queryset = PhoneDevice.objects.all()
    serializer_class = PhoneDeviceSerializer
