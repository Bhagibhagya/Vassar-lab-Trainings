import json

from DatabaseApp.models import Customers, Applications, CustomerApplicationMapping
from DatabaseApp.models import KnowledgeSources, Entities, Errors

from azure.storage.blob import BlobServiceClient, ContentSettings
import mimetypes
from urllib.parse import unquote


defaut_azure_conn_str="DefaultEndpointsProtocol=https;AccountName=vassarstorage;AccountKey=swchwatDlv5wKfoOOqxaudMSDkyobu0HrDWqBWCl/QP+rRCK5/1UQycuCdY/XLXoORl+9zzVe5GQ+AStRn+B5g==;EndpointSuffix=core.windows.net"
default_azure_container="connected-enterprise"


class AzureBlobManager():
    
    def __init__(self, connection_string):
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.account_key = self.blob_service_client.credential.account_key

    def update_json_to_blob_name(self, json, blob_name, container_name):

        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(unquote(blob_name))

        blob_client.upload_blob(json.encode('utf-8'), overwrite=True)
        new_file_url = blob_client.url

        return new_file_url
    
    def upload_attachments_to_azure_blob(self, file_paths, blob_name, container_name):

        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(unquote(blob_name))

        urls = []
        for file_path in file_paths:
            
            content_type = mimetypes.guess_type(file_path)
            
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True,content_settings=ContentSettings(content_type=content_type))

            file_url = blob_client.url
            urls.append(file_url)
           
        return urls
    
    def download_json_from_blob_name(self, blob_name, container_name):

        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(unquote(blob_name))
  
        if blob_client.exists():
            
            details_json = blob_client.download_blob().readall().decode('utf-8')

            return details_json


def create_data_header():
    
    cuuid = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
    cname = 'my_customer'
    email = 'customer@ce.vassar.ai'
    contact = '0123456789'

    customer = Customers.objects.create(
        cust_uuid=cuuid,
        cust_name=cname,
        email=email,
        primary_contact=contact
    )

    auuid = '5d2b2a38-c3db-4033-9402-23dc3e901601'
    aname = 'my_app'
    url = 'myapp.ce.vassar.ai'
    scope = 'scope.myapp.ce.vassar.ai'

    application = Applications.objects.create(
        application_uuid=auuid, 
        application_name=aname,
        application_url=url,
        scope_end_point=scope
    )

    camuuid = '9cc0292d-176b-49b2-9855-27861563f7cc'

    CustomerApplicationMapping.objects.create(
        customer_application_id=camuuid,
        customer=customer,
        application=application
    )

    customer = Customers.objects.filter(cust_uuid=cuuid).first()
    app = Applications.objects.filter(application_uuid=auuid).first()
    ename = 'default'
    euuid = '07a936b4-1241-4f80-b8a6-644babbb2219'

    entity = Entities.objects.create(
        entity_uuid=euuid,
        entity_name=ename,
        customer_uuid=customer,
        application_uuid=app,
        attribute_details_json={'default' : ['default']}
    )

    js = json.dumps(json.load(open('/home/vassar/Files/mesa/internalFormat-SF6.json', 'r')))

    manager = AzureBlobManager(connection_string=defaut_azure_conn_str)
    blob = "connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/internalFormat.json"
    manager.update_json_to_blob_name(js, blob, default_azure_container)

    fuuid = 'e9141856-cca7-476d-9db8-a6a49c177768'
    file = KnowledgeSources.objects.create(
        knowledge_source_uuid = fuuid,
        knowledge_source_name = 'SF6 Circuit Breaker - Type OHB manual.pdf',
        knowledge_source_path = 'connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual.pdf',
        knowledge_source_type = 'PDF',
        knowledge_source_status = 'Reviewed',
        knowledge_source_metadata = {},
        application_uuid = app,
        customer_uuid = customer,
        entity_uuid = entity,
        attribute_details_json = {'entity_name' : 'default', 'attributes' : {'default' : 'default'}}
    )
    
    error_uuid = 'd19ff37d-8921-49e1-b513-5f826f2264a9'
    error_type = 'headers'
    error_status = 'Unresolved'
    
    error = Errors.objects.create(
        error_uuid=error_uuid,
        error_type=error_type,
        error_status=error_status,
        knowledge_source_uuid=file,
        customer_uuid=customer,
        application_uuid=application
    )
    
    return file, error


