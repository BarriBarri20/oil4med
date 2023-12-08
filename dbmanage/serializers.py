from rest_framework import serializers
from datetime import datetime, date
from django.contrib.auth import authenticate
from dbmanage.models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'password']


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = '__all__'


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'


class MillManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MillManager
        fields = '__all__'


class OliveGroveSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer()

    class Meta:
        model = OliveGrove
        fields = '__all__'

        def create(self, validated_data):
            # Set the farmer to the current user
            validated_data['farmer'] = self.context['request'].user.farmer
            return super().create(validated_data)

        def update(self, instance, validated_data):
            # Update the related farmer instance if it is provided
            if 'farmer' in validated_data:
                farmer_data = validated_data.pop('farmer')
                farmer_serializer = FarmerSerializer(instance.farmer, data=farmer_data, partial=True)
                farmer_serializer.is_valid(raise_exception=True)
                farmer_serializer.save()

            return super().update(instance, validated_data)


class OilMillSerializer(serializers.ModelSerializer):
    mill_manager = MillManagerSerializer()

    class Meta:
        model = OilMill
        fields = '__all__'

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            representation['creation_date'] = datetime.strftime(instance.creation_date, '%m/%d/%Y')
            return representation


class HarvestSerializer(serializers.ModelSerializer):
    grove = OliveGroveSerializer()

    class Meta:
        model = Harvest
        fields = '__all__'

        def validate_quantity(self, value):
            if value < 0:
                raise serializers.ValidationError("Quantity must be a positive number.")
            return value


class OliveSaleOfferSerializer(serializers.ModelSerializer):
    harvest = HarvestSerializer()

    class Meta:
        model = OliveSaleOffer
        fields = '__all__'

        def validate_quantity(self, value):
            if value < 0:
                raise serializers.ValidationError("harvest sale quantity must be a positive number.")
            return value


class OlivePurchaseRequestSerializer(serializers.ModelSerializer):
    olive_sale_offer = OliveSaleOfferSerializer()
    mill = OilMillSerializer()

    class Meta:
        model = OlivePurchaseRequest
        fields = '__all__'


class PurchasedOliveSerializer(serializers.ModelSerializer):
    olive_purchase_request = OlivePurchaseRequestSerializer()
    mill = OilMillSerializer()

    class Meta:
        model = PurchasedOlive
        fields = '__all__'


class MachineSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = Machine
        fields = '__all__'


class ExtractionRequestSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer()
    harvest = HarvestSerializer()

    class Meta:
        model = ExtractionRequest
        fields = '__all__'


class MillManagerExtractionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionRequest
        fields = [
            'considered_quantity',
            'quantity_unit',
            'requested_price',
            'price_unit',
            'method',
            'request_date',
            'farmer',
        ]


class MillManagerPackagingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackagingRequest
        fields = [
            'considered_quantity',
            'quantity_unit',
            'requested_price',
            'price_unit',
            'type_of_packaging',
            'packaging_volume',
            'request_date',
            'farmer',
        ]


class MillManagerStorageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageRequest
        fields = [
            'considered_quantity',
            'quantity_unit',
            'requested_price',
            'price_unit',
            'storage_condition',
            'request_date',
            'farmer',
        ]


class MillManagerAnalysisRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRequest
        fields = [
            'analysis_type_1',
            'analysis_type_2',
            'analysis_type_3',
            'analysis_type_4',
            'request_date',
            'farmer',
        ]


class ExtractionOfferSerializer(serializers.ModelSerializer):
    extraction_request = ExtractionRequestSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = ExtractionOffer
        fields = '__all__'


class ExtractionOperationSerializer(serializers.ModelSerializer):
    used_machines = MachineSerializer(many=True)
    oil_mill = OilMillSerializer()
    harvest = HarvestSerializer()
    purchased_olives = PurchasedOliveSerializer(many=True)
    extraction_offer = ExtractionOfferSerializer()

    class Meta:
        model = ExtractionOperation
        fields = '__all__'


class FarmerExtractionOperationOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionOperation
        fields = ['reception_date', 'finish_date', 'produced_quantity', 'produced_quantity_unit']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_mill'] = self.context['oil_mill']
        validated_data['extraction_offer'] = self.context['extraction_offer']
        validated_data['harvest'] = self.context['harvest']
        validated_data['olives_quantity'] = self.context['considered_quantity']
        validated_data['quantity_unit'] = self.context['quantity_unit']
        return super().create(validated_data)


class MillExtractionOperationOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionOperation
        fields = ['reception_date', 'start_date', 'finish_date', 'water_per_100kg', 'mixing_duration', 'time_unit',
                  'press_temperature', 'filtration_considered', 'separate_mixing_by_variety', 'method',
                  'produced_quantity', 'produced_quantity_unit']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_mill'] = self.context['oil_mill']
        validated_data['extraction_offer'] = self.context['extraction_offer']
        validated_data['harvest'] = self.context['harvest']
        validated_data['olives_quantity'] = self.context['considered_quantity']
        validated_data['quantity_unit'] = self.context['quantity_unit']
        return super().create(validated_data)


class FarmerExtractionOperationCreateSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()
    harvest = HarvestSerializer()

    class Meta:
        model = ExtractionOperation
        fields = ['oil_mill', 'external_oil_mill', 'reception_date', 'finish_date', 'olives_quantity',
                  'produced_quantity', 'produced_quantity_unit']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['harvest'] = self.context['harvest']
        return super().create(validated_data)


class SensorMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorMeasurement
        fields = '__all__'


class IoTSensorSerializer(serializers.ModelSerializer):
    measurements = SensorMeasurementSerializer(many=True)

    class Meta:
        model = IoTSensor
        fields = '__all__'


class StorageAreaSerializer(serializers.ModelSerializer):
    # sensors = IoTSensorSerializer(many=True)
    oil_mill = OilMillSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = StorageArea
        fields = '__all__'


class PackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = '__all__'


class PackagingOperationOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = ['packaging_reference', 'packaging_date', 'packaging_factory_name', 'factory_address',
                  'factory_certificate']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_mill'] = self.context['oil_mill']
        validated_data['packaging_offer'] = self.context['packaging_offer']
        validated_data['oil_product'] = self.context['oil_product']
        validated_data['packaged_quantity'] = self.context['considered_quantity']
        validated_data['quantity_unit'] = self.context['quantity_unit']
        validated_data['type_of_packaging'] = self.context['type_of_packaging']
        validated_data['packaging_volume'] = self.context['packaging_volume']
        return super().create(validated_data)


class PackagingOperationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = ['packaging_reference', 'packaging_date', 'packaged_quantity', 'type_of_packaging', 'packaging_volume',
                  'packaging_factory_name', 'factory_address',
                  'factory_certificate', 'oil_mill']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['quantity_unit'] = self.context['quantity_unit']
        return super().create(validated_data)


class OilAnalysisOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OilAnalysis
        fields = ['analysis_reference', 'analysis_date', 'lab_name', 'lab_address', 'lab_agreement',
                  'lab_agreement_date', 'oil_quality', 'fatty_acid', 'acidity', 'peroxide_value', 'UV_absorbance']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_mill'] = self.context['oil_mill']
        validated_data['analysis_offer'] = self.context['analysis_offer']
        validated_data['oil_product'] = self.context['oil_product']
        return super().create(validated_data)


class OilAnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OilAnalysis
        fields = ['analysis_reference', 'analysis_date', 'lab_name', 'lab_address', 'lab_agreement',
                  'lab_agreement_date', 'oil_quality', 'fatty_acid', 'acidity', 'peroxide_value', 'UV_absorbance',
                  'oil_mill']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_product'] = self.context['oil_product']
        return super().create(validated_data)


