from django.urls import path

from .views import PortalUserCreate, activate, PortalUserLogin, PortalCustomerList, PortalUserUpdate

app_name = "portal_user"

urlpatterns = [
    path('create/user/', PortalUserCreate.as_view(),
         name="create"),
    path('login/', PortalUserLogin.as_view(), name="login"),
    path('list/user/', PortalCustomerList.as_view(), name="user-list"),
    path('user/update/<int:pk>/', PortalUserUpdate.as_view(), name="user-update"),
    path(
        'activate/<slug:uidb64>/<slug:token>/', activate, name="account-activate"),
]
