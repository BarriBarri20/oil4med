from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, role=None):
        """
        Creates and saves a User with the given email, password, name, and role.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name, role):
        """
        Creates and saves a superuser with the given email, password, first_name, last_name, and role.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('mill manager', 'Mill Manager'),
        ('administrator', 'Administrator'),
        ('visitor', 'Visitor'),
    )
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class ReceivedFeedback(models.Model):
    appreciation = models.IntegerField()
    feedback = models.CharField(max_length=255)
    cause_choices = (
        ('VS', 'Olive Selling'),
        ('OS', 'Oil Selling'),
        ('ES', 'Extraction Service'),
        ('PS', 'Packaging Service'),
        ('SS', 'Storage Service'),
        ('AS', 'Analysis Service'),
        ('VB', 'Olive Buying'),
        ('OB', 'Oil Buying'),
    )
    feedback_cause = models.CharField(max_length=3, choices=cause_choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedbacks')


class Farmer(User):
    country = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Farmers"


class Consumer(User):
    country = models.CharField(max_length=20, blank=True, null=True)


class MillManager(User):
    pass


class OliveGrove(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_owner = models.BooleanField(default=False)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    trees_age = models.IntegerField()
    area = models.FloatField()
    area_unit = 'Hectare'
    density = models.FloatField()
    olives_variety = models.CharField(max_length=20)
    soil_type_choices = (
        ('SN', 'Sandy'),
        ('SL', 'Silty'),
        ('C', 'Clay'),
        ('L', 'Loamy'),
    )
    soil_type = models.CharField(max_length=3, choices=soil_type_choices)
    fertilizers_used = models.CharField(max_length=255)
    pesticide_sprays = models.BooleanField(default=False)
    cropping_choices = (
        ('R', 'Rainfed'),
        ('I', 'Irrigated'),
    )
    cropping_system = models.CharField(max_length=2, choices=cropping_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=2, choices=practice_choices)
    grove_picture = models.ImageField(upload_to='images/')
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class OilMill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    fax = models.CharField(max_length=20)
    website = models.URLField(max_length=255)
    creation_date = models.DateField()
    milling_capacity = models.FloatField()
    transformation_capacity_unit_choices = (
        ('l', 'Liters'),
        ('kg', 'Kilograms'),
        ('t', 'Tonnes'),
    )
    transformation_capacity_unit = models.CharField(max_length=3, choices=transformation_capacity_unit_choices)
    chains_number = models.IntegerField()
    has_lab = models.BooleanField(default=False)
    has_pack_unit = models.BooleanField(default=False)
    storage_capacity = models.FloatField()
    storage_capacity_unit = models.CharField(max_length=2, choices=transformation_capacity_unit_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=20, choices=practice_choices)
    quality_certificate = models.CharField(max_length=255)
    agreement_date = models.DateField()
    mill_manager = models.OneToOneField(MillManager, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Harvest(models.Model):
    harvest_date = models.DateField()
    harvest_method_choices = (
        ('Mn', 'Manual'),
        ('Mc', 'Mechanical'),
        ('B', 'Both'),
    )
    harvest_method = models.CharField(max_length=3, choices=harvest_method_choices)
    initial_quantity = models.FloatField()
    remaining_quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    olives_color = (
        ('G', 'Green'),
        ('P', 'Purple'),
        ('B', 'Black'),
    )
    maturity_index = models.CharField(max_length=2, choices=olives_color)
    characterization_choices = (
        ('Mono', 'Monovarietal'),
        ('Poly', 'Polyvarietal'),
    )
    characterization = models.CharField(max_length=5, choices=characterization_choices)
    classification_by_maturity = models.BooleanField(default=False)
    containers_choices = (
        ('Bg', 'Fabric bags'),
        ('Pb', 'Plastic bags'),
        ('Px', 'Plastic boxes'),
        ('O', 'Other'),
    )
    containers = models.CharField(max_length=3, choices=containers_choices)
    harvest_picture = models.ImageField(upload_to='images/')
    grove = models.ForeignKey(OliveGrove, on_delete=models.CASCADE, related_name='harvests')
    creation_cause = models.CharField(max_length=15, default='Harvesting')
    harvest_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.remaining_quantity = self.initial_quantity
        if not self.harvest_code:
            formatted_date = self.harvest_date.strftime('%Y%m%d')
            harvest_id = str(self.id).zfill(6)
            self.harvest_code = f"{harvest_id}-{formatted_date}-{self.grove.name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.harvest_code


class OliveNeed(models.Model):
    quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    price_min = models.DecimalField(max_digits=12, decimal_places=3)
    price_max = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    region = models.CharField(max_length=50)
    country = models.CharField(max_length=20)
    need_date = models.DateField()
    olives_variety = models.CharField(max_length=50)
    cropping_choices = (
        ('R', 'Rainfed'),
        ('I', 'Irrigated'),
    )
    cropping_system = models.CharField(max_length=2, choices=cropping_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=2, choices=practice_choices)
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='olive_needs')
    status_choices = (
        ('P', 'Pending'),
        ('R', 'Responded'),
    )
    need_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()
    need_code = models.CharField(max_length=255, unique=True, blank=True)

    def clean(self):
        if not self.oil_mill:
            raise ValidationError("An olive need must have a creator (OilMill).")

    def save(self, *args, **kwargs):
        formatted_date = self.need_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.need_code:
            self.need_code = f"olive need-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.need_code


class OliveSaleOffer(models.Model):
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE)
    initial_quantity_for_sell = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    available_quantity_for_sell = models.FloatField()
    offer_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    availability_date = models.DateField()
    transport_choices = (
        ('D', 'Delivered'),
        ('R', 'Recovered locally'),
    )
    transportation = models.CharField(max_length=2, choices=transport_choices)
    creation_date = models.DateField()
    update_date = models.DateField()
    status_choices = (
        ('A', 'Available'),
        ('Cl', 'Closed'),
        ('Ca', 'Cancelled'),
    )
    offer_status = models.CharField(max_length=3, choices=status_choices, default='A')
    offer_code = models.CharField(max_length=255, unique=True, blank=True)
    creation_cause_need = models.BooleanField(default=False)
    olive_need = models.ForeignKey(OliveNeed, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='olive_sale_offers')

    def save(self, *args, **kwargs):
        if not self.id and self.offer_status == 'A':
            self.available_quantity_for_sell = self.initial_quantity_for_sell
        formatted_date = self.creation_date.strftime('%Y%m%d')
        offer_id = str(self.id).zfill(6)
        if not self.offer_code:
            self.offer_code = f"olive selling-{formatted_date}-{offer_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_code


class OlivePurchaseRequest(models.Model):
    olive_sale_offer = models.ForeignKey(OliveSaleOffer, on_delete=models.CASCADE,
                                         related_name='olive_purchase_requests')
    mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='olive_purchase_requests')
    requested_quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    requested_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    request_date = models.DateField()
    buyer_appreciation = models.IntegerField()
    buyer_feedback = models.CharField(max_length=255)
    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('B', 'Bought'),
    )
    request_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()
    request_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        formatted_date = self.request_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.request_code:
            self.request_code = f"olive purchase-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_code


