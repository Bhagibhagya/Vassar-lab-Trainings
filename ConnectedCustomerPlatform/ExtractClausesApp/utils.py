import time
import uuid
from venv import logger
import chromadb
import httpx
from langchain.chains import LLMChain
from ExtractClausesApp.AIServices.llm import llm, embeddings
from ExtractClausesApp.AIServices.prompts import clause_prompt,de_duplicate_prompt,evaluation_prompt,quantitative_prompt,\
        referencing_prompt,quantitative_prompt_v2,relevant_chunks_prompt,chunks_extraction_prompt,query_decomposition_prompt,format_text_prompt \
        , initial_answer_prompt, external_reference_prompt, external_standards_prompt
import json
import sys
import re
import requests
from openai._exceptions import APITimeoutError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
import logging
logger = logging.getLogger(__name__)

storage_path_chroma='/home/vassar/Documents/MESA_UCOR_POC/GenAI/chroma_data'

def get_header(customer_uuid,application_uuid,user_uuid,csrf_token,authorization):
    headers = {
        'customer-uuid': customer_uuid,
        'application-uuid': application_uuid,
        'user-uuid': user_uuid,
        'csrf-token': csrf_token,
        'Authorization': authorization
    }
    return headers

def get_project_id():
    try:
        url = 'https://dev.ce.vassardigital.ai/api/chatbot/entity/30d10b41-e359-4772-914d-b2bed8cafad8'

        headers = get_header('9a2f0f2e-7260-47ff-8403-98104657078e', '047cab49-538c-4bcd-a56d-440b35b4e0c3',
                            '39887cfc-fb15-4180-ba0a-06f35f76a424')
        response = requests.get(url=url, headers=headers)
        print("Response",response)
        project_ids = response.json().get('result', {}).get('attributes', {}).get('Project ID', {}).get('values', None)
        return project_ids
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Chunks From Document: {e}"


def gpt_call(llm_chain, data):

    response = llm_chain.run(data)
    print("DEBUG : Response From GPT ::",response)
    return response

def extract_and_clean_json(input_string):
    """
    Extracts and attempts to clean the first JSON object found within a string.

    Args:
        input_string (str): The input string containing JSON-like content.

    Returns:
        str: The cleaned and extracted JSON string, or None if no valid JSON could be extracted.
    """
    logger.info("Inside extract_and_clean_json function")
    json_pattern = r'\{.*\}'  # Match JSON-like structures
    logger.info("Searching for JSON within the input string")

    match = re.search(json_pattern, input_string, re.DOTALL)
    if match:
        json_str = match.group(0)  # Extract the matched JSON string
        try:
            # Attempt to clean and load JSON
            logger.info("Attempting to load and validate the extracted JSON")
            json_object = json.loads(json_str)  # Test if it is valid JSON
            return json.dumps(json_object)  # Return as a valid JSON string
        except json.JSONDecodeError as e:
            # Try to clean the JSON string if there's an error
            logger.warning(f"Initial JSON decoding failed: {e}. Attempting to clean the JSON string.")
            cleaned_json_str = clean_json_string(json_str)
            try:
                json_object = json.loads(cleaned_json_str)
                logger.info("Successfully cleaned and loaded JSON")
                return json.dumps(json_object)
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to clean and load JSON: {e2}")
                return None
    else:
        logger.warning("No JSON object found in the input string")
        return None

def clean_json_string(json_string):
    """
    Cleans a JSON string by fixing common issues like improper escaping or extra characters.

    Args:
        json_string (str): The JSON string to clean.

    Returns:
        str: The cleaned JSON string.
    """
    logger.info("Cleaning JSON string")
    # Replace problematic characters or patterns
    json_string = re.sub(r'\\+', r'\\', json_string)  # Fix excessive backslashes
    json_string = re.sub(r'“|”', r'"', json_string)   # Replace fancy quotes with standard quotes
    json_string = re.sub(r'\s+', ' ', json_string)    # Replace excessive whitespace
    json_string = json_string.strip()                # Strip leading/trailing whitespace
    return json_string

def string_to_json(json_string):
    """
    Converts a JSON string into a Python dictionary.

    Args:
        json_string (str): The JSON string to parse.

    Returns:
        dict: The parsed JSON object if valid, or None if invalid.
    """
    logger.info("Inside string_to_json function")
    try:
        # Parse the JSON string into a Python object
        logger.info("Attempting to parse JSON string into a Python dictionary")
        json_object = json.loads(json_string)
        logger.info("Successfully converted JSON string to a dictionary")
        return json_object
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON string: {e}")
        return None


