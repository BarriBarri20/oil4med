from bdb import GENERATOR_AND_COROUTINE_FLAGS
from django.contrib.auth.hashers import make_password
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from dbmanage.serializers import *
from dbmanage.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from dbmanage.permissions import *
from django.db.models import Q
from django.views import View
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

@api_view(['POST'])
def register(request):
    role = request.data.get('role')
    
    if role == 'farmer':
        serializer = FarmerSerializer(data=request.data)
    elif role == 'consumer':
        serializer = ConsumerSerializer(data=request.data)
    elif role == 'oil mill':
        serializer = OilMillSerializer(data=request.data)
    else:
        return Response({'detail': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        hashed_password = make_password(request.data.get('password'))
        serializer.validated_data['password'] = hashed_password
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)

    if user is not None:
        print("user not none")
        refresh = RefreshToken.for_user(user)
        response = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response)
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    token = RefreshToken(refresh_token)
    response = {
        'access': str(token.access_token),
    }
    return Response(response)

class UserViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FarmerList(generics.ListCreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer


class FarmerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer


class ConsumerList(generics.ListCreateAPIView):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer


class ConsumerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer


class OilMillList(generics.ListCreateAPIView):
    queryset = OilMill.objects.all()
    serializer_class = OilMillSerializer


class OilMillDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OilMill.objects.all()
    serializer_class = OilMillSerializer

#Mill manager details:
class MillManagerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MillManager.objects.all()
    serializer_class = MillManagerSerializer


# Shorter version of code and more accurate
class OliveGroveListRetrieveViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = OliveGroveSerializer
    lookup_field = 'name'

class OliveGroveModelViewSet(ModelViewSet):
    serializer_class = OliveGroveSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

# # get olive groves list, filter by practice (conventional or organic), by address
# class OliveGroveList(generics.ListAPIView):
#     queryset = OliveGrove.objects.all()
#     serializer_class = OliveGroveSerializer

#     def get_queryset(self):
#         queryset = OliveGrove.objects.all()

#         # Get query parameters from the request
#         practice = self.request.query_params.get('practice')
#         address = self.request.query_params.get('address')
#         if practice:
#             queryset = queryset.filter(practice=practice)
#         if address:
#             # Filter by address, allowing partial matches (icontains)
#             queryset = queryset.filter(Q(address__icontains=address))

#         return queryset


# # retrieve an olive grove by its ID
# class OliveGroveDetailAPIView(RetrieveAPIView):
#     queryset = OliveGrove.objects.all()
#     serializer_class = OliveGroveSerializer


# # retrieve an olive grove by its name
# class OliveGroveByNameAPIView(RetrieveAPIView):
#     queryset = OliveGrove.objects.all()
#     serializer_class = OliveGroveSerializer
#     lookup_field = 'name'  # Specify the field to use for lookup

#     def get_object(self):
#         name = self.kwargs.get('name')
#         return self.queryset.filter(name__iexact=name).first()


# # create an olive grove, only the farmer has permission to do
# class OliveGroveCreateView(APIView):
#     permission_classes = [IsAuthenticated, IsFarmer]

#     def post(self, request):
#         serializer = OliveGroveSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(farmer=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # update an olive grove, only farmers that are owners are allowed to update it
# class OliveGroveUpdateView(APIView):
#     permission_classes = [IsAuthenticated, IsFarmer, IsOwnerOfOliveGrove]

#     def put(self, request, pk):
#         try:
#             olive_grove = OliveGrove.objects.get(pk=pk, farmer=request.user)
#         except OliveGrove.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         serializer = OliveGroveSerializer(olive_grove, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # delete an olive grove, only farmers that are owners are allowed to delete it
# class OliveGroveDeleteView(APIView):
#     permission_classes = [IsAuthenticated, IsFarmer]

#     def delete(self, request, pk):
#         try:
#             olive_grove = OliveGrove.objects.get(pk=pk, farmer=request.user)
#         except OliveGrove.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         olive_grove.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# display the list of harvests, only the farmer that owns the harvest has permission
# filter harvest list by quantity, maturity and date, sort the list by quantity +/-, date (oldest to newest)
class HarvestListAPIView(ListAPIView):
    serializer_class = HarvestSerializer
    permission_classes = [IsAuthenticated, IsFarmer, IsOwnerOfHarvest]  # Use the custom permission class

    def get_queryset(self):
        # Filter the queryset to include only harvests owned by the current user (farmer)
        queryset = Harvest.objects.filter(grove__farmer=self.request.user)
        # filter by quantity
        quantity_min = self.request.query_params.get('quantity_min')
        quantity_max = self.request.query_params.get('quantity_max')
        if quantity_min and quantity_max:
            queryset = queryset.filter(quantity__range=[quantity_min, quantity_max])
        # filter by maturity
        maturity = self.request.query_params.get('maturity')
        if maturity:
            queryset = queryset.filter(maturity_index=maturity)
        # filter by date
        harvest_date = self.request.query_params.get('harvest_date')
        year = self.request.query_params.get('year')
        if harvest_date:
            queryset = queryset.filter(harvest_date=harvest_date)
        if year:
            queryset = queryset.filter(harvest_date__year=year)
        # sorting
        sort_by = self.request.query_params.get('sort_by')
        if sort_by == 'quantity_asc':
            queryset = queryset.order_by('quantity')
        elif sort_by == 'quantity_desc':
            queryset = queryset.order_by('-quantity')
        elif sort_by == 'harvest_date':
            queryset = queryset.order_by('harvest_date')
        return queryset


class HarvestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Harvest.objects.all()
    serializer_class = HarvestSerializer
    permission_classes = [IsAuthenticated, IsFarmer, IsOwnerOfHarvest]


class HarvestCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFarmer]

    def post(self, request):
        serializer = HarvestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(grove__farmer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HarvestUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsFarmer, IsOwnerOfHarvest]

    def put(self, request, pk):
        try:
            harvest = Harvest.objects.get(pk=pk, grove__farmer=request.user)
        except Harvest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HarvestSerializer(harvest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# delete a harvest, only farmers that are owners are allowed to delete it
class HarvestDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsFarmer, IsOwnerOfHarvest]

    def delete(self, request, pk):
        try:
            harvest = Harvest.objects.get(pk=pk, grove__farmer=request.user)
        except Harvest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        harvest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# create an olive sale offer by the farmer