class PurchasedOlive(models.Model):
    olive_quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    purchase_date = models.DateField()
    olives_variety = models.CharField(max_length=50)
    olives_color = (
        ('G', 'Green'),
        ('P', 'Purple'),
        ('B', 'Black'),
    )
    maturity_index = models.CharField(max_length=2, choices=olives_color)
    characterization_choices = (
        ('Mono', 'Monovarietal'),
        ('Poly', 'Polyvarietal'),
    )
    characterization = models.CharField(max_length=5, choices=characterization_choices)
    classification_by_maturity = models.BooleanField(default=False)
    cropping_choices = (
        ('R', 'Rainfed'),
        ('I', 'Irrigated'),
    )
    cropping_system = models.CharField(max_length=2, choices=cropping_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=2, choices=practice_choices)
    mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='purchased_olives')
    olive_purchase_request = models.OneToOneField(OlivePurchaseRequest, on_delete=models.CASCADE, blank=True, null=True)


class Machine(models.Model):
    machine_reference = models.CharField(max_length=100)
    brand = models.CharField(max_length=20)
    constructor = models.CharField(max_length=50)
    purchase_date = models.DateField()
    capacity = models.IntegerField()
    type_choices = (
        ('T', 'Traditional'),
        ('S', 'Super press'),
        ('Co', 'Continuous one phase'),
        ('Ct', 'Continuous two phases'),
    )
    type = models.CharField(max_length=3, choices=type_choices)
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='machines')