def get_chunks_for_document(query,num_of_chunks,filtered_data,headers):
    try:
        url = 'https://dev.ce.vassardigital.ai/api/chatbot/sme/chunks'

        # headers=get_header('9a2f0f2e-7260-47ff-8403-98104657078e','047cab49-538c-4bcd-a56d-440b35b4e0c3', '39887cfc-fb15-4180-ba0a-06f35f76a424')
        headers = get_header(
            customer_uuid = headers.get('Customer-Uuid',None),
            application_uuid = headers.get('Application-Uuid',None),
            user_uuid= headers.get('User-Uuid',None),
            csrf_token = headers.get('Csrf-Token',None),
            authorization= headers.get('Authorization',None)
        )

        json = {
            'query': query,
            'entity_filter': filtered_data,
            'top_n': num_of_chunks,
            'metadata_keys': ['source', 'pages', 'entity_name', 'Document Name', 'document_id','Project ID']
        }

        response = requests.post(url=url, json=json, headers=headers)
        chunks = response.json()['result']
        return chunks
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Chunks From Document: {e}"

def llm_call(text):
    # llm call for clauses
    llm_chain = LLMChain(llm=llm, prompt=format_text_prompt, verbose=True)
    response = gpt_call(llm_chain, {'text': text})
    print("Responses after text formater prompt called::", response)
    return response


def extract_guidelines(chunks):
    try:
        extracted_clauses = []
        relevent_chunks = []
        checked=0
        for i in range(0, len(chunks),10):  # Step size of 5
            if checked > len(chunks):
                break
            chunk_batch = chunks[i:i + 20]  # Slicing the next 20 chunks
            context_chunks = []
            current_chunks = []
            if i == 0:
                for each_chunk in chunk_batch:
                    print("for i=0")
                    current_chunks.append({
                        "chunk_id": each_chunk["id"],
                        "document": each_chunk["document"],
                        "Document Name": each_chunk["metadata"]["Document Name"],
                        "Page No": each_chunk["metadata"]["pages"],

                    })
                    checked=20
            else:
                # Split the chunk_batch into two parts
                mid_index = len(chunk_batch) // 2

                context_chunk_chunk_batch = chunk_batch[:mid_index]  # First half as context_chunks
                context_chunks=[]
                #preparing context chunks
                for each_chunk in context_chunk_chunk_batch:
                    context_chunks.append({
                        "chunk_id": each_chunk["id"],
                        "document": each_chunk["document"],
                        "Document Name": each_chunk["metadata"]["Document Name"],
                        "Page No": each_chunk["metadata"]["pages"],

                    })
                current_batch_chunks = chunk_batch[mid_index:]  # Second half as current_chunks
                current_chunks=[]
                # preparing
                for each_chunk in current_batch_chunks:
                    current_chunks.append({
                        "chunk_id": each_chunk["id"],
                        "document": each_chunk["document"],
                        "Document Name": each_chunk["metadata"]["Document Name"],
                        "Page No": each_chunk["metadata"]["pages"],
                    })
                checked=i+20
            prompt = clause_prompt
            print("calling prompt")
            #llm call for clauses
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
            response = gpt_call(llm_chain, {'chunks': current_chunks,'context':context_chunks})
            print("Responses::", response)
            response = extract_json_from_string(response)
            print("Responses after extracting json::", response)
            print("Responses after extracting::", response)
            if response is not None:
                response = string_to_json(response)
                extracted_clauses.extend(response["clauses"])
        print("extracted_clauses",extracted_clauses)

        # # Function to remove duplicates based on the 'clause' field
        # def remove_duplicates(clauses):
        #     unique_clauses = []
        #     seen_clauses = set()
        #
        #     for clause in clauses:
        #         if clause['clause'] not in seen_clauses:
        #             unique_clauses.append(clause)
        #             seen_clauses.add(clause['clause'])
        #
        #     return unique_clauses

        # Call the function to remove duplicates
        #unique_clauses = remove_duplicates(extracted_clauses)
        # for clause in unique_clauses:
        #     if clause["type_of_clause"] != "Consultant_Clause":
        #         unique_clauses.remove(clause)
        matching_data = []
        # return unique_clauses
        for clause in extracted_clauses:
            for toc in chunks:
                if clause["chunk_id"] == toc["id"] and clause["type_of_clause"]== "Consultant_Clause":
                    print("chunk data",toc["document"])
                    if not any(item["id"] == toc["id"] for item in matching_data):
                        print("each toc::",toc)
                        print("Meta data::",toc.get('metadata',None))
                        # res= check_call(toc["document"])
                        # print("res::",res)
                        # if res=="TRUE" or res=="true" :
                        matching_data.append({
                            "id": toc["id"],
                            "clause": llm_call(toc["document"]),
                            "type_of_clause":clause["type_of_clause"],
                            #"reason_for_clause":clause["reason_for_clause"],
                            "independent": clause["independent"],
                            #"reason":clause["reason"],
                            "references": {toc["metadata"]["source"],
                                           toc["metadata"]["pages"]
                                           }
                    })
        print("matching data 1::",matching_data)
        return matching_data
        # for txt in matching_data:
        #     text=txt["clause"]
        #     # llm call for clauses
        #     llm_chain = LLMChain(llm=llm, prompt=CLAUSE_CLASSIFICATION_PROMPT, verbose=True)
        #     response = gpt_call(llm_chain, {'clause': text})
        #     print("Responses clause::", response)
        #     if response == "Consultant_Clause":
        #         txt["type_of_clause"]=response
        #     else:
        #         print("removing::",txt)
        #         matching_data.remove(txt)
        # print("matching_data", matching_data)
        # return matching_data



    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}"


