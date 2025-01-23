
# from BOT.LLM import embeddings, gpt4_llm
# from BOT.prompts import hyde_prompt
# from PDFChatbot.models import Documents
# from PDFChatbot.Constants.constants import *

# from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
# from langchain.document_loaders import PyMuPDFLoader, TextLoader, CSVLoader, UnstructuredWordDocumentLoader
# from langchain.docstore.document import Document
# # from langchain.vectorstores import FAISS

# from pgvector.django import L2Distance, CosineDistance, MaxInnerProduct

# # from datetime import datetime
# import json

# from langchain.vectorstores import MongoDBAtlasVectorSearch, Chroma

# from pymongo import MongoClient

# from langchain.chains.query_constructor.base import AttributeInfo
# from langchain.retrievers.self_query.base import SelfQueryRetriever
# from langchain.chains import HypotheticalDocumentEmbedder, LLMChain


# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')




# class PGVectorStore:

# 	def __init__(self, k, distance):
# 		self.k = k
# 		if(distance == "cosine"):
# 			self.distance = CosineDistance
# 		elif(distance == "euclidean"):
# 			self.distance = L2Distance
# 		else:
# 			self.distance = MaxInnerProduct
# 		self.text_splitter =  CharacterTextSplitter(separator="\n",
#                                           chunk_size=CHUNK_SIZE,
#                                           chunk_overlap=CHUNK_OVERLAP,
#                                           length_function=len,
#                                           is_separator_regex=False)
		
# 		self.hyde_chain = LLMChain(llm=gpt4_llm, prompt=hyde_prompt)
		
# 		self.hyde_embeddings = HypotheticalDocumentEmbedder(llm_chain=self.hyde_chain, base_embeddings=embeddings)

		
# 		# self.vector_search = MongoDBAtlasVectorSearch.from_connection_string(
# 		# 	MONGODB_ATLAS_CLUSTER_URI,
# 		# 	DB_NAME + "." + COLLECTION_NAME,
# 		# 	embeddings,
# 		# 	index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
# 		# )
# 		# self.qa_retriever = self.vector_search.as_retriever(
# 		# 						search_type="similarity",
# 		# 						search_kwargs={"k": self.k},
# 		# 					)
		
# 		# self.db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 		# self.metadata_field_info = []

# 		# self.retriever = SelfQueryRetriever.from_llm(
# 		# 	gpt4_llm, self.db, document_content_description, self.metadata_field_info, verbose=True, search_kwargs = {'k' : self.k}
# 		# )


# 	def create_from_files(self, files, conn_id, text_rag_folder):
# 		chunks = []
# 		for file in files:
# 			if file.endswith('.csv'):
# 				csv_loader = CSVLoader(file)

# 				csv_data = csv_loader.load()
# 				csv_data_chunks = self.text_splitter.split_documents(csv_data)
# 				for i in range(len(csv_data_chunks)):
# 					csv_data_chunks[i].metadata['Source'] = ''
# 					csv_data_chunks[i].metadata['Pages'] = ''
# 				chunks.extend(csv_data_chunks)
				
# 			elif file.endswith('.docx'):
# 				unstruc_loader = UnstructuredWordDocumentLoader(file)

# 				unstruc_data = unstruc_loader.load()
# 				unstruc_data_chunks = self.text_splitter.split_documents(unstruc_data)
# 				chunks.extend(unstruc_data_chunks)
				
# 			elif file.endswith('pdf'):
# 				pdf_loader = PyMuPDFLoader(file)
				
# 				pdf_data = pdf_loader.load()
# 				pdf_data_chunks = self.text_splitter.split_documents(pdf_data)
# 				chunks.extend(pdf_data_chunks)

		
# 		# vectorstore = FAISS.from_documents(chunks, embeddings)
# 		# vectorstore.save_local(text_rag_folder)

# 		contents = [ chunk.page_content for chunk in chunks ]
# 		metadatas = [ chunk.metadata for chunk in chunks ]
# 		# print(chunks[:1])

# 		chunk_embeddings = embeddings.embed_documents(contents)

# 		# print(chunk_embeddings[:1])