class ServiceRequest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='service_requests')
    considered_quantity = models.FloatField()
    requested_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    request_date = models.DateField()
    status_choices = (
        ('P', 'Pending'),
        ('R', 'Responded'),
        ('Cf', 'Confirmed'),
        ('Ca', 'Cancelled'),
    )
    request_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()

    request_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        formatted_date = self.request_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.request_code:
            # Determine the type of request based on the class name
            request_type = self.__class__.__name__.lower()
            self.request_code = f"{request_type}-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_code


class ExtractionRequest(ServiceRequest):
    harvest = models.OneToOneField(Harvest, on_delete=models.CASCADE, related_name='extraction_requests')
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    method = models.CharField(max_length=20)


class ServiceOffer(models.Model):
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='service_offers')
    offered_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    offer_date = models.DateField()
    negotiable_price = models.BooleanField(default=False)
    availability = models.DateField(null=True, blank=True)
    service_type_choices = (
        ('E', 'Extraction'),
        ('P', 'Packaging'),
        ('S', 'Storage'),
        ('A', 'Analysis'),
        ('N', 'Not defined'),
    )
    service_type = models.CharField(max_length=3, choices=service_type_choices, default='N')
    offer_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        formatted_date = self.offer_date.strftime('%Y%m%d')
        offer_id = str(self.id).zfill(6)
        service_type = self.__class__.__name__.lower()
        if not self.offer_code:
            self.offer_code = f"{service_type}-{formatted_date}-{offer_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_code


class ExtractionOffer(ServiceOffer):
    extraction_request = models.ForeignKey(ExtractionRequest, on_delete=models.CASCADE,
                                           related_name='extraction_offers')
    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('E', 'Extracted'),
    )
    offer_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()


class ExtractionOperation(models.Model):
    used_machines = models.ManyToManyField(Machine, blank=True) # to verify!
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='extractions')
    external_oil_mill = models.CharField(max_length=50, blank=True, null=True)
    harvest = models.OneToOneField(Harvest, on_delete=models.CASCADE, null=True, blank=True)
    purchased_olives = models.ManyToManyField(PurchasedOlive, blank=True)
    extraction_offer = models.OneToOneField(ExtractionOffer, on_delete=models.CASCADE, null=True, blank=True)
    reception_date = models.DateField()
    start_date = models.DateField()
    finish_date = models.DateField()
    olives_quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=10, default='Tonnes')
    water_per_100kg = models.IntegerField()
    mixing_duration = models.IntegerField()
    time_unit = models.CharField(max_length=10, default='Minutes')
    press_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    filtration_considered = models.BooleanField(default=False)
    separate_mixing_by_variety = models.BooleanField(default=False)
    method = models.CharField(max_length=20)
    produced_quantity = models.FloatField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    produced_quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)

    def clean(self):
        if self.harvest and self.purchased_olives:
            raise ValidationError("An extraction operation cannot derive from both a harvest and a purchased olive.")


