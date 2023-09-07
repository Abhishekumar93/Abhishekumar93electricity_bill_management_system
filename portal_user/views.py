import json
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.response import Response
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .token import account_activation_token

# Import Models Here
from .models import PortalUser

# Import Serializers Here
from .serializers import PortalUserSerializer, PortalUserBasicDataSerializer, PortalUserUpdateSerializer, PortalUserDetailSerializer

# Create your views here.


class PortalUserCreate(APIView):
    queryset = PortalUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PortalUserSerializer

    def post(self, request):
        request_type = request.GET.get("type")
        try:
            if request.data['email'] is not None:
                user = get_object_or_404(
                    PortalUser.objects.all(), email=request.data['email'])

                if request_type and request_type == "add":
                    return Response({'message': 'User is already registered with us'}, status=status.HTTP_403_FORBIDDEN)
                elif user:
                    return Response({'message': 'You are already registered with us'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'message': 'Email is required!'}, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user.send_welcome_email()
            user.send_account_activation_mail()
            response_data = {
                'message': 'Account created successfully!. An activation email has been sent to your email id. Please activate your account before login.'}
            if request_type and request_type == "add":
                response_data = {
                    'message': f"User {user.first_name} added successfully!.  An activation email is sent to the user's email id."}
                response_data["data"] = json.dumps(serializer.data)

            return Response(response_data, status=status.HTTP_201_CREATED)


class PortalUserLogin(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortalUserBasicDataSerializer

    def get(self, request):
        queryset = PortalUser.objects.get(pk=request.user.id)
        serializer = PortalUserBasicDataSerializer(queryset)
        return Response(serializer.data)


class PortalCustomerList(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticated)
    serializer_class = PortalUserUpdateSerializer
    queryset = PortalUser.objects.all().order_by("-date_joined")
    filterset_fields = ["is_active", "user_role"]


class PortalUserUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = PortalUser.objects.all()
    serializer_class = PortalUserUpdateSerializer


class PortalUserDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PortalUserDetailSerializer
    queryset = PortalUser.objects.all()


class PortalUserOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user = PortalUser.objects.get(email=request.data["email"])
            user.generate_otp()
            return Response({'message': "otp_sent"}, status=status.HTTP_200_OK)
        except PortalUser.DoesNotExist:
            return Response({'message': "user_not_found"}, status=status.HTTP_404_NOT_FOUND)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = PortalUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, PortalUser.DoesNotExist):
        user = None
    except Exception as e:
        return HttpResponse("Something went wrong!")

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return JsonResponse({"message": "activation_successful"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "activation_failed"}, status=status.HTTP_200_OK)
