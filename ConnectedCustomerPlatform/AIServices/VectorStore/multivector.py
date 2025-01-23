# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.prompts import ChatPromptTemplate
# from langchain_core.documents import Document
# from langchain_core.output_parsers import StrOutputParser
# from langchain.vectorstores import Chroma
# # from Url_ChatBot_App.models import Documents
# import chromadb
# from chromadb.config import Settings
# from BOT.LLM.llm_chain import embeddings, gpt4_llm
# from PDFChatbot.Constants.constants import TEMP_FOLDER
# import json
# from datetime import datetime

# class MultiVectorRetriever():
    
#     def __init__(self):
        
#         self.client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
#         self.id_key = 'doc_id'
#         self.k = 15

#     def generate_child_chunks(self, docs, doc_ids, chunk_size):
        
#         child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size)
#         child_docs = []
        
#         for i in range(len(docs)):
#             doc = docs[i]
#             id = doc_ids[i]
#             sub_docs = child_text_splitter.split_documents([doc])
#             for sub_doc in sub_docs:
#                 sub_doc.metadata[self.id_key] = id
#             child_docs.extend(sub_docs)
        
#         return child_docs
    
#     def generate_summaries(self, docs, doc_ids):
        
#         chain = ({"doc": lambda x: x.page_content, "source" : lambda x: x.metadata['source']}
#         | ChatPromptTemplate.from_template("Summarize the following document.\
#         The documents are about door installation manuals, so the summaries should be generated accordingly.\
#         The summaries should also include the heading and sub-headings which are the first line of the document.\
#         The source of the document  given below should be a part of the summary.\n\ndocument : {doc}\nsource : {source}")
#         | gpt4_llm
#         | StrOutputParser())

#         summaries = chain.batch(docs, {"max_concurrency": 5})
#         summary_docs = [
#             Document(page_content=s, metadata={self.id_key: doc_ids[i]})
#             for i, s in enumerate(summaries)
#         ]
#         return summary_docs

#     def generate_hypothetical_questions(self, docs, doc_ids, n):
    
#         functions = [
#             {
#                 "name": "hypothetical_questions",
#                 "description": "Generate hypothetical questions",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "questions": {
#                             "type": "array",
#                             "items": {"type": "string"},
#                         },
#                     },
#                     "required": ["questions"],
#                 },
#             }
#         ]

#         from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

#         chain = (
#         {"doc": lambda x: x.page_content, "source" : lambda x: x.metadata['source']}
#         | ChatPromptTemplate.from_template(
#         "Generate a list of exactly 3 hypothetical questions that the below document could be used to answer.\
#         The generated questions should not be specific to any one part of the document, it should encapsulate\
#         all the content of the document. Use the headers and sub-headers to do this.\
#         The documnets are about a door installation manual, questions should be accordingly.\
#         The questions generated should also include the headings and sub-headings in the document which\
#         are in the first line of the document. It should also include the\
#         source of the document given below. In case of the documents which are listing the `contents` of a heading\
#         the questions should be only on the heading and not the contents,\
#         eg: what are the steps/contents of the <heading> of the <source>:\n\ndocument : {doc}\n\nsource : {source}")
#         | gpt4_llm.bind(
#         functions=functions, function_call={"name": "hypothetical_questions"})
#         | JsonKeyOutputFunctionsParser(key_name="questions")
#         )

#         hypothetical_questions = chain.batch(docs, {"max_concurrency": 5})
#         question_docs = []
#         for i, question_list in enumerate(hypothetical_questions):
#             question_docs.extend(
#             [Document(page_content=question, metadata={self.id_key: doc_ids[i]}) for question in question_list]
#             )
#         return question_docs
    
#     def create_vectorstore(self, connection_id, collection_name, docs):
        
#         documents = []
#         for i in range(len(docs)):
#             documents.append(Documents(
#                 connection_id = connection_id,
#                 content = docs[i].page_content,
#                 metadata = docs[i].metadata
#             ))
#         Documents.objects.bulk_create(documents)
        
#         ids = Documents.objects.filter(connection_id=connection_id).values_list('id')
#         ids = [ id[0] for id in ids ]
#         print(ids)
        
#         store_docs = []
#         # print('generating child docs................')
#         # store_docs.extend(self.generate_child_chunks(docs, ids, 400))
#         print('generating summary docs................')
#         summary_docs = self.generate_summaries(docs, ids)
#         summary_obj = {}
#         for d in summary_docs:
#             summary_obj[d.metadata[self.id_key]] = d.page_content
#         #json.dump(summary_obj, open(TEMP_FOLDER + 'summ_' + str(datetime.now()) + '.json', 'x'))
#         store_docs.extend(summary_docs)
        
#         print('generating question docs................')
#         question_docs = self.generate_hypothetical_questions(docs, ids, 3)
#         question_obj = {}
#         for d in question_docs:
#             question_obj[d.metadata[self.id_key]] = d.page_content
#         #json.dump(question_obj, open(TEMP_FOLDER + 'hque_' + str(datetime.now()) + '.json', 'x'))
#         store_docs.extend(question_docs)
        
#         doc_map = {}
#         for i in range(len(ids)):
#             id = ids[i]
            
#             questions = []
#             for j in range(3):
#                 questions.append(question_docs[(i*3)+j].page_content)

#             doc_map[id] = {
#                 'parent' : {
#                     'content' : docs[i].page_content,
#                     'metadata' : docs[i].metadata   
#                 },
#                 'summary' : summary_docs[i].page_content,
#                 'questions' : questions
#             }
#         #json.dump(doc_map, open(TEMP_FOLDER + str(datetime.now()) + '.json', 'x'))
        
#         self.client.get_or_create_collection(collection_name)
        
#         vectorstore = Chroma(client=self.client, collection_name=collection_name,
#                              embedding_function=embeddings)
#         vectorstore.add_documents(store_docs)
        
#     def get_relevant_documents(self, collection_name, query):
        
#         collection = self.client.get_collection(collection_name)
#         count = collection.count()
        
#         vectorstore = Chroma(client=self.client, collection_name=collection_name,
#                              embedding_function=embeddings)
#         sub_docs = vectorstore.similarity_search(query, count)
        
#         print('similar hypothetical docs : ')  
#         print('*************************************')
#         for sub_doc in sub_docs[:10]:
#             print(sub_doc.page_content,sub_doc.metadata)
#         print('*************************************')
        
#         ids = set()
#         id_order = []
        
#         for sub_doc in sub_docs:
        
#             id = sub_doc.metadata[self.id_key]
#             if id not in ids:
#                 ids.add(id)
#                 id_order.append(id)
        
#         documents = []
#         for id in id_order[:self.k]:
#             documents.append(Documents.objects.filter(id = id).first())
        
#         relevant_docs = [Document(page_content=document.content, metadata=document.metadata) for document in documents]
#         return relevant_docs