class OilProduct(models.Model):
    extraction_operation = models.OneToOneField(ExtractionOperation, on_delete=models.CASCADE, null=True, blank=True)
    production_date = models.DateField()
    creation_cause_choices = (
        ('E', 'Extraction'),
        ('St', 'Storage'),
        ('P', 'Packaging'),
        ('B', 'Buying'),
    )
    creation_cause = models.CharField(max_length=3, choices=creation_cause_choices)
    produced_quantity = models.FloatField()
    remaining_quantity = models.FloatField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    quality_control_performed = models.BooleanField(default=False)
    olive_oil_type_choices = (
        ('EVOO', 'Extra Virgin olive oil'),
        ('VOO', 'Virgin olive oil'),
        ('L', 'Lampante olive oil'),
        ('R', 'Refined olive oil'),
        ('P', 'Olive pomace oil'),
        ('N', 'Not defined'),

    )
    oil_quality = models.CharField(max_length=5, choices=olive_oil_type_choices, default='N')
    owner_category_choices = (
        ('F', 'Farmer'),
        ('M', 'Oil mill'),
        ('C', 'Consumer'),
    )
    owner_category = models.CharField(max_length=2, choices=owner_category_choices)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='oil_products')
    is_packaged = models.BooleanField(default=False)
    is_stored = models.BooleanField(default=False)
    mother_product = models.ForeignKey(
        'self',
        related_name='child_products',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    oil_product_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        cre_date = self.production_date.strftime('%Y%m%d')
        oil_id = str(self.id).zfill(6)
        cause = self.creation_cause
        if not self.oil_product_code:
            self.oil_product_code = f"{cause}-{cre_date}-{oil_id}"
        super().save(*args, **kwargs)

    @property
    def last_analysis(self):
        return self.analysis.last()

    def get_owner_instance(self):
        if self.owner_category == 'F':
            # if the farmer has extracted his oil via an extraction request/offer
            if self.extraction_operation and self.extraction_operation.extraction_offer:
                return self.extraction_operation.extraction_offer.extraction_request.farmer
            # if the farmer has extracted his oil directly without request/offer
            elif self.extraction_operation and self.extraction_operation.harvest:
                return self.extraction_operation.harvest.grove.farmer
            else:
                return None  # no owner instance for the farmer
        elif self.owner_category == 'M':
            if self.extraction_operation and self.extraction_operation.purchased_olives.exists():
                return self.extraction_operation.purchased_olives.latest('purchase_date').mill
            else:
                return None  # no owner instance for the oil mill
        else:
            return None  # owner category is unknown or invalid

    def __str__(self):
        return self.oil_product_code


class StorageRequest(ServiceRequest):
    oil_product = models.ForeignKey(OilProduct, on_delete=models.CASCADE, related_name='storage_requests')
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    storage_condition = models.CharField(max_length=100, null=True, blank=True)


class StorageOffer(ServiceOffer):
    storage_request = models.ForeignKey(StorageRequest, on_delete=models.CASCADE,
                                        related_name='storage_offers')

    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('S', 'Stored'),
    )
    offer_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()


class StorageArea(models.Model):
    local_type = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    container_type = models.CharField(max_length=100)
    container_number = models.IntegerField()
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True, related_name='storage_areas')
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, null=True, blank=True, related_name='storage_areas')

    def clean(self):
        if self.oil_mill and self.farmer:
            raise ValidationError("A StorageArea cannot have both an OilMill and a Farmer as owners.")
        if not self.oil_mill and not self.farmer:
            raise ValidationError("A StorageArea must have an owner (OilMill or Farmer).")


class OilStorage(models.Model):
    storage_offer = models.OneToOneField(StorageOffer, on_delete=models.CASCADE, null=True, blank=True)
    oil_product = models.OneToOneField(OilProduct, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='storage')
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True, related_name='storages')
    storage_date = models.DateField()
    stored_quantity = models.FloatField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    storage_area = models.ForeignKey(StorageArea, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='stored_oils')


class PackagingRequest(ServiceRequest):
    oil_product = models.ForeignKey(OilProduct, on_delete=models.CASCADE, related_name='packaging_requests')
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    type_of_packaging_choices = (
        ('DGbt', 'Dark Glass Bottles'),
        ('TGbt', 'Transparent Glass Bottles'),
        ('Pbt', 'Plastic Bottles'),
        ('T', 'Tin Cans'),
        ('Bx', 'Bag In Box'),
        ('C', 'Ceramic jars'),
    )
    type_of_packaging = models.CharField(max_length=4, choices=type_of_packaging_choices, null=True, blank=True)
    packaging_volume = models.CharField(max_length=50, null=True, blank=True)


class PackagingOffer(ServiceOffer):
    packaging_request = models.ForeignKey(PackagingRequest, on_delete=models.CASCADE,
                                          related_name='packaging_offers')

    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('Pk', 'Packaged'),
    )
    offer_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()


