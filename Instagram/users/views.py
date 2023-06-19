from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_mail, send_phone_number, check_email_or_phone
from .serializers import SignUpSerializer, ChangeUserInformation, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogoutSerializer,ForgetPasswordSerializer,ResetPasswordSerializer
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.decorators import permission_classes
# Create your views here.

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request,*args,**kwargs):
        user=self.request.user
        code=self.request.data.get('code')

        self.check_verify(user,code)
        return Response(
            data={
                'success': True,
                'auth_status': user.auth_status,
                'access': user.token()['access'],
                'refresh': user.token()['refresh']
            }
        )

    @staticmethod
    def check_verify(user,code):
        verifies=user.verify_codes.filter(expiration_time__gte=datetime.now(),
                                          code=code,
                                          is_confirmed=False)
        if not verifies.exists():
            data={
                'success':False,
                'message':"Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status==NEW:
            user.auth_status=CODE_VERIFIED
            user.save()
        return True

class GetNewVerification(APIView):
    def get(self,request,*args,**kwargs):
        user=self.request.user
        self.check_verification(user)
        if user.auth_type==VIA_EMAIL:
            code=user.create_verify_code(VIA_EMAIL)
            send_mail(user.email,code)
        elif user.auth_type==VIA_PHONE:
            code=user.create_verify_code(VIA_PHONE)
            send_mail(user.phone_number,code)
            # telfon raqam bo'lmagan uchun email jo'natib turamiz
            #send_phone_number(user.phone_number,code)
        else:
            data={
                'success': False,
                'message': "Email yoki telefon nomer xato"
            }
            raise  ValidationError(data)
        return Response(
            {
                'success': True,
                'message': "Tasdiqlash kodingiz qaytadan jo'natildi"
            }
        )

    @staticmethod
    def check_verification(user):
        verifies=user.verify_codes.filter(expiration_time__gte=datetime.now(),
                                          is_confirmed=False)
        if verifies.exists():
            data={
                'success': False,
                'message':"Kodningiz hali ishlatish uchun yaroqli. Biroz kuting!!!"
            }
            raise ValidationError(data)
        return True
class ChangeUserInformationUpdateAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class =ChangeUserInformation
    http_method_names = ['patch','put']

    def get_object(self):
       return  self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationUpdateAPIView,self).update(request,*args,**kwargs)
        data={
            'success': True,
            'message': "User updated successfully",
            'auth_status': self.request.user.auth_status
        }
        return Response(data,status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationUpdateAPIView,self).partial_update(request,*args,**kwargs)
        data={
            'success': True,
            'message': "User updated successfully",
            'auth_status': self.request.user.auth_status
        }
        return Response(data,status=200)

class ChangeUserPhotoUpdateAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class = ChangeUserPhotoSerializer
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserPhotoUpdateAPIView,self).partial_update(request,*args,**kwargs)
        data = {
            'success': True,
            'message': "User's photo updated successfully",
        }
        return Response(data, status=200)

class ChangeUserPhotoAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def put(self,request,*args,**kwargs):
        serializer=ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user=request.user
            serializer.update(user,serializer.validated_data)
            return Response(
                {
                    'success': True,
                    'message': "User's photo updated successfully",
                },
                status=200
            )
        return Response(
            serializer.errors,status=400
        )
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class =LoginRefreshSerializer

class LogOutAPIView(APIView):
    serializer_class=LogoutSerializer
    permission_classes = [IsAuthenticated,]

    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token=self.request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            data={
                'success':True,
                'message':"You are loggout out"
            }
            return Response(data,status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny,]
    serializer_class=ForgetPasswordSerializer

    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone=serializer.validated_data.get('email_or_phone')
        user=serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone)=='phone':
            code=user.create_verify_code(VIA_PHONE)
            send_mail(email_or_phone,code)
            # bizda telefon raqam bo'lmagan uchun emailda jo'natib turamiz
            #send_phone_number(email_or_phone,code)
        elif check_email_or_phone(email_or_phone)=='email':
            code=user.create_verify_code(VIA_EMAIL)
            send_mail(email_or_phone,code)
        else:
            return Response(status=500)
        return Response(
            {
                'success':True,
                'message':"Tasdiqlash kodningiz muvaffaqiyatli yuborildi",
                'access':user.token()['access'],
                'refresh':user.token()['refresh'],
                'auth_status':user.auth_status
            },
            status=200
        )


class ResetPasswordUpdateAPIView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        respone=super(ResetPasswordUpdateAPIView,self).update(request,*args,**kwargs)
        try:
            user=User.objects.get(id=respone.data.get('id'))
        except ObjectDoesNotExist as err:
            raise  NotFound(detail="Foydalanuvchi topilmadi")
        return Response({
            'success':True,
            'message':"Parol muvaqiyatli o'zgartirildi",
            'access': user.token()['access'],
            'refresh': user.token()['refresh'],
        },
        status=201
        )