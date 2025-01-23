from django.test import TestCase
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .test_error_data import create_data_table
from django.core.management import call_command
import uuid


class BaseTestCase(TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        
        super().setUpClass()
        call_command('makemigrations')
        call_command('migrate')


class TableCorrectionTestCase(BaseTestCase):
    
    def setUp(self):
        
        self.client = APIClient()
        file, error = create_data_table()
        
        self.file = file
        self.error = error
    
    def test_get_table(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.get(
            reverse('ChatBot:get_table', kwargs = {'file_uuid' : file_uuid, 'table_id' : 5})
        )
        json_response = response.json()
        
        columns = json_response['result']['columns']
        self.assertEqual(columns, ['Checking operation  ', 'Time interval   ', 'Criteria '])
        
        matrix = json_response['result']['matrix']
        self.assertEqual(
            matrix, 
            [['Carry out five mechanical  opening closing operations.  ',
            '1 Year   ',
            'The circuit-breaker must operate normally without stopping in intermediate positions '],
            ['Visual inspection of the poles   (insulating parts).  ',
            '1 Yr./ 5000   operations   ',
            'The insulating parts must be free of any accumulation of dust, dirt, cracks, discharges or traces of surface discharges '],
            ['Visual inspection of the operating   mechanism and transmission.  ',
            '1 Yr./ 5000  operations   ',
            'The elements must be free of any deformation. Screws, nuts, bolts, etc. must be tight. '],
            ['Measuring the insulation   resistance.   ',
            '1 Yr/5000   operations ',
            'See par. 8.1. point 1. '
            ]]
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        url = json_response['result']['table_image_url']
        url = url.replace(' ', '%20')
        self.assertEqual('connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/Table_3.png' in url, True)
        
    def test_get_table_list_of_lists(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.get(
            reverse('ChatBot:get_table', kwargs = {'file_uuid' : file_uuid, 'table_id' : 2})
        )
        json_response = response.json()
        
        columns = json_response['result']['columns']
        self.assertEqual(columns, ['a', 'b', 'c'])
        
        matrix = json_response['result']['matrix']
        self.assertEqual(
            matrix, 
            [[1, 2, 3], [4, 5, 6]]
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        url = json_response['result']['table_image_url']
        url = url.replace(' ', '%20')
        self.assertEqual('connected-enterprise/my_customer/my_app/2024/October/pdf/SF6%20Circuit%20Breaker%20-%20Type%20OHB%20manual/Table_3.png' in url, True)
    
    def test_get_table_from_csv(self):
        
        csv_bytes = open('/home/vassar/Files/Stanley ProCare/tab.csv', 'rb').read()
        uploaded_file = SimpleUploadedFile("tab.csv", csv_bytes, content_type="text/csv")
        data = {
            'csvfile': uploaded_file  
        }
        
        response = self.client.post(
            reverse('ChatBot:errors_tables'),
            data=data,
            format="multipart"
        )
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result']['columns'], ['A', 'B', 'C'])
        self.assertEqual(json_response['result']['matrix'], [['1', '2', '3']])
        
    def test_get_table_from_xlsx(self):
        
        csv_bytes = open('/home/vassar/Files/Stanley ProCare/tables/fileoutpart2.xlsx', 'rb').read()
        uploaded_file = SimpleUploadedFile("fileoutpart2.xlsx", csv_bytes, content_type="text/csv")
        data = {
            'csvfile': uploaded_file  
        }
        
        response = self.client.post(
            reverse('ChatBot:errors_tables'),
            data=data,
            format="multipart"
        )
        json_response = response.json()
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result']['matrix'], [['0.05 _x000D_', 'AMBIENT _x000D_', '1.36 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.10 _x000D_', 'AMBIENT _x000D_', '1.89 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.20 _x000D_', 'AMBIENT _x000D_', '2.99 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.30 _x000D_', 'AMBIENT _x000D_', '3.87 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.05 _x000D_', '400 _x000D_', '0.32 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.10 _x000D_', '400 _x000D_', '0.69 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.20 _x000D_', '400 _x000D_', '0.93 _x000D_', '2 _x000D_', 'NO _x000D_'], ['0.30 _x000D_', '400 _x000D_', '1.02 _x000D_', '2 _x000D_', 'NO _x000D_']])
        self.assertEqual(json_response['result']['columns'], ['PRESSURE (IN. WC) _x000D_', 'AIR TEMP, °F _x000D_', 'LEAKAGE (CFM/SQ FT) _x000D_', 'CLOSING FORCE, LB _x000D_', 'ARTIFICIAL BOTTOM SEAL _x000D_'])
        
    def test_update_table(self):
        
        file_uuid = self.file.knowledge_source_uuid
        error_uuid = self.error.error_uuid
        
        columns = ['Column1', 'Column2', 'Column3']
        matrix = [
            ['Row1Value1', 'Row1Value2', 'Row1Value3'],
            ['Row2Value1', 'Row2Value2', 'Row2Value3']
        ]
        table_id = 0
        
        response = self.client.put(
            reverse('ChatBot:errors_tables'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'table_id' : table_id,
                'columns' : columns,
                'matrix' : matrix
            },
            format="json"
        )
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result'], SuccessMessages.TABLE_UPDATE_SUCCESS)
    
    def test_update_table_no_table(self):
        
        file_uuid = self.file.knowledge_source_uuid
        error_uuid = self.error.error_uuid
        
        columns = ['Column1', 'Column2', 'Column3']
        matrix = [
            ['Row1Value1', 'Row1Value2', 'Row1Value3'],
            ['Row2Value1', 'Row2Value2', 'Row2Value3']
        ]
        table_id = 100
        
        response = self.client.put(
            reverse('ChatBot:errors_tables'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'table_id' : table_id,
                'columns' : columns,
                'matrix' : matrix
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_table_negative(self):
        
        file_uuid = str(uuid.uuid4())
        error_uuid = self.error.error_uuid
        
        columns = ['Column1', 'Column2', 'Column3']
        matrix = [
            ['Row1Value1', 'Row1Value2', 'Row1Value3'],
            ['Row2Value1', 'Row2Value2', 'Row2Value3']
        ]
        table_id = 100
        
        response = self.client.put(
            reverse('ChatBot:errors_tables'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'table_id' : table_id,
                'columns' : columns,
                'matrix' : matrix
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)