class Packaging(models.Model):
    packaging_reference = models.CharField(max_length=255, unique=True)
    packaging_date = models.DateField()
    packaged_quantity = models.IntegerField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    packaged_quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    type_of_packaging_choices = (
        ('DGbt', 'Dark Glass Bottles'),
        ('TGbt', 'Transparent Glass Bottles'),
        ('Pbt', 'Plastic Bottles'),
        ('T', 'Tin Cans'),
        ('Bx', 'Bag In Box'),
        ('C', 'Ceramic jars'),
    )
    type_of_packaging = models.CharField(max_length=4, choices=type_of_packaging_choices)
    packaging_volume = models.CharField(max_length=50)
    packaging_factory_name = models.CharField(max_length=50)
    factory_address = models.CharField(max_length=255)
    factory_certificate = models.CharField(max_length=255)
    packaging_offer = models.OneToOneField(PackagingOffer, on_delete=models.CASCADE, null=True, blank=True)
    oil_product = models.OneToOneField(OilProduct, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='packaging')
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True, related_name='packagings')


class AnalysisRequest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='analysis_requests')
    oil_product = models.ForeignKey(OilProduct, on_delete=models.CASCADE, related_name='analysis_requests')
    analysis_choices = (
        ('F', 'Fatty Acid'),
        ('P', 'Peroxide value'),
        ('U', 'UV absorbance'),
        ('A', 'Acidity'),
    )
    analysis_type_1 = models.CharField(max_length=2, choices=analysis_choices, null=True, blank=True)
    analysis_type_2 = models.CharField(max_length=2, choices=analysis_choices, null=True, blank=True)
    analysis_type_3 = models.CharField(max_length=2, choices=analysis_choices, null=True, blank=True)
    analysis_type_4 = models.CharField(max_length=2, choices=analysis_choices, null=True, blank=True)
    request_date = models.DateField()
    status_choices = (
        ('P', 'Pending'),
        ('R', 'Responded'),
        ('Cf', 'Confirmed'),
        ('Ca', 'Cancelled'),
    )
    request_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()
    request_code = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        formatted_date = self.request_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.request_code:
            self.request_code = f"analysisrequest-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_code


class AnalysisOffer(ServiceOffer):
    analysis_request = models.ForeignKey(AnalysisRequest, on_delete=models.CASCADE,
                                         related_name='analysis_offers')

    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('An', 'Analysed'),
    )
    offer_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()


class OilAnalysis(models.Model):
    analysis_reference = models.CharField(max_length=255, unique=True)
    analysis_date = models.DateField()
    lab_name = models.CharField(max_length=50)
    lab_address = models.CharField(max_length=255)
    lab_agreement = models.CharField(max_length=255)
    lab_agreement_date = models.DateField()
    olive_oil_type_choices = (
        ('EVOO', 'Extra Virgin olive oil'),
        ('VOO', 'Virgin olive oil'),
        ('L', 'Lampante olive oil'),
        ('R', 'Refined olive oil'),
        ('P', 'Olive pomace oil'),
        ('N', 'Not defined'),

    )
    oil_quality = models.CharField(max_length=5, choices=olive_oil_type_choices, default='N')
    fatty_acid = models.CharField(max_length=20, null=True, blank=True)
    acidity = models.CharField(max_length=20, null=True, blank=True)
    peroxide_value = models.CharField(max_length=20, null=True, blank=True)
    UV_absorbance = models.CharField(max_length=20, null=True, blank=True)
    analysis_file = models.FileField(upload_to='analysis_files/', null=True, blank=True)
    analysis_offer = models.OneToOneField(AnalysisOffer, on_delete=models.CASCADE, null=True, blank=True)
    oil_product = models.ForeignKey(OilProduct, on_delete=models.CASCADE, related_name='analysis')
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True, related_name='analyses')


