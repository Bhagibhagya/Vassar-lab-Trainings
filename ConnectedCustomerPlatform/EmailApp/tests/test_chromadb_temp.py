from AIServices.VectorStore.chromavectorstore import chroma_obj
#from EmailApp.utils import get_chroma_collection_name_by_customer_application,get_latest_n_emails_and_responses
def test1():
    #print(get_chroma_collection_name_by_customer_application(customer_uuid='52143feb-ca8a-4e96-94d5-3e49c50372e4',application_uuid='725e005e-40a2-450f-9dab-e72903a63af1'))
    #print(chroma_obj.get_emails_by_metadata(metadata_combination=[],collection_name=get_chroma_collection_name_by_customer_application(customer_uuid='5e9ae945-c009-406a-a112-28d274589db4',application_uuid='a26a2650-19f8-49de-a6e5-7aa73841acb0')))
    print(chroma_obj.delete_older_response(metadata=[],collection_name='email_6452d57e-1627-4c8a-91e7-0d364a28e07f',no_of_responses_to_store=0))
    # print(get_latest_n_emails_and_responses(chroma_output,3))
    
test1()
print("ok")