def create_data_table():
    
    cuuid = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
    cname = 'my_customer'
    email = 'customer@ce.vassar.ai'
    contact = '0123456789'

    customer = Customers.objects.create(
        cust_uuid=cuuid,
        cust_name=cname,
        email=email,
        primary_contact=contact
    )

    auuid = '5d2b2a38-c3db-4033-9402-23dc3e901601'
    aname = 'my_app'
    url = 'myapp.ce.vassar.ai'
    scope = 'scope.myapp.ce.vassar.ai'

    application = Applications.objects.create(
        application_uuid=auuid, 
        application_name=aname,
        application_url=url,
        scope_end_point=scope
    )

    camuuid = '9cc0292d-176b-49b2-9855-27861563f7cc'

    CustomerApplicationMapping.objects.create(
        customer_application_id=camuuid,
        customer=customer,
        application=application
    )

    customer = Customers.objects.filter(cust_uuid=cuuid).first()
    app = Applications.objects.filter(application_uuid=auuid).first()
    ename = 'default'
    euuid = '07a936b4-1241-4f80-b8a6-644babbb2219'

    entity = Entities.objects.create(
        entity_uuid=euuid,
        entity_name=ename,
        customer_uuid=customer,
        application_uuid=app,
        attribute_details_json={'default' : ['default']}
    )

    js = json.dumps(json.load(open('/home/vassar/Files/mesa/internalFormat-SF6.json', 'r')))

    manager = AzureBlobManager(connection_string=defaut_azure_conn_str)
    blob = "connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/internalFormat.json"
    manager.update_json_to_blob_name(js, blob, default_azure_container)

    fuuid = 'e9141856-cca7-476d-9db8-a6a49c177768'
    file = KnowledgeSources.objects.create(
        knowledge_source_uuid = fuuid,
        knowledge_source_name = 'SF6 Circuit Breaker - Type OHB manual.pdf',
        knowledge_source_path = 'connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual.pdf',
        knowledge_source_type = 'PDF',
        knowledge_source_status = 'Reviewed',
        knowledge_source_metadata = {},
        application_uuid = app,
        customer_uuid = customer,
        entity_uuid = entity,
        attribute_details_json = {'entity_name' : 'default', 'attributes' : {'default' : 'default'}}
    )
    
    error_uuid = 'd19ff37d-8921-49e1-b513-5f826f2264a9'
    error_type = 'table'
    error_status = 'Unresolved'
    
    error = Errors.objects.create(
        error_uuid=error_uuid,
        error_type=error_type,
        error_status=error_status,
        knowledge_source_uuid=file,
        customer_uuid=customer,
        application_uuid=application
    )
    
    return file, error


