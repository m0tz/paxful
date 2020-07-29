from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Platform, Transaction, Wallet
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from paxful.settings import WALLET_TRANSFER_COMMISION_RATE
from .helpers import get_current_BTC_to_USD_price
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(required=False)

    class Meta:
        model = User
        fields = ["username", "token"]

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    balance_in_usd = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Wallet
        fields = ["balance", "balance_in_usd"]
        extra_kwargs = {"user": {"read_only": True}, "url": {"lookup_field": "address"}}

    def create(self, validated_data):
        """
        Create and return a new `Wallet` instance, given the validated data.
        """
        user = self.context["request"].user
        # Limit user to 10 wallets
        if Wallet.objects.filter(user=user).count() > 9:
            raise ValidationError
        return Wallet.objects.create(user=user, balance=Decimal("1.0"))

    def get_balance_in_usd(self, obj):
        return obj.balance * Decimal(get_current_BTC_to_USD_price().replace(",", ""))


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ["origin_address", "destination_address", "code", "amount"]

    def create(self, validated_data):
        user = self.context["request"].user
        origin_address = self.validated_data["origin_address"]
        destination_address = self.validated_data["destination_address"]
        amount = self.validated_data["amount"]
        user_wallets_addresses = Wallet.objects.filter(user=user).values_list("address", flat=True)
        destination_wallet = Wallet.objects.get(address=destination_address)
        origin_wallet = Wallet.objects.filter(address=origin_address).filter(balance__gte=amount).first()

        if not origin_wallet.balance:
            raise ValidationError("Wallet does not have enough funds.")

        if destination_address in user_wallets_addresses:
            destination_wallet.balance += amount
            destination_wallet.save()
            origin_wallet.balance -= amount
            origin_wallet.save()

            return Transaction.objects.create(
                origin_address=origin_address, destination_address=destination_address, amount=amount
            )
        else:
            # Calculate Fee.
            fee = amount * WALLET_TRANSFER_COMMISION_RATE
            amount -= fee
            # Add funds to destination wallet.
            destination_wallet.balance += amount
            destination_wallet.save()
            # Substract from origin wallet.
            origin_wallet.balance -= amount
            origin_wallet.save()
            # Add fee to paxful profit.
            paxful = Platform.objects.get(name="paxful")
            paxful.profit += fee
            paxful.save()

            return Transaction.objects.create(
                origin_address=origin_address, destination_address=destination_address, amount=amount
            )
