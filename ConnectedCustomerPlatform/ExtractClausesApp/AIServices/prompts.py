from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate
)
CLAUSE_PROMPT = """
    You are a legal expert in identifying the key guidelines and clauses that a consultant or contractor needs to meet as per Department of Energy (DoE) guidelines based on the document CHUNKS. Please analyse all the CHUNKS and give a list of clauses that the contractor needs to meet. 

    - These clauses are typically referred to with words such as ‘must’, ’shall’ or ‘will’ or similar words. 
    - Each clause should be a complete stand alone clause with sentence starting with Contractor much/shall/will etc.
    - Include all the clauses including from the main documents and attachments 
    - include all clauses, do not merge them or summarise
    - Give QAP and QAC clauses under different headings 
    - If there are no clauses in chunks, return empty list 

    DISPLAY: Ensure that the output is in the following JSON format exactly as shown:
        {{
            [
                {{
                    "clause": "[particular_clause]",
                    "type_of_clause":"[type can be QAP/QAC]",
                    "reference":{{
                        "Page No":"[page no of the particular clause]",
                        "File Name":"[file name for the clause]"
                    }}
                }}
            ]
        }}

    chunks: {chunks}

"""

DEDUPLICATION_PROMPT = """
    You are given with few Standard DOE Guideline clauses and one new DOE Guideline clause to be added. 
    Your task is to check whether the new DOE Guideline is already present in the given Standard DOE Guidelines.

    DISPLAY: Ensure that the output is in the following JSON format exactly as shown:
        {{
        "duplicate_guideline":"[True/False]",
        "matching guideline id":"[id Of matching DOE Guideline e.g. 2e4cdfbd-3365-2339-8d49-03e67377b6bf]"
        }}


    Standard DOE Guidelines:{guidelines}

    New Clause: {clause}

"""

EVALUATION_PROMPT = """
    You are a contract evaluation specialist. Please see if the following CLAUSE is being met by the customer through CHUNKS of customer docs.
    Based on CLAUSE and CHUNKS, you have to set the compliance_status to True or False i.e. whether the clause is being followed by the customer or not.

    DISPLAY: Ensure that the output is in the following JSON format exactly as shown:
        {{
        "compliance_status":"[True/False]"
        }}

    CLAUSE:{clause}

    CHUNKS:{chunks}
"""

REVISED_CHUNKS_EXTRACTION_PROMPT = """
    You are a legal expert responsible for identifying clauses that a consultant or contractor must meet, that are defined by an authority
    called Department of Energy (DoE) who have CLAUSES outlined in the provided CURRENT_CHUNKS. Your task is to analyze all the CURRENT_CHUNKS and
    extract a list of CURRENT_CHUNKS that specifically focus on the QUANTITATIVE CLAUSES  related to contractor assurance,
    oversight, compliance, and performance expectations for contractors.
    These clauses will be used to assess the contractor's or consultant's completed work.

    Instructions:
        1. Only include QUANTITATIVE CLAUSE that explicitly state the responsibilities or requirements that needs to be completed by a contractor.
        2. These CURRENT_CHUNKS do contain some clauses that Department of Energy (DOE) has to follow and not the contractor. 
            - We should strictly should not retrieve the chunks that Department of Energy (DOE) needs to follow. These contains headings and words like 
                e.g. "OBLIGATIONS, RESPONSIBILITIES, OR IMPLEMENTATION REQUIREMENTS
                      ON THE DEPARTMENT OF ENERGY (DOE) OR ITS DEPARTMENTS, SUCH AS STATEMENTS LIKE 'DOE ORGANIZATION MUST HAVE...'
                      OR 'DOE LINE MANAGEMENT MUST HAVE...'" 
            - Only retrieve the chunks that specifically tells us about the clause that the contractor should follow.
        3. QUANTITATIVE CLAUSE typically use words such as 'must', 'shall', 'will', or similar terms.
        4. Each extracted QUANTITATIVE CLAUSE should:
            - Be a complete and standalone sentence, starting with the consultant's or contractor’s obligations
              (e.g., "Contractor must...", "Consultant shall...", "Contractor will...").
            - Exclude any clauses that do not specifically assign responsibility to the contractor or consultant.
        5. Carefully review ALL CURRENT_CHUNKS, including main documents and attachments that will be used to extract QUANTITATIVE CLAUSE.
        6. Do not merge or summarize the QUANTITATIVE CLAUSES; list them as they appear.
        7. Classify each clause as either QAP (Quality Assurance Plan) or QAC (Quality Assurance Criteria).
        8. If no relevant QUANTITATIVE CLAUSES are found in the CURRENT_CHUNKS, return an empty list.
        9. For "independent" classification:
            - For each clause:
                - If the QUANTITATIVE CLAUSE references something else (e.g., "See Attachment A," "Refer to Section 2.3,"
                  "to meet the requirements of this Order"), set `"independent": false`.
                - If the QUANTITATIVE CLAUSE does not reference any external material, set `"independent": true`.
    
    DISPLAY: Ensure the output follows the exact JSON format shown below:
    {{
        "relevant_chunks": [
            {{
                "chunk_id": "ID of the referenced chunk",
                "chunk": "data of the chunk 'document' key data. Do not change any thing in that particular chunk",
                "page no": "Page number of that particular chunk",
                "pdf name": "PDF Name of the that chunk"
            }},
        ]
    }}
    
    Remember : 
    - Extract QUANTITATIVE CLAUSES only from the provided CURRENT_CHUNKS (NOT from the PREVIOUS_CHUNKS). 
    - The PREVIOUS_CHUNKS only provides the context for the CURRENT_CHUNKS. They are just given for your understanding.
    - Do not extract any CHUNKS from the PREVIOUS_CHUNKS. Only use the CURRENT_CHUNKS.

    PREVIOUS_CHUNKS : {context}

    CURRENT_CHUNKS : {chunks}  

"""


