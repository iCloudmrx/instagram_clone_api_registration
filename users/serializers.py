from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_or_phone,send_mail,send_phone_number,check_user_type
from .models import User,UserConfirmation,VIA_EMAIL,VIA_PHONE,CODE_VERIFIED,NEW,DONE,PHOTO_STEP
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q

class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self,*args,**kwargs):
        self.fields['email_phone_number'] = serializers.CharField(required=False)
        super(SignUpSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model=User
        fields=(
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs={
            'auth_type': {
                'read_only': True,
                'required': False
            },
            'auth_status': {
                'read_only': True,
                'required': False
            },
        }
    def create(self, validated_data):
        user=super(SignUpSerializer,self).create(validated_data)
        if user.auth_type==VIA_EMAIL:
            code=user.create_verify_code(VIA_EMAIL)
            send_mail(user.email,code)
        elif user.auth_type==VIA_PHONE:
            code=user.create_verify_code(VIA_PHONE)
            # consoleda kodni ko'rish uchun ishlatyapmiz
            send_mail(user.phone_number, code)
            # sms uchun api  sotib olgandan keyin foydalanib bo'ladi
            #send_phone_number(user.phone_number,code)
        user.save()
        return user



    def validate(self, attrs):
        super(SignUpSerializer,self).validate(attrs)
        attrs=self.auth_validate(attrs)
        return attrs

    @staticmethod
    def auth_validate(attrs):
        user_input=str(attrs.get('email_phone_number')).lower()
        input_type=check_email_or_phone(user_input)
        if input_type=='email':
            attrs={
                'email':user_input,
                'auth_type':VIA_EMAIL
            }
        elif input_type=='phone':
            attrs={
                'phone_number':user_input,
                'auth_type': VIA_PHONE
            }

        else:
            attrs={
                'success':False,
                'message':'Siz email yoki telefon nomer kiritishingiz kerak'
            }
            raise  ValidationError(attrs)
        return attrs

    def validate_email_phone_number(self, value):
        value=value.lower()
        if value and User.objects.filter(email=value).exists():
            data={
                'success': False,
                'message': "Bu email orqali allaqachon ro'yxatdan o'tgan"
            }
            raise  ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': "Bu telefon nomer orqali allaqachon ro'yxatdan o'tgan"
            }
            raise ValidationError(data)
        # to do

        return value

    def to_representation(self, instance):
        data=super(SignUpSerializer,self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserInformation(serializers.Serializer):
    first_name=serializers.CharField(write_only=True,required=True)
    last_name=serializers.CharField(write_only=True,required=True)
    username=serializers.CharField(write_only=True,required=True)
    password=serializers.CharField(write_only=True,required=True)
    confirm_password=serializers.CharField(write_only=True,required=True)

    def validate(self, attrs):
        password=attrs.get('password',None)
        confirm_password=attrs.get('confirm_password',None)
        if password!=confirm_password:
            data={
                'success': False,
                'message': "Parol bir xil emas qaytadan kiriting"
            }
            raise  ValidationError(data)
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return attrs

    def validate_username(self,username):
        if len(username)<5 or len(username)>30:
            data={
                'success':False,
                'message': "Username must be between 5 and 30 characters long"
            }
            raise  ValidationError(data)
        if username.isdigit():
            data = {
                'success': False,
                'message': "This username is entirely numeric"
            }
            raise ValidationError(data)
        if User.objects.filter(username=username).exists():
            data = {
                'success': False,
                'message': "This username has been already registered"
            }
            raise ValidationError(data)

        return username

    def validate_first_name(self,first_name):
        if len(first_name) < 2 or len(first_name) > 30:
            data = {
                'success': False,
                'message': "First name must be between 5 and 30 characters long"
            }
            raise ValidationError(data)
        if not first_name.isalpha():
            data = {
                'success': False,
                'message': "Ismningiz ichida raqam bor boshqatdan kiriting!!!"
            }
            raise ValidationError(data)

        return first_name

    def validate_last_name(self,last_name):
        if len(last_name) < 2 or len(last_name) > 30:
            data = {
                'success': False,
                'message': "Last name must be between 5 and 30 characters long"
            }
            raise ValidationError(data)
        if not last_name.isalpha():
            data = {
                'success': False,
                'message': "Familiyaningiz ichida raqam bor boshqatdan kiriting!!!"
            }
            raise ValidationError(data)

        return last_name
    def update(self, instance, validated_data):
        instance.first_name=validated_data.get('first_name',instance.first_name)
        instance.last_name=validated_data.get('last_name',instance.last_name)
        instance.password=validated_data.get('password',instance.password)
        instance.username=validated_data.get('username',instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status==CODE_VERIFIED:
            instance.auth_status=DONE
        instance.save()
        return instance

class ChangeUserPhotoSerializer(serializers.Serializer):
    photo=serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=[
        'jpg','jpeg','png','heic','heif'
    ])])

    def update(self, instance, validated_data):
        photo=validated_data.get('photo')
        if photo:
            instance.photo=photo
            instance.auth_status=PHOTO_STEP
            instance.save()
        return instance
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self,*args,**kwargs):
        super(LoginSerializer,self).__init__(*args,**kwargs)
        self.fields['userinput']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(required=False,
                                                      read_only=True)
    def auth_validate(self,attrs):
        user_input=attrs.get('userinput')
        if check_user_type(user_input)=='username':
            username=user_input
        elif check_user_type(user_input)=='email':
            user=self.get_user(email__iexact=user_input)
            username=user.username
        elif check_user_type(user_input)=='phone':
            user=self.get_user(phone_number=user_input)
            username=user.username
        else:
            data={
                'success':False,
                'message':"Siz email, username yoki telefon raqamningizni jo'natishingiz kerak"
            }
            raise ValidationError(data)
        authentication_kwargs={
            self.username_field:username,
            'password':attrs['password']
        }
        # user status tekshirilish kerak
        current_user=User.objects.filter(username__iexact=username).first()
        if current_user.auth_status in [NEW,CODE_VERIFIED,None]:
            data = {
                'success': False,
                'message': "Siz ro'yxatdan to'liq o'tmagansiz"
            }
            raise ValidationError(data)
        user=authenticate(**authentication_kwargs)
        if user is None:
            data={
                'success':False,
                'message':"Kechirasiz parol yoki username xato. Iltimos tekshirib yana urinib ko'ring"
            }
            raise ValidationError(data)
        self.user=user
    def validate(self, attrs):
        self.auth_validate(attrs)
        if self.user.auth_status not in [DONE,PHOTO_STEP]:
            raise PermissionDenied("Siz login qila olmaysiz ruxsat yo'q sizga")
        attrs=self.user.token()
        attrs['auth_status']=self.user.auth_status
        return attrs

    def get_user(self,**kwargs):
        user=User.objects.filter(**kwargs)
        if not user:
            data = {
                'success': False,
                'message': "Bu foydalanuvchi topilmadi"
            }
            raise ValidationError(data)
        return user.first()


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data=super().validate(attrs)
        access_token_instance=AccessToken(data['access'])
        user_id=access_token_instance['user_id']
        user=get_object_or_404(User,id=user_id)
        update_last_login(None,user)
        return data
