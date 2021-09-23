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
    OTPSerializer, EmailDeviceSerializer, PhoneDeviceSerializer

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
    serializer_class = OTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, pk):
        email_device = self.get_object()
        email_device.generate_challenge()
        email_device.send_challenge()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        email_device = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                success = email_device.verify_challenge(serializer.validated_data['challenge'])
            except VerificationTimeout:
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                if success:
                    jwt = RefreshToken.for_user(email_device.user)
                    return Response({'refresh': str(jwt), 'access': str(jwt.access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPPhoneDevice(OTPEmailDevice):
    queryset = PhoneDevice.objects.all()
    serializer_class = OTPSerializer