QUERY_DECOMPOSITION_PROMPT = """
    You are a helpful assistant that prepares sub queries from CURRENT_QUERY.
    Your job is to simplify complex queries into multiple queries that will be standalone independent statements evaluated against a set of document.
    The queries should be framed in the same words as the CURRENT_QUERY. 
    Don't make any unwanted assumptions for creating queries.
    
    DISPLAY:
    {{
        "queries":["List of all the different queries we got from CURRENT_QUERY"]
    }}
    
    CURRENT_CLAUSE: {question}
"""



EVALUATION_PROMPT_V2 = """
    You are an expert contract evaluation specialist. Your task is to assess whether the following CLAUSE 
    is being adhered to by the customer based on the provided CHUNKS of customer documentation.

    Instructions:
    1. Carefully analyze the CLAUSE to understand its requirements and implications.
    2. Review each of the CHUNKS of customer documentation to determine if the CLAUSE is being followed.
    3. Base your judgment solely on the information provided in the CHUNKS.

    Output:
    - Set the compliance_status to True if the CHUNKS collectively demonstrate full adherence to the CLAUSE.
    - Set the compliance_status to False if the CHUNKS fail to demonstrate full adherence to the CLAUSE.

    DISPLAY:
        Ensure the result is presented in the following JSON format exactly as shown:
            {{
            "compliance_status": "True/False",
            "reason_of_compliance":"proper reason for True or False"
            }}

    CLAUSE: {clause}

    CHUNKS: {chunks}
"""

