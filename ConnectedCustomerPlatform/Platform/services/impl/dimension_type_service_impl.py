import logging
import uuid
import threading
from datetime import datetime
import pytz
from django.db import transaction, IntegrityError
from dataclasses import asdict

from DatabaseApp.models import Applications, Customers, DimensionTypeCustomerApplicationMapping, DimensionType, DimensionCustomerApplicationMapping
from Platform.services.interface.dimension_type_service_interface import IDimensionTypeService
from Platform.dao.impl.dimension_type_dao_impl import DimensionTypeDaoImpl
from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from Platform.constant.default_descriptions import DefaultDimensionTypeDescription
from Platform.serializers import DimensionTypeModelSerializer, DimensionTypeCAMModelSerializer
from Platform.dao.impl.dimension_type_cam_dao_impl import DimensionTypeCAMDaoImpl

logger = logging.getLogger(__name__)

indian_tz = pytz.timezone('Asia/Kolkata')
# Function to format time in Indian format (DD-MM-YYYY HH:MM:SS)
def format_indian_time(timestamp):
    return timestamp.astimezone(indian_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class DimensionTypeServiceImpl(IDimensionTypeService):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DimensionTypeServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):  # Ensures __init__ is called only once
            super().__init__(**kwargs)
            print("Inside DimensionTypeViewSet")
            self.dimension_type_dao = DimensionTypeDaoImpl()
            self.dimension_type_cam_dao = DimensionTypeCAMDaoImpl()
            print(f"Inside DimensionTypeViewSet - Singleton Instance ID: {id(self)}")
            self.initialized = True

    # Adds a new dimension type and map it to the customer-application.
    @transaction.atomic
    def add_dimension_type(self, customer_uuid, application_uuid, user_uuid, dimension_type_data):
        try:
            uuid_data = (customer_uuid, application_uuid, user_uuid)
            dimension_type_name = dimension_type_data.get('dimension_type_name')

            # Check if the dimension type is default one.
            logger.debug(f"Checking if dimension type '{dimension_type_name}' is default one.")
            if self.__is_default_name(dimension_type_name):
                raise CustomException(ErrorMessages.DIMENSION_TYPE_EXISTS)

            logger.info(f"Starting creation of dimension type '{dimension_type_name}'.")

            # Build and save the dimension type instance.
            dimension_type = self.__get_or_create_dimension_type_instance(user_uuid, dimension_type_name)
            self.dimension_type_dao.save_dimension_type(dimension_type)

            # Build and save the dimension type mapping.
            dimension_type_mapping = self.__build_dimension_type_mapping_instance(uuid_data, dimension_type_data, dimension_type)
            self.dimension_type_cam_dao.save_dimension_type_mapping(dimension_type_mapping)

            logger.info(f"Dimension type '{dimension_type_name}' created and mapped successfully.")
        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                logger.error("Unique constraint violation occurred: %s", str(ie))
                raise CustomException(ErrorMessages.DIMENSION_TYPE_EXISTS)
            logger.error("Database integrity error: %s", str(ie))
            raise CustomException(ErrorMessages.DIMENSION_TYPE_CREATE_FAILED)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error(f"Transaction Failed while adding dimension type'. Error: {str(e)}")
            raise CustomException(ErrorMessages.DIMENSION_TYPE_CREATE_FAILED)

    # Retrieves all dimension types associated with the specified customer and application.
    def get_dimension_types(self, customer_uuid, application_uuid):
        # Fetch default and mapped dimension types

        get_dimension_types_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Fetching dimension types from DimensionType table:: {format_indian_time(get_dimension_types_st)}\n")
        default_dimension_types = list(self.dimension_type_dao.get_default_dimension_types())
        get_dimension_types_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Fetching dimension types from DimensionType table :: {format_indian_time(get_dimension_types_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Fetching dimension types from DimensionType table :: {(get_dimension_types_et - get_dimension_types_st).total_seconds() * 1000:.4f} ms\n")
        logger.info("Fetched default dimension types")

        get_dimension_type_mappings_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Fetching dimension types from DimensionType mapping table:: {format_indian_time(get_dimension_type_mappings_st)}\n")
        mapped_dimension_types = self.dimension_type_cam_dao.get_mapped_dimension_type_by_id_or_all(customer_uuid, application_uuid)
        get_dimension_type_mappings_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Fetching dimension types from DimensionType mapping table :: {format_indian_time(get_dimension_type_mappings_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Fetching dimension types from DimensionType mapping table :: {(get_dimension_type_mappings_et - get_dimension_type_mappings_st).total_seconds() * 1000:.4f} ms\n")
        logger.info("Fetched mapped dimension types")


        list_dimension_type_mappings_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Using List on  dimension types from DimensionType mapping table:: {format_indian_time(get_dimension_type_mappings_st)}\n")
        list(mapped_dimension_types)
        list_dimension_type_mappings_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Using List on dimension types from DimensionType mapping table :: {format_indian_time(list_dimension_type_mappings_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Using List on dimension types from DimensionType mapping table :: {(list_dimension_type_mappings_et - list_dimension_type_mappings_st).total_seconds() * 1000:.4f} ms\n")

        # Split mapped default and normal dimension types
        loop_dimension_type_mappings_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Looping dimension types from DimensionTypes mapping:: {format_indian_time(loop_dimension_type_mappings_st)}\n")
        mapped_default_dimension_types = {}
        mapped_normal_dimension_types = []
        for dimension_type in mapped_dimension_types:
            if dimension_type.get('is_default'):
                mapped_default_dimension_types[dimension_type.get('dimension_type_uuid')] = dimension_type
            else:
                mapped_normal_dimension_types.append(dimension_type)
        loop_dimension_type_mappings_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Looping dimension types from DimensionTypes mapping :: {format_indian_time(loop_dimension_type_mappings_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Looping dimension types from DimensionTypes mapping :: {(loop_dimension_type_mappings_et - loop_dimension_type_mappings_st).total_seconds() * 1000:.4f} ms\n")

        # First insert default dimension types
        loop_dimension_types_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Looping dimension types from DimensionTypes:: {format_indian_time(loop_dimension_types_st)}\n")
        response_data = []
        for dimension_type in default_dimension_types:
            if dimension_type.get('dimension_type_uuid') in mapped_default_dimension_types:
                response_data.append(mapped_default_dimension_types[dimension_type.get('dimension_type_uuid')])
            else:
                dimension_type['status'] = False
                dimension_type['description'] = self.__get_dimension_type_description(dimension_type.get('dimension_type_name'))
                response_data.append(dimension_type)
        loop_dimension_types_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Looping dimension types from DimensionTypes :: {format_indian_time(loop_dimension_types_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Looping dimension types from DimensionTypes :: {(loop_dimension_types_et - loop_dimension_types_st).total_seconds() * 1000:.4f} ms\n")

        # Extend mapped normal dimension types
        add_mapping_data_to_response_st = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time before Add mapping dimension types to response:: {format_indian_time(add_mapping_data_to_response_st)}\n")
        response_data += mapped_normal_dimension_types
        add_mapping_data_to_response_et = datetime.now()
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: time after Add mapping dimension types to response :: {format_indian_time(add_mapping_data_to_response_et)}\n")
        logger.info(f"\nTime profile :: Thread ID: {threading.get_ident()} :: Get DimensionTypes :: Total time taken Add mapping dimension types to response :: {(add_mapping_data_to_response_et - add_mapping_data_to_response_st).total_seconds() * 1000:.4f} ms\n")

        return response_data

    # Retrieves a dimension type based on the specified customer, application, and mapping UUID.
    def get_dimension_type_by_id(self, customer_uuid, application_uuid, mapping_uuid):
        # Fetch the dimension type mapping
        dimension_type_mapping = self.dimension_type_cam_dao.get_mapped_dimension_type_by_id_or_all(customer_uuid, application_uuid, mapping_uuid)

        # Serialize the data and return
        if dimension_type_mapping:
            serialized_data = DimensionTypeCAMModelSerializer(dimension_type_mapping).data
            logger.info(f"Fetched dimension type mapping of mapping UUID - {mapping_uuid}")
            return serialized_data
        else:
            return None

    # Edits an existing dimension type based on the provided customer, application, user, and dimension type data.
    @transaction.atomic
    def edit_dimension_type(self, customer_uuid, application_uuid, user_uuid, dimension_type_data):
        try:
            uuid_data = (customer_uuid, application_uuid, user_uuid)

            mapping_uuid = dimension_type_data.get('mapping_uuid')
            dimension_type_name = dimension_type_data.get('dimension_type_name')
            status = dimension_type_data.get('status')
            is_default_dimension_type = dimension_type_data.get('is_default')

            # If updating status of default dimension type for the first time
            if is_default_dimension_type and mapping_uuid is None and status is True:
                logger.info(f"Updating status of default dimension type for customer {customer_uuid} and application {application_uuid}")
                self.edit_status_for_default_types(uuid_data, dimension_type_data)
                return

            # Else update the mapping instance and save
            if mapping_uuid is None:
                raise CustomException(ErrorMessages.MAPPING_UUID_NOT_NULL)

            # Fetch the existing mapping
            logger.info(f"Fetching existing dimension type mapping for customer {customer_uuid}, application {application_uuid} and mapping_uuid {mapping_uuid}")
            dimension_type_mapping = self.dimension_type_cam_dao.get_mapped_dimension_type_by_id_or_all(customer_uuid,
                                                                                                        application_uuid,
                                                                                                        mapping_uuid)
            if dimension_type_mapping is None:
                raise CustomException(ErrorMessages.DIMENSION_TYPE_NOT_FOUND)

            # Get Dimension type from mapping
            dimension_type = dimension_type_mapping.dimension_type_uuid

            # If Dimension Type Name updated, remove mapping to the previous dimension type and map a new dimension type
            if dimension_type.dimension_type_name != dimension_type_name:
                # Get or create new dimension type
                new_dimension_type = self.__create_new_dimension_type(uuid_data, dimension_type_name)
                # Map the new dimension type
                dimension_type_mapping.dimension_type_uuid = new_dimension_type

            # Update each field of mapping
            self.__update_dimension_type(dimension_type_data, dimension_type_mapping, user_uuid)

            # Save the mapping instance
            self.dimension_type_cam_dao.save_dimension_type_mapping(dimension_type_mapping)
        except IntegrityError as ie:
            if 'unique constraint' in str(ie):
                logger.error("Unique constraint violation occurred: %s", str(ie))
                raise CustomException(ErrorMessages.DIMENSION_TYPE_EXISTS)
            logger.error("Database integrity error: %s", str(ie))
            raise CustomException(ErrorMessages.DIMENSION_TYPE_UPDATE_FAILED)
        except CustomException as ce:
            raise ce
        except Exception as e:
            logger.error(f"Transaction Failed while updating dimension type'. Error: {str(e)}")
            raise CustomException(ErrorMessages.DIMENSION_TYPE_UPDATE_FAILED)

    # Edits the status of default dimension types and map default dimension values if any.
    @transaction.atomic
    def edit_status_for_default_types(self, uuid_data, dimension_type_data):
        try:
            dimension_type_uuid = dimension_type_data.get('dimension_type_uuid')

            # Create mapping with default dimension type
            logger.info(f"Creating default dimension type mapping instance for dimension type UUID: {dimension_type_uuid}")
            default_dimension_type = DimensionType(dimension_type_uuid=dimension_type_uuid)
            dimension_type_mapping = self.__build_dimension_type_mapping_instance(uuid_data, dimension_type_data, default_dimension_type)

            # Save the dimension type mapping
            self.dimension_type_cam_dao.save_dimension_type_mapping(dimension_type_mapping)

            # Fetch all default dimensions under this dimension type uuid
            logger.info(f"Fetching default dimensions for dimension type UUID: {dimension_type_uuid}")
            default_dimensions = self.dimension_type_dao.get_default_dimensions(dimension_type_uuid)

            # Create mappings for default dimensions
            dimension_mappings = []
            for dimension in default_dimensions:
                dimension_mapping = self.__build_dimension_mapping_instance(uuid_data, dimension)
                dimension_mappings.append(dimension_mapping)

            # Bulk create dimensions
            self.dimension_type_dao.bulk_create_dimensions(dimension_mappings)
        except Exception as e:
            logger.error(f"Transaction Failed while updating dimension type status'. Error: {str(e)}")
            raise CustomException(ErrorMessages.DIMENSION_TYPE_UPDATE_FAILED)

    def delete_dimension_type_mapping(self, customer_uuid, application_uuid, mapping_uuid):
        logger.info(f"Deleting dimension type mapping for customer {customer_uuid}, application {application_uuid}, and mapping_uuid {mapping_uuid}")

        # Combine fetching and deleting in one operation
        deleted, _ = self.dimension_type_cam_dao.delete_dimension_type_mapping(customer_uuid, application_uuid, mapping_uuid)

        if deleted == 0:
            raise CustomException(ErrorMessages.DIMENSION_TYPE_NOT_FOUND)

        logger.info("Dimension type mapping deleted successfully.")

    # Helper Methods
    def __get_or_create_dimension_type_instance(self, user_uuid, dimension_type_name):
        """
        Creates a new DimensionType instance or retrieves an existing one.

        :param: user_uuid (str): The ID of the user creating or updating the dimension type.
        :param: dimension_type_name (str): The name of the dimension type.

        :return: The DimensionType instance (either newly created or retrieved).
        """

        dimension_type, _ = self.dimension_type_dao.get_or_create_dimension_type(dimension_type_name, user_uuid)

        return dimension_type

    def __build_dimension_type_mapping_instance(self, uuid_data, validated_data, dimension_type):
        """
        Creates a new DimensionTypeCustomerApplicationMapping instance.

        :param uuid_data: A tuple containing the customer UUID, application UUID, and user ID.
        :param validated_data: A dictionary containing the validated data for the dimension type mapping.
        :param dimension_type: The DimensionType instance associated with the mapping.

        :return: A new DimensionTypeCustomerApplicationMapping instance.
        """

        customer_uuid, application_uuid, user_uuid = uuid_data

        dimension_type_details_json = validated_data.get('dimension_type_details_json')
        dimension_type_details_json_dict = asdict(dimension_type_details_json) if dimension_type_details_json is not None else None
        description = self.__get_dimension_type_description(
            validated_data.get('dimension_type_name')) if validated_data.get('is_default') else validated_data.get('description')

        return DimensionTypeCustomerApplicationMapping(
            mapping_uuid=str(uuid.uuid4()),
            dimension_type_uuid=dimension_type,
            description=description,
            dimension_type_details_json=dimension_type_details_json_dict,
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            created_by=user_uuid,
            updated_by=user_uuid
        )

    def __build_dimension_mapping_instance(self, uuid_data, dimension):
        """
        Creates a new DimensionCustomerApplicationMapping instance for a dimension.

        :param uuid_data: A tuple containing the customer UUID, application UUID, and user ID.
        :param dimension: The Dimension instance associated with the mapping.

        :return: A new DimensionCustomerApplicationMapping instance.
        """

        customer_uuid, application_uuid, user_uuid = uuid_data
        return DimensionCustomerApplicationMapping(
            mapping_uuid=str(uuid.uuid4()),
            dimension_uuid=dimension,
            description='description',
            dimension_details_json={},
            application_uuid=Applications(application_uuid),
            customer_uuid=Customers(customer_uuid),
            created_by=user_uuid,
            updated_by=user_uuid
        )

    def __create_new_dimension_type(self, uuid_data, dimension_type_name):
        """
        Creates a new dimension type for the specified customer and application.

        :param uuid_data (tuple): A tuple containing the customer UUID, application UUID, and user ID.
        :param: dimension_type_name (str): The name of the new dimension type.
        :return: DimensionType: The newly created DimensionType instance.
        """

        _, _, user_uuid = uuid_data

        # Check if new dimension type name is default name
        if self.__is_default_name(dimension_type_name):
            raise CustomException(ErrorMessages.DIMENSION_TYPE_EXISTS)

        # Create new dimension type and map it
        return self.__get_or_create_dimension_type_instance(user_uuid, dimension_type_name)

    def __get_dimension_type_description(self, dimension_type_name):
        """
        Retrieves the default description for a dimension type.

        :param dimension_name (str): The name of the dimension type.
        :return: The default description for the dimension type, or None if not found.
        """

        return DefaultDimensionTypeDescription.dimension_type_descriptions.get(dimension_type_name.lower())

    def __is_default_name(self, dimension_type_name):
        """
        Checks if a dimension type name is a default name.

        :param dimension_type_name (str): The name of the dimension type.
        :return: True if the dimension type name is a default name, False otherwise.
        """

        return dimension_type_name.lower() in list(DefaultDimensionTypeDescription.dimension_type_descriptions.keys())

    def __update_dimension_type(self, dimension_type_data, dimension_type_mapping, user_uuid):
        """
        Updates the Dimension Type Mapping instance with the provided data.

        :param dimension_type_data: A dictionary containing the updated details for the dimension type.
        :param dimension_type_mapping: The DimensionTypeCustomerApplicationMapping instance to be updated.
        :param user_uuid: UUID of the user making the update.
        """

        # Convert the dimension type details from data to a dictionary
        dimension_type_details_json = dimension_type_data.get('dimension_type_details_json')
        dimension_type_details_json_dict = asdict(dimension_type_details_json) if dimension_type_details_json is not None else None

        dimension_type_mapping.dimension_type_details_json = dimension_type_details_json_dict
        dimension_type_mapping.status = dimension_type_data.get('status')
        dimension_type_mapping.description = dimension_type_data.get('description')

        dimension_type_mapping.updated_by = user_uuid
