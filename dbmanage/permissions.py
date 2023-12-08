from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a farmer
        return request.user.role == 'farmer'


class IsConsumer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a consumer
        return request.user.role == 'consumer'


class IsMillManager(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an oil mill
        return request.user.role == 'mill manager'

class IsOilMill(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an oil mill
        return request.user.role == 'mill manager'

class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a administrator
        return request.user.role == 'administrator'


class IsVisitor(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a visitor
        return request.user.role == 'visitor'


class IsOwnerOfOliveGrove(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the olive grove
        return obj.farmer == request.user


class IsOwnerOfHarvest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the olive grove
        return obj.grove.farmer == request.user


class IsOwnerOfPurchasedOlive(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the PurchasedOlive object
        return obj.mill.mill_manager == request.user


class IsOwnerOfMachine(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # check if the request user is the owner of the Machine
        return obj.oil_mill.mill_manager == request.user


class IsOwnerOfStorageArea(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the StorageArea function of his role, farmer or mill_manager
        if request.user.role == 'farmer':
            return obj.farmer == request.user
        elif request.user.role == 'mill manager':
            return obj.oil_mill.mill_manager == request.user
        else:
            return False


class IsOwnerOfOilProduct(permissions.BasePermission):
    def has_permission(self, request, view, obj):
        oil_product = request.data.get('oil_product')
        owner_instance = obj.get_owner_instance()
        if request.user.role == 'farmer':
            return (
                    owner_instance == request.user
            )

        elif request.user.role == 'mill manager':
            return (
                owner_instance.mill_manager == request.user
            )
        else:
            return False