EVALUATION_PROMPT_V3 = """
    You are an expert contract evaluation specialist. Your task is to assess whether the following CLAUSE 
    is being adhered to by the customer based on the provided CHUNKS of customer documentation.

    Instructions:
    1. Use the CLAUSE and rephrase it to Question to retrieve relevant CHUNKS to the rephrased CLAUSE.
    2. Carefully analyze the repharased CLAUSE to understand its requirements and implications.
    3. Review each of the CHUNKS of customer documentation to determine if the CLAUSE is being followed.
    4. Base your judgment solely on the information provided in the CHUNKS.
    5. Evaluate each CHUNK individually and collectively to calculate the compliance level accurately.

    Output:
    - Set the compliance_status to one of the following:
        - "Fully Meeting" if the CHUNKS collectively demonstrate full adherence to the CLAUSE.
        - "Partially Meeting" if the CHUNKS show partial adherence but fail to meet some aspects of the CLAUSE.
        - "Not Meeting" if the CHUNKS do not provide sufficient evidence to demonstrate adherence to the CLAUSE.
    - Provide detailed reasoning for your classification decision.
    - List the specific CHUNKS (with chunk_id, document_name, and page_no) that are most relevant to your evaluation.
    - Provide at least 4-5 specific and valid points to justify your classification.

    DISPLAY:
        Present the result in the following JSON format exactly as shown:
        {{
            "Repharased Clause": "Repharase the Clause to a question to be asked for better retrieval of relevant chunks"
            "compliance_status": "Fully Meeting/Partially Meeting/Not Meeting",
            "reason_of_classification": "Detailed explanation for the compliance status selected, referencing the CLAUSE and CHUNKS.",
            "chunk_ids": [
                {{
                    "chunk_id": "ID of the referenced chunk",
                    "chunk_content":"chunk data",
                    "document_name": "File Name or the PDF name",
                    "page_no": "Page number of the chunk"
                }}
            ],
            "proofs_to_validate": "List 4- 5 valid points to validate that the clause is 'Fully Meeting/Partially Meeting/Not Meeting' in the chunks"
        }}

    REMEMBER:
    - Use a balanced and evidence-based approach. 
    - If compliance is ambiguous or cannot be fully determined, classify as "Partially Meeting" and explain why.
    - When quantifying compliance, choose the best possible interpretation based on the provided CHUNKS.
    - Choose the most relevant CHUNKS from the list of CHUNKS that matches the rephrased CLAUSE.

    CLAUSE: {clause}

    CHUNKS: {chunks}
"""


EVALUATION_PROMPT_V4 = """
    You are an expert contract evaluation specialist. Your task is to assess whether the following CLAUSE 
    is being adhered to by the customer based on the provided CHUNKS of customer documentation.

    Instructions:
    1. Use the CLAUSE to retrieve relevant CHUNKS to the rephrased CLAUSE.
    2. Carefully analyze the CLAUSE to understand its requirements and implications.
    3. Review each of the CHUNKS of customer documentation to determine if the CLAUSE is being followed.
    4. Base your judgment solely on the information provided in the CHUNKS.
    5. Evaluate each CHUNK individually and collectively to calculate the compliance level accurately.

    Output:
    - Set the compliance_status to one of the following:
        - "Fully Meeting" if the CHUNKS collectively demonstrate full adherence to the CLAUSE.
        - "Partially Meeting" if the CHUNKS show partial adherence but fail to meet some aspects of the CLAUSE.
        - "Not Meeting" if the CHUNKS do not provide sufficient evidence to demonstrate adherence to the CLAUSE.
    - Provide detailed reasoning for your classification decision.
    - List the specific CHUNKS (with chunk_id, document_name, and page_no) that are most relevant to your evaluation.
    - Provide at least 4-5 specific and valid points to justify your classification.

    DISPLAY: Output correctly the result only in the following JSON format exactly as shown. Don't make any irrelevant json:
        {{
            "clause": "Clause that is being used",
            "compliance_status": "Fully Meeting/Partially Meeting/Not Meeting",
            "chunk_ids": [
                {{
                    "chunk_id": "ID of the referenced chunk",
                    "chunk_content":"chunk data of that particular chunk_id",
                    "document_name": "PDF name of the Chunk",
                    "page_no": "Page number of the chunk",
                    "reasoning": "Detailed explanation for the chunk referencing"
                }},
                .
                .
            ],
            "proofs_to_validate": ["List 4- 5 valid points to validate that the clause is 'Fully Meeting/Partially Meeting/Not Meeting' in the chunks" ],
            "accountability_lead":"any person name or title name responsible for making this clause meet."
        }}

    REMEMBER:
    - Use a balanced and evidence-based approach. 
    - If compliance is ambiguous or cannot be fully determined, classify as "Partially Meeting" and explain why.
    - When quantifying compliance, choose the best possible interpretation based on the provided CHUNKS.
    - Choose the most relevant CHUNKS from the list of CHUNKS that matches the rephrased CLAUSE.
    - Strictly select "chunk_ids" from CHUNKS only and "clause" from CLAUSE only. Don't mix them. 


    CLAUSE: ```{clause}```

    CHUNKS: ```{chunks}```
"""