class ExtractionServiceProposal(models.Model):
    capacity = models.IntegerField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('t', 'Tonnes'),
    )
    capacity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    type_choices = (
        ('T', 'Traditional'),
        ('S', 'Super press'),
        ('Co', 'Continuous one phase'),
        ('Ct', 'Continuous two phases'),
    )
    machine_type = models.CharField(max_length=3, choices=type_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=2, choices=practice_choices)
    price = models.DecimalField(max_digits=12, decimal_places=3)
    negotiable_price = models.BooleanField(default=False)
    availability = models.DateField()
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='extraction_proposals')


class PackagingServiceProposal(models.Model):
    packaging_factory_name = models.CharField(max_length=50)
    factory_address = models.CharField(max_length=255)
    factory_certificate = models.CharField(max_length=255)
    type_of_packaging_choices = (
        ('DGbt', 'Dark Glass Bottles'),
        ('TGbt', 'Transparent Glass Bottles'),
        ('Pbt', 'Plastic Bottles'),
        ('T', 'Tin Cans'),
        ('Bx', 'Bag In Box'),
        ('C', 'Ceramic jars'),
    )
    type_of_packaging = models.CharField(max_length=4, choices=type_of_packaging_choices)
    packaging_volume = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    negotiable_price = models.BooleanField(default=False)
    availability = models.DateField()
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='packaging_proposals')


class AnalysisServiceProposal(models.Model):
    lab_name = models.CharField(max_length=50)
    lab_address = models.CharField(max_length=255)
    lab_agreement = models.CharField(max_length=255)
    fatty_acid = models.BooleanField(default=False)
    sensory_description = models.BooleanField(default=False)
    peroxide_value = models.BooleanField(default=False)
    UV_absorbance = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='analysis_proposals')


class StorageServiceProposal(models.Model):
    storage_type = models.CharField(max_length=100)
    capacity = models.IntegerField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    capacity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    negotiable_price = models.BooleanField(default=False)
    availability = models.DateField()
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, related_name='storage_proposals')


class OilNeed(models.Model):
    quantity = models.FloatField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    olive_oil_type_choices = (
        ('EVOO', 'Extra Virgin olive oil'),
        ('VOO', 'Virgin olive oil'),
        ('L', 'Lampante olive oil'),
        ('R', 'Refined olive oil'),
        ('P', 'Olive pomace oil'),

    )
    oil_quality = models.CharField(max_length=5, choices=olive_oil_type_choices)
    flavour = models.CharField(max_length=50)
    price_min = models.DecimalField(max_digits=12, decimal_places=3)
    price_max = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    region = models.CharField(max_length=50)
    country = models.CharField(max_length=20)
    need_date = models.DateField()
    production_year = models.DateField()
    packaged = models.BooleanField(default=True)
    cropping_choices = (
        ('R', 'Rainfed'),
        ('I', 'Irrigated'),
    )
    cropping_system = models.CharField(max_length=2, choices=cropping_choices)
    practice_choices = (
        ('C', 'Conventional'),
        ('O', 'Organic'),
    )
    practice = models.CharField(max_length=2, choices=practice_choices)
    buyer_category_choices = (
        ('C', 'Consumer'),
        ('M', 'Oil mill'),
    )
    buyer_category = models.CharField(max_length=2, choices=buyer_category_choices)
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_needs')
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_needs')

    status_choices = (
        ('P', 'Pending'),
        ('R', 'Responded'),
    )
    need_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()
    need_code = models.CharField(max_length=255, unique=True, blank=True)

    def clean(self):
        if self.oil_mill and self.consumer:
            raise ValidationError(
                "An oil need cannot be created by an oil mill and a consumer at the same time.")
        if not self.oil_mill and not self.consumer:
            raise ValidationError("An oil need must have a creator (OilMill or Consumer).")

    def save(self, *args, **kwargs):
        formatted_date = self.need_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.need_code:
            self.need_code = f"oil need-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.need_code


