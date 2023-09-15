from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from portal_user.models import PortalUser


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        user = None

        try:
            requested_email = request.data["email"]
            user = PortalUser.objects.get(email=requested_email)
            if not user.is_active:
                return JsonResponse(
                    {
                        "message": "account_not_active"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (request.data["password"] == user.otp) or (
                user.check_password(request.data["password"])
            ):
                requested_consumer_or_staff_id = request.data["consumer_or_staff_id"]

                if (requested_consumer_or_staff_id and not user.is_staff) or (requested_consumer_or_staff_id and user.is_staff and user.consumer_or_staff_id != requested_consumer_or_staff_id):
                    return JsonResponse({'message': "staff_account_not_found"}, status=status.HTTP_400_BAD_REQUEST)
                elif not requested_consumer_or_staff_id and user.is_staff:
                    return JsonResponse({'message': "consumer_account_not_found"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    pass

                user.otp = ""
                user.failed_login_attempt = 0
                user.is_active = True
                user.last_login = timezone.now()
                user.save()

                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            else:
                user.failed_login_attempt += 1
                user.save()
                return JsonResponse(
                    {"message": "email_password_invalid"}, status=status.HTTP_400_BAD_REQUEST
                )
        except PortalUser.DoesNotExist:
            user = None
            return JsonResponse(
                {
                    "message": "account_not_found"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