RELEVANT_CHUNKS = """
    You are an expert similarity finder specialist. Your task is to identify relevant chunks from a given set of CHUNKS that directly relate to the provided CLAUSE. The goal is to narrow down the CHUNKS for deeper evaluation against the CLAUSE requirements while excluding completely irrelevant chunks.

    Instructions:
    1. Rephrase the CLAUSE into a question to effectively retrieve CHUNKS relevant to the CLAUSE.
    2. Analyze each CHUNK carefully to assess its relevance to the rephrased CLAUSE.
    3. Select only those CHUNKS that directly address or provide context for the CLAUSE requirements.
    4. Exclude CHUNKS that are completely irrelevant to the CLAUSE.
    5. If the relevance is ambiguous or partially related, include the CHUNK for further review.
    6. Base your decisions solely on the provided information in the CHUNKS.

    Output:
    - For each set of CHUNKS, provide:
        - The Rephrased Clause as a question to improve chunk retrieval.
        - A list of relevant CHUNKS (with chunk_id, chunk_content) that directly address or provide context for the CLAUSE.

    DISPLAY: Output the result in the following JSON format exactly as shown:
    {{
        "Rephrased Clause": "Rephrase the Clause to a question to retrieve relevant chunks.",
        "relevant_chunks": [
            {{
                "chunk_id": "ID of the referenced chunk",
                "chunk": "data of the chunk 'document' key data",
                "page no": "Page number of the chunk",
                "pdf name": "PDF Name of the chunk"
            }},
        ]
    }}

    REMEMBER:
    - Use a balanced and evidence-based approach.
    - Exclude chunks that are entirely irrelevant and unrelated to the CLAUSE.
    - If the relevance is ambiguous but potentially linked, include the CHUNK as relevant for further evaluation.
    - When quantifying compliance, choose the best possible interpretation based on the provided CHUNKS.
    - Select the most relevant CHUNKS from the list that directly address or provide meaningful context to the rephrased CLAUSE.

    CLAUSE: {clause}

    CHUNKS: {chunks}

"""

RELEVANT_CHUNKS_V2 = """
    You are an expert similarity finder specialist. Your task is to identify relevant chunks from a given set of CHUNKS that directly relate to the provided CLAUSE. The goal is to narrow down the CHUNKS for deeper evaluation against the CLAUSE requirements while excluding unnecessary, redundant, or irrelevant chunks.

    Instructions:
    1. Rephrase the CLAUSE into a question to effectively retrieve CHUNKS relevant to the CLAUSE.
    2. Analyze each CHUNK carefully to assess its relevance to the rephrased CLAUSE.
    3. Select only those CHUNKS that:
        - Directly address the CLAUSE requirements.
        - Provide meaningful information or context related to the CLAUSE.
    4. Exclude CHUNKS that:
        - Are completely irrelevant to the CLAUSE.
        - Contain only general headings, repetitive content, or metadata (e.g., titles, procedural numbering, or document formatting details).
        - Add no substantive value to understanding or fulfilling the CLAUSE requirements.
        - Can't be used directly in evaluating the clause.
        - Contains irrelevant content (like content page, unwanted table data,etc.) that can't be used in evaulation of clause.
    5. If the relevance of a CHUNK is ambiguous but potentially linked to the CLAUSE, include it for further review.
    6. Base your decisions solely on the provided information in the CHUNKS.

    Output:
    - For each set of CHUNKS, provide:
        - The Rephrased Clause as a question to improve chunk retrieval.
        - A list of relevant CHUNKS (with chunk_id, chunk_content) that directly address or provide meaningful context for the CLAUSE.

    DISPLAY: 
    - Output correctly the result only in the following JSON format exactly as shown.
    - JSON format should be standard JSON without any error.
    - Don't make any irrelevant json.
    {{
        "Rephrased Clause": "Rephrase the Clause to a question to retrieve relevant chunks.",
        "relevant_chunks": [
            {{
                "chunk_id": "ID of the referenced chunk",
                "chunk": "data of the chunk 'document' key data of that particular chunk_id",
                "page no": "Page number of the chunk",
                "pdf name": "PDF Name of the chunk"
            }},
        ]
    }}

    REMEMBER:
    - Use a balanced and evidence-based approach.
    - Exclude chunks that are entirely irrelevant, redundant, or consist of only headings, metadata, or formatting details.
    - If a CHUNK is ambiguous but potentially related, include it as relevant for further evaluation.
    - When quantifying compliance, choose the best possible interpretation based on the provided CHUNKS.
    - Select the most relevant CHUNKS from the list that directly address or provide meaningful context to the rephrased CLAUSE.
    - Strictly select "relevant_chunks" from CHUNKS only and "Rephrased Clause" from CLAUSE only. Don't mix them. 

    CLAUSE: ```{clause}```

    CHUNKS: ```{chunks}```

"""

