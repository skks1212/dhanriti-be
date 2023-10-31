import requests
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from core.settings.base import AUTH_MODE, VISHNU_API_KEY, VISHNU_HOST
from utils.views.base import BaseModelViewSetPlain
from dhanriti.models import Login, User

from ..serializers import (
    AuthSerializer,
    UserDetailSerializer,
    VishnuCheckLoginSerializer,
    VishnuLoginSerializer,
)


class APILoginView(CreateAPIView):
    serializer_class = AuthSerializer if AUTH_MODE == "LOCAL" else VishnuLoginSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    @extend_schema(
        tags=("auth",),
        operation_id="api-login",
    )
    def post(self, request: Request):
        login_token = request.data.get("login_token")
        if login_token and AUTH_MODE == "VISHNU":
            try:
                user_data_request = requests.get(
                    VISHNU_HOST + "/users/token?token=" + login_token,
                    headers={"X-API-KEY": VISHNU_API_KEY},
                )
                user_data = user_data_request.json()
                print(user_data)
                user_details = user_data.get("user")
                login = Login.objects.get(
                    service_token=user_data.get("service_token"), successful=False
                )
                if not login:
                    raise ParseError("Invalid login token")
                try:
                    user = User.objects.get(email=user_details.get("email"))
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        email=user_details.get("email"),
                        username="VISHNU-DEFAULT-" + user_details.get("external_id"),
                        password="DEFAULT",
                        vishnu_id=user_details.get("external_id"),
                    )
                login.user = user
                login.successful = True
                login.save()
                return Response(
                    {"token": login.token.key, "user": UserDetailSerializer(user).data}
                )
            except requests.exceptions.ConnectionError:
                raise ParseError("Could not connect to Vishnu")
        else:
            client_url = request.data.get("client_url")
            redirect_url = request.data.get("redirect")
            if AUTH_MODE == "VISHNU":
                try:
                    service_token_request = requests.post(
                        VISHNU_HOST + "/servicetoken",
                        {
                            "success_url": (
                                client_url
                                + "/vishnu-login?success=true&token=[token]"
                                + (
                                    ("&redirect=" + redirect_url)
                                    if redirect_url
                                    else ""
                                )
                            ),
                            "failure_url": client_url + "/vishnu-login?success=false",
                        },
                        headers={"X-API-KEY": VISHNU_API_KEY},
                    )
                    json_data = service_token_request.json()
                    print(json_data)
                    service_token = json_data["token"]
                    url = json_data["url"]
                    Login.objects.create(service_token=service_token)
                    return Response({"url": url, "token": service_token})
                except requests.exceptions.ConnectionError:
                    return Response(
                        {"error": "Could not connect to Vishnu"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        """Get auth token"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class APILogoutView(DestroyAPIView):
    @extend_schema(tags=("auth",), operation_id="api-logout", responses=None)
    def delete(self, request: Request):
        """Destroy auth token"""
        if auth_token := request.auth:
            Token.objects.filter(key=auth_token).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ParseError("No auth token provided")


class APICheckLoginView(BaseModelViewSetPlain, RetrieveModelMixin):
    queryset = Login.objects.all()
    serializer_class = VishnuCheckLoginSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "service_token"