def retrieve_data_from_vectordb(chroma_client,query,collection_name='doe_guidelines'):
    collection = chroma_client.get_collection(name=collection_name)

    # Generate the embedding for the query
    query_embedding = embeddings.embed_query(query)

    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5  # Number of top results to retrieve
    )

    result_str =""
    for i in range(5):
        result_str += results['documents'][0][i]+"-- "+results['ids'][0][i]
        result_str += "\n"


    print("DEBUG: Vector String::",result_str)
    return result_str

def update_document_in_vectordb(chroma_client, doc_id, extra_metadata=None, collection_name="doe_guidelines"):
    """
    Updates metadata or document in the ChromaDB collection.
    :param chroma_client: ChromaDB client instance
    :param doc_id: ID of the document to update
    :param updated_metadata: New metadata to update (optional)
    :param updated_document: New document text to update (optional)
    :param collection_name: Name of the collection
    :return: Status message
    """
    try:
        # Fetch the collection
        collection = chroma_client.get_or_create_collection(name=collection_name)

        # Retrieve the existing document
        existing_data = collection.get(ids=[doc_id])
        if not existing_data["ids"]:
            return f"Document with ID '{doc_id}' does not exist in the collection."

        # Extract existing values
        existing_metadata = existing_data["metadatas"][0] if "metadatas" in existing_data else {}
        existing_document = existing_data["documents"][0]

        embedding = embeddings.embed_query(existing_document)
        print("DEBUG:: Existing Data::",existing_data)


        # Merge updated values with existing ones
        reference_metadata = json.loads(existing_metadata['reference'])
        print("Metadata reference::",reference_metadata)
        print("Type of Metadata reference::",type(reference_metadata))

        if extra_metadata != None:
            print("Extra Metadata reference::",extra_metadata)
            print("Type of Extra Metadata reference::",type(extra_metadata))
            reference_metadata.append(extra_metadata)

        metadata_str = json.dumps(reference_metadata)

        print("DEBUG:: Metadata String",metadata_str)
        existing_metadata['reference'] = metadata_str

        # Delete the old entry
        collection.delete(ids=[doc_id])

        # Re-add the updated document
        collection.add(
            embeddings=[embedding],
            metadatas=[existing_metadata],
            documents=[existing_document],
            ids=[doc_id]
        )
        return f"Document with ID '{doc_id}' updated successfully."

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error updating document: {e}"

def add_clauses_to_chroma_db(chroma_client,clauses,collection_name='doe_guidelines'):
    try:
        print("DEBUG: Inside Add Data To Vector DB")
        collection = chroma_client.get_or_create_collection(name=collection_name)

        print("DEBUG: Items are getting Added")
        for item in clauses:
            # Generate the embedding for the clause
            embedding = embeddings.embed_query(item['clause'])
            # print("Enbeddings::",embedding)

            # Convert the reference dictionary to a JSON string
            print("11111111111111")
            reference_str = json.dumps(item["reference"])
            print("22222222222222222222222")

            # Add the item to the collection
            collection.add(
                embeddings=[embedding],  # Ensure this is a list
                metadatas={
                    "type_of_clause": item.get("type_of_clause",None),
                    "reference": reference_str,  # Store reference as a JSON string
                    "id":item.get("chunk_id",None)
                },
                documents=[item["clause"]],  # Ensure this is a list
                ids=[str(uuid.uuid4())]  # Ensure this is a list
            )
        print("DEBUG: Items are get Added")
        return "Data Added to Vector DB"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Adding Clauses To Chroma DB: {e}"