format_text="""
You are text formatter.Please format the following TEXT(below in triple backticks) into a readable markdown format, with proper headings, bullet points, and sections. Ensure that the structure is clear and easy to read.
TEXT:```{text}```

"""


QUANTITATIVE_CLAUSE= """
    You are a legal expert responsible for identifying clauses that a consultant or contractor must meet, based on the Department of Energy (DoE) guidelines outlined in the provided CHUNKS. Your task is to analyze all the CHUNKS and extract a list of QUANTITATIVE CLAUSES that specifically define the obligations of consultants or contractors. These clauses will be used to assess the contractor's or consultant's completed work.

    - Only include clauses that explicitly state the responsibilities or requirements of the consultant or contractor. Ignore clauses that pertain to the obligations of the Department of Energy or its departments.
    - Clauses typically use words such as 'must', 'shall', 'will', or similar terms.
    - Each extracted QUANTITATIVE CLAUSE should:
    - Be a complete and standalone sentence, starting with the consultant's or contractor’s obligations (e.g., "Contractor must...", "Consultant shall...", "Contractor will...").
    - Exclude any clauses that do not specifically assign responsibility to the contractor or consultant.
    - Include all relevant QUANTITATIVE CLAUSES, whether from the main documents or attachments.
    - Do not merge or summarize the clauses; list them as they appear.

    DISPLAY: Ensure the output follows the exact JSON format shown below:
    {{ 
        "clauses": [ 
            {{ 
                "clause": "please put the extracted QUANTITATIVE CLAUSE here", 
                "type_of_clause": "based on the extracted quantitative clause, identify QAC or QAP"
                "reference": {{ 
                    "Page No": "[page number of the particular clause]", 
                    "File Name": "[file name for the clause]" 
                }} 
            }} 
        ] 
    }} 

    CHUNKS: {chunks} 

"""

QUANTITATIVE_CLAUSE_V2 = """
    You are a legal expert responsible for identifying clauses that a consultant or contractor must meet, based on the
    Department of Energy (DoE) guidelines outlined in the provided CHUNKS. Your task is to analyze all the CHUNKS and
    extract a list of QUANTITATIVE CLAUSES that specifically define the obligations of consultants or contractors.
    These clauses will be used to assess the contractor's or consultant's completed work.

    Point to be remember:
        1.Only include clauses that explicitly state the responsibilities or requirements of the consultant or contractor.
          Ignore clauses that pertain to the obligations of the Department of Energy or its departments.
        2. Clauses typically use words such as 'must', 'shall', 'will', or similar terms.
        3. Each extracted QUANTITATIVE CLAUSE should:
          - Be a complete and standalone sentence, starting with the consultant's or contractor’s obligations (e.g., "Contractor must...", "Consultant shall...", "Contractor will...").
          - Exclude any clauses that do not specifically assign responsibility to the contractor or consultant.
        4. Include all relevant QUANTITATIVE CLAUSES, whether from the main documents or attachments.
        5. Do not merge or summarize the clauses; list them as they appear.
        6. Classify each clause as either QAP (Quality Assurance Plan) or QAC (Quality Assurance Criteria).
        7. If no relevant clauses are found in the CHUNKS, return an empty list.

    "independent":
        Your goal is to check whether each clause references something else, such as another clause, attachment, file, or section, and update the independemt value the in the  JSON accordingly.

        - For each clause:
            - If the clause references something else (e.g., "See Attachment A," "Refer to Section 2.3," "to meet the requirements of this Order"), set `"independent": false`.
            - If the clause does not reference any external material, set `"independent": true`.

    DISPLAY: Ensure the output follows the exact JSON format shown below:
    {{
        "clauses": [
            {{
                "clause": "please put the extracted QUANTITATIVE CLAUSE here",
                "type_of_clause": "based on the extracted quantitative clause, identify QAC or QAP",
                "independent":"[true/false]",
                "reason":"reason for 'independent' classification to true/false"
                "reference": {{
                    "Page No": "[page number]",
                    "File Name": "[file name]"
                }}
            }}
        ]
    }}

    CHUNKS: {chunks}
"""

