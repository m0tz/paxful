from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserSerializer, TransactionSerializer, WalletSerializer, StaticticsSerializer
from .models import Transaction, Wallet, Statictics
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().filter(id=self.request.user.pk)
        return queryset


class WalletViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "address"

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Transaction.objects.all().order_by("-date_joined")
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


class StaticticsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Statictics.objects.all().order_by("-date_joined")
    serializer_class = StaticticsSerializer
    permission_classes = (IsAuthenticated,)


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {"message": "Hello world."}
        return Response(content)
