import sys
import chromadb
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import json
from ExtractClausesApp.utils import get_chunks_for_document, extract_guidelines, response_from_llm_for_relevant_chunks, storage_path_chroma, \
    check_deduplication, add_clauses_to_chroma_db,get_doe_clauses,response_from_llm,get_project_id,response_from_decomposition, response_from_llm_for_initial_answer,\
    response_from_llm_for_external_standards,response_from_llm_for_references
from ExtractClausesApp.constants import DOCUMENT_NAME,CUSTOMER_ID_UCOR, OUTPUT_CLAUSES_FINAL,FINAL_CLAUSES_414,DEMO_RESPONSE, GUIDELINES_COLLECTION_NAME,TEST_CLAUSES,TEST_CLAUSES_ONLY_TWO,TEST_CLAUSES_V2,extrated_clauses_10CFR,extrated_clauses_226,extracted_clauses_414
from ExtractClausesApp.models import ComplianceReport
from uuid import uuid4
import time
import logging
logger = logging.getLogger(__name__)
class ExtractClauseViewSet(ViewSet):

    @action(detail=False, methods=['post'])
    def extract_clauses_from_docs(self, request, *args, **kwargs):
        try:
            document_name =DOCUMENT_NAME
            collection_name = 'doe_guidelines'
            filtered_data = {'DOE Guidelines': {'Document Name': document_name}}
            # getting all the chunks
            chunks = get_chunks_for_document(query= 'random query',num_of_chunks=10000,filtered_data=filtered_data,headers=request.headers)
            if chunks == "UM api failure":
                response = chunks
                data = {"message": response, "extracted clauses": []}
                return Response(data, status=status.HTTP_200_OK)
            if len(chunks) > 0 and chunks != "UM api failure":
                if chunks[0]["metadata"]["entity_name"] == "DOE Guidelines":
                    print("No. Of Chunks::",len(chunks))
                    #extract the guidelines by sending the chunks
                    print("calling extract_guidelines ")
                    extracted_clauses = extract_guidelines(chunks)
                    print("length of extracted guidelines::",len(extracted_clauses))
                    data= {"message": "Clauses extracted", "extracted clauses": extracted_clauses}
                    # Initialize chroma client
                    chroma_client = chromadb.PersistentClient(path=storage_path_chroma)
                    collection = chroma_client.get_or_create_collection(name=collection_name)
                    if collection.count() > 0:
                        # if some clause already present in the chroma then check for the de-duplicate
                        print("going for the de duplication")
                        response = check_deduplication(extracted_clauses,chroma_client)
                        data = {"message": "Clauses extracted", "extracted clauses": response}
                    else:
                        # else add without do deduplication
                        response = add_clauses_to_chroma_db(chroma_client,extracted_clauses)
                        data = {"message": "Clauses extracted", "extracted clauses": response}
            else:
                response = "No Chunks Found for current Document"
                data = {"message": response, "extracted clauses": []}

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Exception Occurred: {str(e)}"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)
            print(error_message)
            data = {"error": error_message}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post', 'options'])
    def validate_supplier_docs(self, request, *args, **kwargs):
        try:
            body_json = request.body.decode('utf-8')
            project_id =json.loads(body_json).get('project_id',None)
            compliance = ComplianceReport.objects.filter(project_id=project_id)

            if compliance.exists(): 
                report = compliance.values('report').first()
                data = {"message": "Document is Validated", "results": report}
                return Response(data, status=status.HTTP_200_OK)
            else:
                result = ComplianceReport.objects.filter(
                    project_id='DOE Guidelines',
                ).values('report').first()
                clauses = []
                if result is not None:
                    clauses = result.get('report')
                filtered_data_doe = {'DOE Guidelines': {}} 
                result = {}
                result_list=[]
                for clause in clauses:
                    data={'clause':clause['clause']}

                    #get relevant chunks
                    relevant_chunks = get_chunks_for_document(query = data['clause'],num_of_chunks=10,filtered_data=filtered_data_doe,headers=request.headers)
                    data['relevant_chunks'] = relevant_chunks
                    
                    time.sleep(5)
                    #create initial answer
                    response_for_initial_answer =  response_from_llm_for_initial_answer(data)
                    data['initial_answer'] = response_for_initial_answer["output"]
                    data['external_references'] = response_for_initial_answer['external_references']

                    time.sleep(5)

                    #references details extraction
                    response_for_references = response_from_llm_for_references(data['external_references'],data['clause'])
                    data['details_for_external_references'] = response_for_references
                    
                    time.sleep(5)

                    #generating final combined answer
                    combined_response = response_from_llm_for_external_standards(data['clause'], data['initial_answer'],data['external_references'])
                    data['combined_answer'] = combined_response

                    time.sleep(5)
                    #creating decomposed requirements
                    decomposed_requirements = response_from_decomposition(data['combined_answer'])
                    data['decomposed_requirements'] = decomposed_requirements["queries"] 

                    #start validating document
                    print("Project ID::",project_id)

                    filtered_data_supplier = {'UCOR Supplier Submission':{'Project ID':project_id}} 
                    final_chunks = []
                    chunk_ids = []
                    for requirement in data['decomposed_requirements']: 
                        chunks_for_supplier_docs = get_chunks_for_document(query = requirement,num_of_chunks=4,filtered_data=filtered_data_supplier,headers=request.headers)
                        for chunk in chunks_for_supplier_docs:
                            if chunk['id'] not in chunk_ids:
                                final_chunks.append(chunk)
                                chunk_ids.append(chunk['id'])
                    
                    print("Length of final chunks::",len(final_chunks))
                    time.sleep(5)

                    # Now we got final chunks in final_chunks array
                    # Make a final call to llm for evaluation response documents
                    response_for_evaluation = response_from_llm(data['clause'],final_chunks, data['decomposed_requirements'])
                    data['evaluation_result'] = response_for_evaluation
                    result_list.append(data)

                result["clauses"] = result_list

                #saving them in database for better results
                if len(result_list) > 0: 
                    ComplianceReport.objects.create(
                        report_id = uuid4(),
                        customer_uuid=CUSTOMER_ID_UCOR,
                        project_id=project_id,
                        report=json.dumps(result)
                    )
                else:
                    print("No clauses found")
                data = {"message": "Document Validation in progress","results":result}
                return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            data = {"message": "Exception Occured in Validation of Docs","error messsage":str(e),"line no":exc_tb.tb_lineno}  # Example response data
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def add_clauses_from_docs(self, request, *args, **kwargs):
        collection_name = 'doe_guidelines'
        extracted_clauses = request.data['extracted_clauses']
        # Initialize chroma client
        logger.debug("Initializing the chroma client")
        chroma_client = chromadb.PersistentClient(path=storage_path_chroma)
        logger.debug("Getting the collection")
        print("getting collection")
        collection = chroma_client.get_or_create_collection(name=collection_name)
        if collection.count()== 0:
            # else add without do deduplication
            logger.info("New collection added")
            response = add_clauses_to_chroma_db(chroma_client, extracted_clauses)
            logger.info("clauses added to chroma db first time")
            data = {"message": "Clauses extracted", "extracted clauses": response}
        else:
            data = {"message": "First empty the chroma db with collection doe_guidelines", "extracted clauses": []}

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_clauses_from_docs(self, request, *args, **kwargs):
        try:
            result = ComplianceReport.objects.filter(
                project_id='DOE Guidelines',
            ).values('report').first()

            if result is None:
                data = {"message": "No data found", "clauses": None}
            else:
                data = {"message": "It's working", "clauses": result.get('report')}

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Exception Occurred: {str(e)}"
            print(error_message)
            data = {"message": "Exception Aa gaya"}  # Example response data
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