REFERENCING_PROMPT="""
    You are a legal expert tasked with analyzing the JSON data containing QUANTITATIVE CLAUSES. Your goal is to check whether each clause references something else, such as another clause, attachment, file, or section, and update the independemt value the in the  JSON accordingly.

    - For each clause:
        - If the clause references something else (e.g., "See Attachment A," "Refer to Section 2.3," "to meet the requirements of this Order"), set `"independent": false`.
        - If the clause does not reference any external material, set `"independent": true`.

    - Ensure the updated JSON structure follows the exact format shown below:
    {{ 
        "clauses": [ 
            {{ 
                "clause": "please put the extracted QUANTITATIVE CLAUSE here", 
                "type_of_clause": "based on the extracted quantitative clause, identify QAC or QAP", 
                "independent": "if the clause references to something like another clause, attachment, file, section, or similar term, set as false; otherwise set as true", 
                "reason": "reason for classifying independent flag"
                "reference": {{ 
                    "Page No": "[page number of the particular clause]", 
                    "File Name": "[file name for the clause]" 
                }} 
            }} 
        ] 
    }} 

    DISPLAY:UPDATED JSON

    REMEMBER
    -Do not change the other values in the json, You just need to update the independent key's value and its reason.

    JSON_INPUT: {json_data} 
"""

INITIAL_ANSWER_PROMPT = """
    You are provided with CLAUSE and its referenced CHUNKS.
    Your task is to include all the information from the CHUNKS that are required to fulfill the CLAUSE fully, in the output.
    If there are any established standards, references or links required to meet the CLAUSE. Then include them also in the output.    

    "external_references":
    - the output may contain some established standards(e.g. ASME NQA-1-2008,NQA-1a-2009 addenda etc.). Extract them from the "output" and list them. 
    

    Output:{{
        "output":"Provide a  generalized output in paragraph format that incorporates all necessary aspects from the CHUNKS to fulfill the CLAUSE while maintaining clarity and focus.",
        "external_references":["List fo all external references"]
    }}

    REMEMBER:
    - Only include the data from CHUNKS that the contractor needs to meet and satisfy.
    - Don't include any information that the DOE(Department Of Energy) needs to follow for themselves. 

    CLAUSE: {clause}

    CHUNKS: {chunks}
"""

EXTERNAL_REFERENCE_PROMPT = """
    Below given is a QUESTION and few EXTABLISHED_STANDARDS. 
    I want you to use your knowledge and give me detailed knowledge of what is required to fulfill the QUESTION in comprehensive manner for each of the EXTABLISHED_STANDARDS.
    
    Output:
    Detailed knowledge of what is required to fulfill the QUESTION in comprehensive manner for each of the EXTABLISHED_STANDARDS.

    QUESTION: {question}
    EXTABLISHED_STANDARDS :{standards}

"""

EXTERNAL_STANDARDS_PROMPT = """
    You have a QUESTION and its ANSWER.
    The ANSWER may reference some standards. Please use your knowledge and extract relevant information from those standards for the QUESTION given below
    and give a comprehensive and detailed answer which includes combination of prior answer along with any information you extracted 
    from the standards related to the QUESTION. 

    For the standards,I have provided brief explanation in EXPLANATION_FOR_REFERENCES. 
    Include that knowldge in the output also and give me a comprehensive answer for the question.
    Don't keep standards name in the final output, you have to use EXPLANATION_FOR_REFERENCES to get relevant information to be included there.

    Output:
    Final version of the clause is thorough and provides all necessary instructions for implementation, independent of any external standards.
    
    QUESTION : {question}

    ANSWER : {answer}

    EXPLANATION_FOR_REFERENCES: {references}
"""