class OliveSaleOfferCreateAPIView(generics.CreateAPIView):
    serializer_class = OliveSaleOfferSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def perform_create(self, serializer):
        # Get the sale offer data from the request
        harvest_id = self.request.data.get('harvest')

        try:
            harvest = Harvest.objects.get(pk=harvest_id, grove__farmer=self.request.user)
        except Harvest.DoesNotExist:
            return Response(
                {"detail": "Harvest with the provided ID does not exist or does not belong to you."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Additional data for the sale offer
        creation_date = timezone.now().date()
        update_date = timezone.now().date()
        offer_status = 'A'  # Set the offer status to 'Available'.

        # Save the sale offer with the associated harvest and additional data
        serializer.save(
            harvest=harvest,
            creation_date=creation_date,
            update_date=update_date,
            offer_status=offer_status
        )


# update an olive sale offer by the farmer
class OliveSaleOfferUpdateAPIView(APIView):
    queryset = OliveSaleOffer.objects.all()
    serializer_class = OliveSaleOfferSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def put(self, request, pk):
        try:
            offer = OliveSaleOffer.objects.get(pk=pk)
        except OliveSaleOffer.DoesNotExist:
            return Response({'error': 'Olive Sale Offer does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the request user is the owner of the offer's harvest
        if offer.harvest.grove.farmer != request.user:
            return Response({'error': 'You do not have permission to update this offer'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(offer, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        # Automatically set the update_date to the current time
        serializer.save(update_date=timezone.now().date())


# display the list of olive sale offers, every one can check the list
# filter offers list by quantity, price, transportation and olives_variety, sort the list by quantity +/-, price +/-
class OliveSaleOfferListAPIView(ListAPIView):
    serializer_class = OliveSaleOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OliveSaleOffer.objects.all()
        # Get the query parameters from the request
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        quantity_min = self.request.query_params.get('quantity_min')
        quantity_max = self.request.query_params.get('quantity_max')
        transport_option = self.request.query_params.get('transportation')
        olives_variety = self.request.query_params.get('olives_variety')
        sort_by = self.request.query_params.get('sort_by')
        # Filtering by price
        if price_min and price_max:
            queryset = queryset.filter(price__range=[price_min, price_max])
        # Filtering by quantity
        if quantity_min and quantity_max:
            queryset = queryset.filter(quantity__range=[quantity_min, quantity_max])
        # Filtering by transportation option
        if transport_option:
            queryset = queryset.filter(transportation=transport_option)
        # Filtering by olives variety
        if olives_variety:
            queryset = queryset.filter(harvest__olives_variety=olives_variety)
        # Sorting
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'quantity_asc':
            queryset = queryset.order_by('quantity')
        elif sort_by == 'quantity_desc':
            queryset = queryset.order_by('-quantity')
        return queryset


# check the corresponding harvest details for each olive sale offer through its ID
class OliveSaleOfferDetails(APIView):
    def get(self, request, pk):
        try:
            olive_sale_offer = OliveSaleOffer.objects.get(pk=pk)
            harvest = olive_sale_offer.harvest
            harvest_serializer = HarvestSerializer(harvest)
            return Response(harvest_serializer.data, status=status.HTTP_200_OK)
        except OliveSaleOffer.DoesNotExist:
            return Response({'error': 'Olive Sale Offer does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Harvest.DoesNotExist:
            return Response({'error': 'Harvest details not found'}, status=status.HTTP_404_NOT_FOUND)


# check the farmer profile for each harvest sale offer through its ID
class OliveSaleOfferFarmerProfile(APIView):
    def get(self, request, pk):
        try:
            olive_sale_offer = OliveSaleOffer.objects.get(pk=pk)
            farmer = olive_sale_offer.harvest.grove.farmer
            farmer_serializer = FarmerSerializer(farmer)
            return Response(farmer_serializer.data, status=status.HTTP_200_OK)
        except OliveSaleOffer.DoesNotExist:
            return Response({'error': 'Olive Sale Offer does not exist'}, status=status.HTTP_404_NOT_FOUND)


# create an olive purchase request, by the oil mill, as a reply to the olive sale offer published by the farmer
class OlivePurchaseRequestCreateView(generics.CreateAPIView):
    queryset = OlivePurchaseRequest.objects.all()
    serializer_class = OlivePurchaseRequestSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        # Get the sale offer ID from the request data
        sale_offer_id = self.request.data.get('olive_sale_offer')

        try:
            sale_offer = OliveSaleOffer.objects.get(pk=sale_offer_id)
        except OliveSaleOffer.DoesNotExist:
            return Response(
                {"detail": "OliveSaleOffer with the provided ID does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(
            olive_sale_offer=sale_offer,
            request_date=timezone.now().date(),
            request_status='P',  # Set the request status to 'Pending'.
            mill=self.request.user,  # Assuming the mill is the currently authenticated user.
        )


class OlivePurchaseRequestList(generics.ListCreateAPIView):
    queryset = OlivePurchaseRequest.objects.all()
    serializer_class = OlivePurchaseRequestSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]


class OlivePurchaseRequestDetail(View):
    def get(self, request, pk):
        olive_purchase_request = get_object_or_404(OlivePurchaseRequest, pk=pk)
        return render(request, 'olive_purchase_request_detail.html', {'olive_purchase_request': olive_purchase_request})


# when the oil mill send the OlivePurchaseRequest, the farmer can approve the request (request_status set to Approved)
# the oil mill will receive a notification that the farmer has approved the purchase request,
class ApproveOlivePurchaseRequest(APIView):
    permission_classes = [IsAuthenticated, IsFarmer]

    def post(self, request, pk):
        try:
            purchase_request = OlivePurchaseRequest.objects.get(pk=pk)
        except OlivePurchaseRequest.DoesNotExist:
            return Response({'error': 'Olive Purchase Request does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the request user is the owner of the grove associated with the request
        if purchase_request.olive_sale_offer.harvest.grove.farmer != request.user:
            return Response({'error': 'You do not have permission to approve this request'},
                            status=status.HTTP_403_FORBIDDEN)

        # Update the request_status to "Approved"
        purchase_request.request_status = 'A'
        purchase_request.status_update_date = timezone.now().date()
        purchase_request.save()

        # Trigger a notification to the oil mill
        oil_mill = purchase_request.mill
        notification_message = f'Your olive purchase request for {purchase_request.requested_quantity} {purchase_request.quantity_unit} has been approved by the farmer.'
        Notification.objects.create(
            oil_mill=oil_mill,  # Assuming 'user' is the field for the oil mill's user
            message=notification_message,
        )

        return Response({'message': 'Olive Purchase Request approved'}, status=status.HTTP_200_OK)


# the oil mill after receiving the notification of farmer approval, will confirm the purchase
class ConfirmOlivePurchase(APIView):
    permission_classes = [IsAuthenticated, IsOilMill]

    def post(self, request, pk):
        try:
            purchase_request = OlivePurchaseRequest.objects.get(pk=pk)
        except OlivePurchaseRequest.DoesNotExist:
            return Response({'error': 'Olive Purchase Request does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the request user is the owner of the olive mill associated with the request
        if purchase_request.mill != request.user:
            return Response({'error': 'You do not have permission to confirm this purchase'},
                            status=status.HTTP_403_FORBIDDEN)

        # Update the request_status to "Bought"
        purchase_request.request_status = 'B'
        purchase_request.status_update_date = timezone.now().date()
        purchase_request.save()

        if purchase_request.requested_quantity == purchase_request.olive_sale_offer.available_quantity_for_sell:
            purchase_request.olive_sale_offer.offer_status = 'Cl'
        else:
            remaining_quantity = purchase_request.olive_sale_offer.available_quantity_for_sell - purchase_request.requested_quantity
            purchase_request.olive_sale_offer.available_quantity_for_sell = remaining_quantity

        purchase_request.olive_sale_offer.save()

        purchased_olive = PurchasedOlive(
            olive_quantity=purchase_request.requested_quantity,
            quantity_unit=purchase_request.quantity_unit,
            purchase_date=timezone.now().date(),
            olives_variety=purchase_request.olive_sale_offer.harvest.olives_variety,
            maturity_index=purchase_request.olive_sale_offer.harvest.maturity_index,
            characterization=purchase_request.olive_sale_offer.harvest.characterization,
            classification_by_maturity=purchase_request.olive_sale_offer.harvest.classification_by_maturity,
            cropping_system=purchase_request.olive_sale_offer.harvest.cropping_system,
            practice=purchase_request.olive_sale_offer.harvest.practice,
            mill=purchase_request.mill,
            olive_purchase_request=purchase_request
        )
        purchased_olive.save()

        # Create a notification for the farmer
        user = purchase_request.olive_sale_offer.harvest.grove.farmer
        if purchase_request.requested_quantity == purchase_request.olive_sale_offer.available_quantity_for_sell:
            notification_message = f'The purchase of {purchase_request.olive_sale_offer.available_quantity_for_sell} {purchase_request.quantity_unit} of olives has been confirmed and your sale offer is closed.'
        else:
            notification_message = f'The purchase of {purchase_request.requested_quantity} {purchase_request.quantity_unit} of olives has been confirmed and your sale offer is remaining available.'

        Notification.objects.create(
            user=user,  # Assuming 'user' is the field for the oil mill's user
            message=notification_message,
        )

        return Response({'message': 'Olive Purchase confirmed'}, status=status.HTTP_200_OK)


class PurchasedOliveCreateAPIView(generics.CreateAPIView):
    queryset = PurchasedOlive.objects.all()
    serializer_class = PurchasedOliveSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# update purchased olive
class PurchasedOliveUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsOilMill]

    def put(self, request, pk):
        try:
            purchased_olive = PurchasedOlive.objects.get(pk=pk, mill=request.user)
        except PurchasedOlive.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PurchasedOliveSerializer(purchased_olive, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# retrieve all purchased olives, only the owner is authorized to check the list
class PurchasedOliveListView(ListAPIView):
    serializer_class = PurchasedOliveSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def get_queryset(self):
        # Filter the queryset to include only purchased olives belonging to the current oil mill
        return PurchasedOlive.objects.filter(mill=self.request.user)


class PurchasedOliveRetrieveAPIView(RetrieveAPIView):
    serializer_class = PurchasedOliveSerializer
    queryset = PurchasedOlive.objects.all()
    permission_classes = [IsAuthenticated, IsOilMill, IsOwnerOfPurchasedOlive]


class MachineList(generics.ListCreateAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsOwnerOfMachine]


class MachineDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsOwnerOfMachine]


# create an extraction request
class ExtractionRequestCreateAPIView(generics.CreateAPIView):
    queryset = ExtractionRequest.objects.all()
    serializer_class = ExtractionRequestSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


# create an extraction offer
class ExtractionOfferCreateAPIView(generics.CreateAPIView):
    queryset = ExtractionOffer.objects.all()
    serializer_class = ExtractionOfferSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create an extraction operation
class ExtractionOperationCreateAPIView(generics.CreateAPIView):
    queryset = ExtractionOperation.objects.all()
    serializer_class = ExtractionOperationSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


class ExtractionOperationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExtractionOperation.objects.all()
    serializer_class = ExtractionOperationSerializer


# create a storage area
class StorageAreaCreateAPIView(generics.CreateAPIView):
    queryset = StorageArea.objects.all()
    serializer_class = StorageAreaSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


class IoTSensorDetailView(RetrieveAPIView):
    queryset = IoTSensor.objects.all()
    serializer_class = IoTSensorSerializer
    lookup_field = 'pk'


class SensorMeasurementListView(ListAPIView):
    queryset = SensorMeasurement.objects.all()
    serializer_class = SensorMeasurementSerializer


# create a packaging operation
class PackagingCreateAPIView(generics.CreateAPIView):
    queryset = Packaging.objects.all()
    serializer_class = PackagingSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


# create an oil product
class OilProductCreateAPIView(generics.CreateAPIView):
    queryset = OilProduct.objects.all()
    serializer_class = OilProductSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


class OilProductDetailView(RetrieveAPIView):
    queryset = OilProduct.objects.all()
    serializer_class = OilProductSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]
    lookup_field = 'pk'


class OilAnalysisCreateView(CreateAPIView):
    queryset = OilAnalysis.objects.all()
    serializer_class = OilAnalysisSerializer


# create a service request
class ServiceRequestCreateAPIView(generics.CreateAPIView):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


# create a service offer
class ServiceOfferCreateAPIView(generics.CreateAPIView):
    queryset = ServiceOffer.objects.all()
    serializer_class = ServiceOfferSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create an extraction service proposal
class ExtractionServiceProposalCreateAPIView(generics.CreateAPIView):
    queryset = ExtractionServiceProposal.objects.all()
    serializer_class = ExtractionServiceProposalSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create a packaging service proposal
class PackagingServiceProposalCreateAPIView(generics.CreateAPIView):
    queryset = PackagingServiceProposal.objects.all()
    serializer_class = PackagingServiceProposalSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create a storage service proposal
class StorageServiceProposalCreateAPIView(generics.CreateAPIView):
    queryset = StorageServiceProposal.objects.all()
    serializer_class = StorageServiceProposalSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create an analysis service proposal
class AnalysisServiceProposalCreateAPIView(generics.CreateAPIView):
    queryset = AnalysisServiceProposal.objects.all()
    serializer_class = AnalysisServiceProposalSerializer
    permission_classes = [IsAuthenticated, IsOilMill]

    def perform_create(self, serializer):
        serializer.save()


# create an oil sale offer
class OilSaleOfferCreateAPIView(generics.CreateAPIView):
    queryset = OilSaleOffer.objects.all()
    serializer_class = OilSaleOfferSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsFarmer]

    def perform_create(self, serializer):
        serializer.save()


# create an oil purchase request
class OilPurchaseRequestCreateAPIView(generics.CreateAPIView):
    queryset = OilPurchaseRequest.objects.all()
    serializer_class = OilPurchaseRequestSerializer
    permission_classes = [IsAuthenticated, IsOilMill, IsConsumer]

    def perform_create(self, serializer):
        serializer.save()