# 		docs = [ Documents(
# 				connection_id = conn_id, 
# 				content = contents[i], 
# 				metadata = metadatas[i],
# 				embedding = chunk_embeddings[i]
# 			) for i in range(len(chunks)) ]
		
# 		# print(docs[0], len(docs))
# 		# print("start")
# 		Documents.objects.bulk_create(docs)
# 		# print("done")

# 	def create_from_json(self, file, conn_id, rag_folder):
     
# 		with open(file) as jsonfile:
# 			data = json.load(jsonfile)

# 		source = file.split('/')[-1]
# 		data = json.load(open(file))
# 		blocks = data['elements']

# 		text = ""
# 		chunks = []
# 		pages = set()
# 		metadata = {'Source' : source, "H1": "", "H2": "", "H3": "", "Pages": set()}
# 		h1 = ""
# 		h2 = ""
# 		h3 = ""
# 		headers = []

# 		for block in blocks:
			
# 			if "Path" not in block or "Text" not in block:
# 				continue
			
# 			block_path = block['Path']
# 			block_text = block['Text']
# 			block_page = block['Page'] + 1
			
# 			if block_page == 2:
# 				continue

# 			if block_path.find('Title') != -1:
# 				continue
			
# 			elif block_path.find("H1") != -1:
# 				headers.append({'type' : 'H1', 'text' : block_text})
# 				if text:
# 					metadata['Pages'] = list(pages)
# 					chunks.append((text, metadata.copy()))
# 				pages = set() 
# 				pages.add(block_page)
# 				h1 = block_text
# 				h2 = ""
# 				h3 = ""
# 				text =  h1 + '\n'
# 				metadata = {"H1" : h1, "Source" : source}
			
# 			elif block_path.find('H2') != -1:
# 				headers.append({'type' : 'H2', 'text' : block_text})
# 				h2 = block_text
# 				h3 = ""
# 				text += h1 + ', ' + h2 + '\n'
# 				pages.add(block_page)
			
# 			elif block_path.find('H3') != -1:
# 				headers.append({'type' : 'H3', 'text' : block_text})
# 				h3 = block_text
# 				text += h1 + ', ' + h2 + ', ' + h3 +  '\n'
# 				pages.add(block_page)
			
# 			else:
# 				text += block_text
# 				pages.add(block_page)
# 				if len(text) > CHUNK_SIZE:
# 					metadata['Pages'] = list(pages)
# 					chunks.append((text, metadata.copy()))
# 					text =  h1 + ', ' + h2 + ', ' + h3 + '\n'
# 					pages = set()

# 		chunks.append((text, metadata.copy()))

# 		contents_chunks = []
# 		contents_text = ""
# 		contents_metadata = {'Source' : source, 'Pages' : [2], "H1": "Table of Contents", "H2": "", "H3": "",}

# 		for header in headers:
			
# 			if header['type'] == 'H1':
# 				if contents_text:
# 					contents_chunks.append((contents_text, contents_metadata.copy()))
# 				contents_text = header['text'] + '\n'
# 			elif header['type'] == 'H2':
# 				contents_text += '\t' + header['text'] + '\n'
# 			else:
# 				contents_text += '\t\t' + header['text'] + '\n'
			
# 		contents_chunks.append((contents_text, contents_metadata.copy()))

# 		contents = []
# 		metadatas = []

# 		for chunk in contents_chunks:
# 			page_content, metadata = chunk
# 			contents.append(page_content)
# 			metadatas.append(metadata)

# 		for chunk in chunks:
# 			page_content, metadata = chunk
# 			contents.append(page_content)
# 			metadatas.append(metadata)

# 		chunk_embeddings = embeddings.embed_documents(contents)
		
# 		heading1 = list(set([ metadatas[i]['H1'] for i in range(len(metadatas))]))

# 		for i in range(len(metadatas)):
# 			metadatas[i]['Pages'] = str(metadatas[i]['Pages'])

# 		docs = [ Document(page_content=contents[i], 
# 						metadata=metadatas[i]
# 				   ) for i in range(len(chunks)) ]
		