def create_data_page():
    
    cuuid = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
    cname = 'my_customer'
    email = 'customer@ce.vassar.ai'
    contact = '0123456789'

    customer = Customers.objects.create(
        cust_uuid=cuuid,
        cust_name=cname,
        email=email,
        primary_contact=contact
    )

    auuid = '5d2b2a38-c3db-4033-9402-23dc3e901601'
    aname = 'my_app'
    url = 'myapp.ce.vassar.ai'
    scope = 'scope.myapp.ce.vassar.ai'

    application = Applications.objects.create(
        application_uuid=auuid, 
        application_name=aname,
        application_url=url,
        scope_end_point=scope
    )

    camuuid = '9cc0292d-176b-49b2-9855-27861563f7cc'

    CustomerApplicationMapping.objects.create(
        customer_application_id=camuuid,
        customer=customer,
        application=application
    )

    customer = Customers.objects.filter(cust_uuid=cuuid).first()
    app = Applications.objects.filter(application_uuid=auuid).first()
    ename = 'default'
    euuid = '07a936b4-1241-4f80-b8a6-644babbb2219'

    entity = Entities.objects.create(
        entity_uuid=euuid,
        entity_name=ename,
        customer_uuid=customer,
        application_uuid=app,
        attribute_details_json={'default' : ['default']}
    )

    js = json.dumps(json.load(open('/home/vassar/Files/mesa/internalFormat-SF6_2.json', 'r')))

    manager = AzureBlobManager(connection_string=defaut_azure_conn_str)
    blob = "connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual_2/internalFormat.json"
    manager.update_json_to_blob_name(js, blob, default_azure_container)

    fuuid = 'e9141856-cca7-476d-9db8-a6a49c177768'
    file = KnowledgeSources.objects.create(
        knowledge_source_uuid = fuuid,
        knowledge_source_name = 'SF6 Circuit Breaker - Type OHB manual.pdf',
        knowledge_source_path = 'connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual_2/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual_2.pdf',
        knowledge_source_type = 'PDF',
        knowledge_source_status = 'Reviewed',
        knowledge_source_metadata = {},
        application_uuid = app,
        customer_uuid = customer,
        entity_uuid = entity,
        attribute_details_json = {'entity_name' : 'default', 'attributes' : {'default' : 'default'}}
    )
    
    error_uuid = 'd19ff37d-8921-49e1-b513-5f826f2264a9'
    error_type = 'page'
    error_status = 'Unresolved'
    
    error = Errors.objects.create(
        error_uuid=error_uuid,
        error_type=error_type,
        error_status=error_status,
        knowledge_source_uuid=file,
        customer_uuid=customer,
        application_uuid=application
    )
    
    return file, error


def create_data_video():
    
    cuuid = '8e556ba8-9c27-4a3f-9335-b78ae937392a'
    cname = 'my_customer'
    email = 'customer@ce.vassar.ai'
    contact = '0123456789'

    customer = Customers.objects.create(
        cust_uuid=cuuid,
        cust_name=cname,
        email=email,
        primary_contact=contact
    )

    auuid = '5d2b2a38-c3db-4033-9402-23dc3e901601'
    aname = 'my_app'
    url = 'myapp.ce.vassar.ai'
    scope = 'scope.myapp.ce.vassar.ai'

    application = Applications.objects.create(
        application_uuid=auuid, 
        application_name=aname,
        application_url=url,
        scope_end_point=scope
    )

    camuuid = '9cc0292d-176b-49b2-9855-27861563f7cc'

    CustomerApplicationMapping.objects.create(
        customer_application_id=camuuid,
        customer=customer,
        application=application
    )

    customer = Customers.objects.filter(cust_uuid=cuuid).first()
    app = Applications.objects.filter(application_uuid=auuid).first()
    ename = 'default'
    euuid = '07a936b4-1241-4f80-b8a6-644babbb2219'

    entity = Entities.objects.create(
        entity_uuid=euuid,
        entity_name=ename,
        customer_uuid=customer,
        application_uuid=app,
        attribute_details_json={'default' : ['default']}
    )

    js = json.dumps(json.load(open('/home/vassar/Files/internalFormat-CBH.json', 'r')))

    manager = AzureBlobManager(connection_string=defaut_azure_conn_str)
    blob = "connected-enterprise/my_customer/my_app/2024/October/video/CBH/internalFormat.json"
    manager.update_json_to_blob_name(js, blob, default_azure_container)

    fuuid = 'e9141856-cca7-476d-9db8-a6a49c177768'
    file = KnowledgeSources.objects.create(
        knowledge_source_uuid = fuuid,
        knowledge_source_name = 'CBH.mp4',
        knowledge_source_path = 'connected-enterprise/my_customer/my_app/2024/October/video/CBH/CBH.mp4',
        knowledge_source_type = 'Video',
        knowledge_source_status = 'Reviewed',
        knowledge_source_metadata = {},
        application_uuid = app,
        customer_uuid = customer,
        entity_uuid = entity,
        attribute_details_json = {'entity_name' : 'default', 'attributes' : {'default' : 'default'}}
    )
    
    error_uuid = 'da87a980-542a-4745-8043-c0d257571062'
    error_type = 'video'
    error_status = 'Unresolved'
    
    error = Errors.objects.create(
        error_uuid=error_uuid,
        error_type=error_type,
        error_status=error_status,
        knowledge_source_uuid=file,
        customer_uuid=customer,
        application_uuid=application
    )
    
    return file, error