class OilSaleOffer(models.Model):
    oil_product = models.ForeignKey(OilProduct, on_delete=models.CASCADE, related_name='sale_offers')
    initial_quantity_for_sell = models.FloatField()
    available_quantity_for_sell = models.FloatField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    offered_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    transport_choices = (
        ('D', 'Delivered'),
        ('R', 'Recovered locally'),
    )
    transportation = models.CharField(max_length=2, choices=transport_choices)
    creation_date = models.DateField()
    update_date = models.DateField()
    type_of_packaging_choices = (
        ('DGbt', 'Dark Glass Bottles'),
        ('TGbt', 'Transparent Glass Bottles'),
        ('Pbt', 'Plastic Bottles'),
        ('T', 'Tin Cans'),
        ('Bx', 'Bag In Box'),
        ('C', 'Ceramic jars'),
    )
    type_of_packaging = models.CharField(max_length=4, choices=type_of_packaging_choices)
    packaging_volume = models.CharField(max_length=50)
    status_choices = (
        ('A', 'Available'),
        ('Cl', 'Closed'),
        ('Ca', 'Cancelled'),
    )
    offer_status = models.CharField(max_length=3, choices=status_choices)
    offer_code = models.CharField(max_length=255, unique=True, blank=True)
    analysis_file = models.FileField(upload_to='analysis_files/', null=True, blank=True)
    creation_cause_need = models.BooleanField(default=False)
    oil_need = models.ForeignKey(OilNeed, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_sale_offers')
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_sale_offers')
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, null=True, blank=True, related_name='oil_sale_offers')
    mother_offer = models.ForeignKey(
        'self',
        related_name='child_offers',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def clean(self):
        if self.oil_mill and self.farmer:
            raise ValidationError("A sale offer cannot be created by an oil mill and a farmer at the same time.")
        if not self.oil_mill and not self.farmer:
            raise ValidationError("A sale offer must have a creator (OilMill or Farmer).")

    def save(self, *args, **kwargs):
        formatted_date = self.creation_date.strftime('%Y%m%d')
        offer_id = str(self.id).zfill(6)
        if not self.offer_code:
            self.offer_code = f"oil selling-{formatted_date}-{offer_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_code


class OilPurchaseRequest(models.Model):
    oil_sale_offer = models.ForeignKey(OilSaleOffer, on_delete=models.CASCADE)
    requested_quantity = models.IntegerField()
    quantity_unit_choices = (
        ('kg', 'Kilograms'),
        ('l', 'Liters'),
    )
    quantity_unit = models.CharField(max_length=3, choices=quantity_unit_choices)
    requested_price = models.DecimalField(max_digits=12, decimal_places=3)
    price_unit_choices = (
        ('$', 'Dollars $'),
        ('€', 'Euros €'),
        ('TND', 'Tunisian Dinar'),
    )
    price_unit = models.CharField(max_length=3, choices=price_unit_choices, default='€')
    request_date = models.DateField()
    buyer_category_choices = (
        ('C', 'Consumer'),
        ('M', 'Oil mill'),
    )
    buyer_category = models.CharField(max_length=2, choices=buyer_category_choices)
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_purchase_requests')
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='oil_purchase_requests')
    buyer_appreciation = models.IntegerField()
    buyer_feedback = models.CharField(max_length=255)
    status_choices = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('B', 'Bought'),
    )
    request_status = models.CharField(max_length=2, choices=status_choices)
    status_update_date = models.DateField()
    request_code = models.CharField(max_length=255, unique=True, blank=True)

    def clean(self):
        if self.oil_mill and self.consumer:
            raise ValidationError(
                "A purchase request cannot be created by an oil mill and a consumer at the same time.")
        if not self.oil_mill and not self.consumer:
            raise ValidationError("A purchase request must have a creator (OilMill or Consumer).")

    def save(self, *args, **kwargs):
        formatted_date = self.request_date.strftime('%Y%m%d')
        request_id = str(self.id).zfill(6)
        if not self.request_code:
            self.request_code = f"oil purchase-{formatted_date}-{request_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_code


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    oil_mill = models.ForeignKey(OilMill, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class IoTSensor(models.Model):
    sensor_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20)
    constructor = models.CharField(max_length=50)
    deployment_date = models.DateField()
    storage_area = models.ForeignKey(StorageArea, on_delete=models.CASCADE, related_name='sensors')


class SensorMeasurement(models.Model):
    parameter = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=5, decimal_places=3)
    date = models.DateField()
    sensor = models.ForeignKey(IoTSensor, on_delete=models.CASCADE, related_name='measurements')
