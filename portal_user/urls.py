from django.urls import path

from .views import PortalUserCreate, activate, PortalUserLogin, PortalCustomerList, PortalUserUpdate, PortalUserDetail, PortalUserOTP

app_name = "portal_user"

urlpatterns = [
    path('create/user/', PortalUserCreate.as_view(),
         name="create"),
    path('login/', PortalUserLogin.as_view(), name="login"),
    path('otp/', PortalUserOTP.as_view(), name="otp"),
    path('list/user/', PortalCustomerList.as_view(), name="user-list"),
    path('user/update/<int:pk>/', PortalUserUpdate.as_view(), name="user-update"),
    path('user/detail/<int:pk>/', PortalUserDetail.as_view(), name="user-detail"),
    path(
        'activate/<slug:uidb64>/<slug:token>/', activate, name="account-activate"),
]