def check_deduplication(clauses, client):
    try:
        non_duplicate_clauses = []
        for clause in clauses:
            # 5 similar clauses will fetch from the vector db
            response = retrieve_data_from_vectordb(client, query=clause['clause'])
            prompt = de_duplicate_prompt
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
            response = gpt_call(llm_chain, {'guidelines': response, 'clause': clause['clause']})
            response = extract_json_from_string(response)
            response = string_to_json(response)
            print("Flag::", response['duplicate_guideline'])

            if response['duplicate_guideline'] == 'True':
                print("Duplicate Guidelines Id::", response["matching_guideline_id"])
                response = update_document_in_vectordb(chroma_client=client,
                                                       doc_id=response["matching_guideline_id"],
                                                       extra_metadata=clause["reference"]
                                                       )
            else:
                non_duplicate_clauses.append(clause)
        if non_duplicate_clauses:
            print("adding the non duplicate clause into db")
            add_clauses_to_chroma_db(client, non_duplicate_clauses)
        return "Checked For De Duplication and the clauses added to DB"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}"
    
def get_doe_clauses():
    try:
        # API to fetch Chroma DB clauses
        collection_name = 'doe_guidelines'
        chroma_client = chromadb.PersistentClient(path=storage_path_chroma)
        collection = chroma_client.get_or_create_collection(name=collection_name)

        clauses_data = collection.get()
        length_of_clauses = len(clauses_data["ids"])
        response = []
        for i in range(length_of_clauses):
            current_element = {}
            current_element["id"] = clauses_data["ids"][i]
            current_element["clause"] = clauses_data["documents"][i]
            current_element["type_of_clause"] = clauses_data["metadatas"][i]['type_of_clause']
            current_element["references"] = json.loads(clauses_data["metadatas"][i]['reference'])
            current_element["chunk_id"] = clauses_data["metadatas"][i]["id"]
            response.append(current_element)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}"
    
@retry(retry=retry_if_exception_type(RateLimitError), stop=stop_after_attempt(3),
           wait=wait_fixed(25))
def response_from_llm(clause,refactored_docs,requirements):
    try:
        llm_chain = LLMChain(llm=llm, prompt=evaluation_prompt, verbose=True)
        response = gpt_call(llm_chain,{'chunks':refactored_docs,'clause':clause,'requirements':requirements})
        response = extract_and_clean_json(response)
        response = string_to_json(response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}" 
    except RateLimitError as e:
        raise e
    except APITimeoutError as e:
        raise RateLimitError(response=httpx.Response(status_code=504), message=str(e), body="")        


@retry(retry=retry_if_exception_type(RateLimitError), stop=stop_after_attempt(3),
           wait=wait_fixed(25))
def response_from_llm_for_relevant_chunks(clause,chunks):
    try:
        llm_chain = LLMChain(llm=llm, prompt=relevant_chunks_prompt, verbose=True)
        response = gpt_call(llm_chain,{'chunks':chunks,'clause':clause})
        response = extract_and_clean_json(response)
        response = string_to_json(response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}" 
    except RateLimitError as e:
        raise e
    except APITimeoutError as e:
        raise RateLimitError(response=httpx.Response(status_code=504), message=str(e), body="")        



def response_from_decomposition(clause):
    try:
        llm_chain = LLMChain(llm=llm, prompt=query_decomposition_prompt, verbose=True)
        response = gpt_call(llm_chain,{'question':clause})
        response = extract_and_clean_json(response)
        response = string_to_json(response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}" 

@retry(retry=retry_if_exception_type(RateLimitError), stop=stop_after_attempt(3),
           wait=wait_fixed(25))
def response_from_llm_for_initial_answer(data):
    try:
        llm_chain = LLMChain(llm=llm, prompt=initial_answer_prompt, verbose=True)
        response = gpt_call(llm_chain,{'chunks':data['relevant_chunks'],'clause':data['clause']})
        response = extract_and_clean_json(response)
        response = string_to_json(response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}"
    except RateLimitError as e:
        raise e
    except APITimeoutError as e:
        raise RateLimitError(response=httpx.Response(status_code=504), message=str(e), body="")        

@retry(retry=retry_if_exception_type(RateLimitError), stop=stop_after_attempt(3),
           wait=wait_fixed(25))
def response_from_llm_for_references(external_references,question):
    try:
        llm_chain = LLMChain(llm=llm, prompt=external_reference_prompt, verbose=True)
        response = gpt_call(llm_chain,{'standards':external_references,'question':question})
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}"
    except RateLimitError as e:
        raise e
    except APITimeoutError as e:
        raise RateLimitError(response=httpx.Response(status_code=504), message=str(e), body="")        

    
@retry(retry=retry_if_exception_type(RateLimitError), stop=stop_after_attempt(3),
           wait=wait_fixed(25))
def response_from_llm_for_external_standards(question, answer, references):
    try:
        llm_chain = LLMChain(llm=llm, prompt=external_standards_prompt, verbose=True)
        response = gpt_call(llm_chain,{'question':question,'answer':answer,'references':references})
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
        return f"Error Fetching Clauses From Chunks: {e}" 
    except RateLimitError as e:
        raise e
    except APITimeoutError as e:
        raise RateLimitError(response=httpx.Response(status_code=504), message=str(e), body="")        