class OilStorageOfferCreateSerializer(serializers.ModelSerializer):
    storage_area = StorageAreaSerializer()

    class Meta:
        model = OilStorage
        fields = ['storage_date', 'stored_quantity', 'storage_area']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['oil_mill'] = self.context['oil_mill']
        validated_data['quantity_unit'] = self.context['quantity_unit']
        validated_data['storage_offer'] = self.context['storage_offer']
        validated_data['oil_product'] = self.context['oil_product']
        return super().create(validated_data)


class OilStorageCreateSerializer(serializers.ModelSerializer):
    storage_area = StorageAreaSerializer()

    class Meta:
        model = OilStorage
        fields = ['oil_mill', 'storage_date', 'stored_quantity', 'storage_area']

    def create(self, validated_data):
        # Pre-fill fields
        validated_data['quantity_unit'] = self.context['quantity_unit']
        return super().create(validated_data)


class OilProductSerializer(serializers.ModelSerializer):
    extraction_operation = ExtractionOperationSerializer()
    storage_area = StorageAreaSerializer()
    packaging = PackagingSerializer()

    class Meta:
        model = OilProduct
        fields = '__all__'


class OilAnalysisSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()

    class Meta:
        model = OilAnalysis
        fields = '__all__'


class ServiceRequestSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = ServiceRequest
        fields = '__all__'


class PackagingRequestSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = PackagingRequest
        fields = '__all__'


class StorageRequestSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = StorageRequest
        fields = '__all__'


class AnalysisRequestSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = AnalysisRequest
        fields = '__all__'


class ServiceOfferSerializer(serializers.ModelSerializer):
    service_request = ServiceRequestSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = ServiceOffer
        fields = '__all__'


class PackagingOfferSerializer(serializers.ModelSerializer):
    packaging_request = PackagingRequestSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = PackagingOffer
        fields = '__all__'


class StorageOfferSerializer(serializers.ModelSerializer):
    storage_request = StorageRequestSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = StorageOffer
        fields = '__all__'


class AnalysisOfferSerializer(serializers.ModelSerializer):
    analysis_request = AnalysisRequestSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = AnalysisOffer
        fields = '__all__'


class ExtractionServiceProposalSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = ExtractionServiceProposal
        fields = '__all__'


class PackagingServiceProposalSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = PackagingServiceProposal
        fields = '__all__'


class AnalysisServiceProposalSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = AnalysisServiceProposal
        fields = '__all__'


class StorageServiceProposalSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = StorageServiceProposal
        fields = '__all__'


class OilSaleOfferSerializer(serializers.ModelSerializer):
    oil_product = OilProductSerializer()
    oil_mill = OilMillSerializer()
    farmer = FarmerSerializer()

    class Meta:
        model = OilSaleOffer
        fields = '__all__'


class OilPurchaseRequestSerializer(serializers.ModelSerializer):
    oil_sale_offer = OilSaleOfferSerializer()
    consumer = ConsumerSerializer()
    oil_mill = OilMillSerializer()

    class Meta:
        model = OilPurchaseRequest
        fields = '__all__'


class OliveNeedSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()

    class Meta:
        model = OliveNeed
        fields = '__all__'


class OilNeedSerializer(serializers.ModelSerializer):
    oil_mill = OilMillSerializer()
    consumer = ConsumerSerializer()

    class Meta:
        model = OilNeed
        fields = '__all__'


class ReceivedFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ReceivedFeedback
        fields = '__all__'


class FarmerGoodsSerializer(serializers.Serializer):
    good_id = serializers.IntegerField()
    good_code = serializers.CharField()
    date = serializers.DateField()
    initial_quantity = serializers.FloatField()
    remaining_quantity = serializers.FloatField()
    quantity_unit = serializers.CharField()
    type = serializers.CharField()
    creation_cause = serializers.CharField()