EVALUATION_PROMPT_V5 = """
    You are an expert contract evaluation specialist. Your task is to assess whether the REQUIREMENTS 
    to satisfy the CLAUSE given by DOE(Department Of Energy) for the contractor is being adhered to by the customer based on the provided CHUNKS of customer documentation.

    Instructions:
    1. Use the CLAUSE to retrieve relevant CHUNKS to the rephrased CLAUSE.
    2. Carefully analyze the REQUIREMENTS to understand the requirements and implications of the CLAUSE.
    3. Review each of the CHUNKS of customer documentation to determine if the REQUIREMENTS are being followed.
    4. Base your judgment solely on the information provided in the CHUNKS.
    5. Evaluate each CHUNK individually and collectively to calculate the compliance level accurately.

    Output:
    - Set the compliance_percentage to tell how much percentage of REQUIREMENTS are being satisfied through the CHUNKS.
        - It should be in range 0-100 percent in integer format.
    - Provide detailed reasoning for your classification decision.
    - List the specific CHUNKS (with chunk_id, document_name, and page_no) that are most relevant to your evaluation.
    - Provide at least 4-5 specific and valid points to justify your classification.
    
    DISPLAY: Output correctly the result only in the following JSON format exactly as shown. Don't make any irrelevant json:
        {{
            "clause": "Clause that is being used",
            "compliance_percentage": "percentage of compliance of documents with the REQUIREMENTS of CLAUSE",
            "chunk_ids": [
                {{
                    "chunk_id": "ID of the referenced chunk",
                    "chunk_content":"chunk data",
                    "document_name": "PDF name of the Chunk",
                    "page_no": "Page number of the chunk",
                    "reasoning": "Detailed explanation for the chunk referencing"
                }},
                .
                .
            ],
            "proofs_to_validate": ["List 4- 5 valid points to validate your percentage justification criteria"],
        }}

    REMEMBER:
    - Use a balanced and evidence-based approach. 
    - When quantifying compliance, choose the best possible interpretation based on the provided CHUNKS.
    - Choose the most relevant CHUNKS from the list of CHUNKS that matches the REQUIREMNTS.

    CLAUSE: {clause}

    REQUIREMENTS: {requirements}

    CHUNKS: {chunks}
"""


clause_prompt=ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(CLAUSE_PROMPT),
    ],
    input_variables=['chunks'],
)

de_duplicate_prompt=ChatPromptTemplate(
        messages=[
                SystemMessagePromptTemplate.from_template(DEDUPLICATION_PROMPT),
            ],
        input_variables=['guidelines','clause'],
    )

evaluation_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(EVALUATION_PROMPT_V5),
                ],
                input_variables=['chunks','clause','requirements'],
        )

relevant_chunks_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(RELEVANT_CHUNKS_V2),
                ],
                input_variables=['chunks','clause'],
        )



query_decomposition_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(QUERY_DECOMPOSITION_PROMPT),
                ],
                input_variables=['question'],
        )

quantitative_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(QUANTITATIVE_CLAUSE),
                ],
                input_variables=['chunks'],
        )

chunks_extraction_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(REVISED_CHUNKS_EXTRACTION_PROMPT),
                ],
                input_variables=['context','chunks'],
        )




quantitative_prompt_v2 = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(QUANTITATIVE_CLAUSE_V2),
                ],
                input_variables=['chunks'],
        )


referencing_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(REFERENCING_PROMPT),
                ],
                input_variables=['json_data'],
        )

format_text_prompt=ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(format_text),
    ],
    input_variables=['text'],
)

initial_answer_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(INITIAL_ANSWER_PROMPT),
                ],
                input_variables=['question'],
        )

external_reference_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(EXTERNAL_REFERENCE_PROMPT),
                ],
                input_variables=['standards','question'],
        )

external_standards_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(EXTERNAL_STANDARDS_PROMPT),
                ],
                input_variables=['context','chunks','references'],
        )