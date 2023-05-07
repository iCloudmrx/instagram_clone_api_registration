from django.urls import path

from .views import CreateUserView,VerifyAPIView,GetNewVerification,\
    ChangeUserInformationUpdateAPIView,ChangeUserPhotoUpdateAPIView,\
    ChangeUserPhotoAPIView,LoginView,LoginRefreshView

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('login/refresh/',LoginRefreshView.as_view()),
    path('signup/',CreateUserView.as_view()),
    path('verify/',VerifyAPIView.as_view()),
    path('new-verify/',GetNewVerification.as_view()),
    path('change-user/',ChangeUserInformationUpdateAPIView.as_view()),
    path('change-user-photo1/',ChangeUserPhotoUpdateAPIView.as_view()),
    path('change-user-photo2/',ChangeUserPhotoAPIView.as_view()),
]