# 		self.metadata_field_info = [
# 				AttributeInfo(
# 					name="H1",
# 					description=f"The heading of the section must be one for the following {heading1}",
# 					type="string",
# 				),  
# 		]

# 		# self.db = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db", collection_metadata={"hnsw:space": "cosine"})

# 		# self.retriever = SelfQueryRetriever.from_llm(
# 		# 	gpt4_llm, self.db, document_content_description, self.metadata_field_info, verbose=True, search_kwargs = {'k' : self.k}
# 		# )
# 		# chunk_embeddings = embeddings.embed_documents(contents)
# 		# meta_embeddings = embeddings.embed_documents(str_metas)
# 		docs = [ Documents(
# 				connection_id = conn_id, 
# 				content = contents[i], 
# 				metadata = metadatas[i],
# 				embedding = chunk_embeddings[i],
# 				# metadata_embedding = meta_embeddings[i]
# 			) for i in range(len(chunks)) ]

# 		Documents.objects.bulk_create(docs)

# 	def get_relevant_documents(self, query, conn_id, get_next, num = 10):
# 		# docs = self.qa_retriever.get_relevant_documents(query=query)
# 		# docs = self.db.similarity_search_with_score(query, k=self.k)#, where_document={"$contains":query})
		
# 		# docs = self.retriever.get_relevant_documents(query=query)
# 		# docs = self.vector_search.similarity_search(query=query)
# 		# for i in range(len(docs)):
# 		# 	docs[i].metadata['source'] = docs[i].metadata['Source'] + " Page: " + docs[i].metadata['Pages']

# 		# print("****************************** docs ")
# 		# # print(docs)
# 		# for i in range(len(docs)):
# 		# 	print("Document : ", i + 1)
# 		# 	print(docs[i].page_content[:400])
# 		# 	print(docs[i].metadata)
# 		# 	print()
# 		# print("******************************")
# 		# print()
# 		# return docs

# 		# embedding = self.hyde_embeddings.embed_query(query)
# 		print(query, get_next)
# 		n = num
# 		if(get_next):
# 			n += self.k
# 		embedding = embeddings.embed_query(query)
# 		docs = Documents.objects.filter(
# 			connection_id=conn_id
# 		).values("content", "metadata", "id").order_by(self.distance('embedding', embedding))[:n]


# 		# id_list = [ doc['id'] for doc in docs ]
# 		# md_docs = Documents.objects.filter(
# 		# 	connection_id=conn_id
# 		# ).exclude(id__in=id_list).values("content", "metadata", "id").order_by(self.distance('metadata_embedding', embedding))[:self.k]


# 		formatted_docs = [ Document(page_content=docs[i]['content'], 
# 							  metadata={"source": f"{docs[i]['metadata']['Source'].split('/')[-1]}, Page: {docs[i]['metadata'].get('Pages', '')}"}
# 				   ) for i in range(n - self.k, len(docs)) ]
		
# 		print("****************************** docs ")
# 		# print(docs)
# 		for i in range(len(formatted_docs)):
# 			print("Document : ", i + 1)
# 			print(formatted_docs[i].page_content)
# 			print()
# 		print("******************************")
# 		print()
		
# 		# formatted_docs_md = [ Document(page_content=doc['content'], 
# 		# 					  metadata={"source": f"{doc['metadata']['source'].split('/')[-1]}, Page: {doc['metadata'].get('page', '')}"}
# 		# 		   ) for doc in md_docs ]

# 		# print("****************************** metadata ")
# 		# # print(docs)
# 		# for i in range(len(formatted_docs_md)):
# 		# 	print("Document : ", i + 1)
# 		# 	print(formatted_docs_md[i].page_content[:400])
# 		# 	print()
# 		# print("******************************")
		
# 		# formatted_docs.extend(formatted_docs_md)

# 		# docs2 = Documents.objects.filter(
# 		# 	connection_id=conn_id
# 		# ).values("content")
# 		# for i in range(len(docs2)):
# 		# 	print("Document 1")
# 		# 	print(docs2[i]['content'][:500])
# 		# 	print()

# 		return formatted_docs
