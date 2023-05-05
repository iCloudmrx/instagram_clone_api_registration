from shared.utility import check_email_or_phone,send_mail
from .models import User,UserConfirmation,VIA_EMAIL,VIA_PHONE,CODE_VERIFIED,NEW,DONE,PHOTO_STEP
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
        print(user)
        if user.auth_type==VIA_EMAIL:
            code=user.create_verify_code(VIA_EMAIL)
            print(code)
            send_mail(user.email,code)
        elif user.auth_type==VIA_PHONE:
            code=user.create_verify_code(VIA_PHONE)
            print(code)
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
        print(value)
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