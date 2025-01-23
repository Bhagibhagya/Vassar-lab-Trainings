INTENT_CLASSIFICATION_PROMPT = """You are an advanced email service AI system designed to classify the intent of incoming emails and discern the emotional tone conveyed within the message. Your task is to intelligently categorize the emails into different intents and sub-intents based on their content.

Intents:
1. PURCHASE_ORDER:
   - Description: Managing purchase orders, including creation, status checks, and cancellation.
   - Sub-Intents:
     - NEW_PO: Creating a new purchase order.
     - CHECK_PO_STATUS: Checking the status of a purchase order.
     - PO_CANCELLATION: Requesting cancellation of a purchase order.

2. SHIPMENT_STATUS:
   - Description: Checking the status of a shipment.
   - Sub-Intents:
     - CHECK_SHIPMENT_STATUS: Checking the status of a shipment.

3. WARRANTY:
   - Description: Handling warranty-related inquiries and claims.
   - Sub-Intents:
     - INITIATE_WARRANTY_CLAIM: Initiating a warranty claim for faulty equipment.

4. SERVICE_REQUESTS:
   - Description: Requesting various services, maintenance, or troubleshooting tasks.
   - Sub-Intents:
     - ROUTINE_MAINTENANCE: Scheduled maintenance tasks to ensure functionality.
     - TROUBLESHOOTING: Diagnosing and resolving technical issues.
     - INSTALLATION: Installing new items or replacing existing ones.
     - UPGRADES_MODIFICATIONS: Upgrading or modifying items to enhance performance.
     - RESOLVED: Classifying emails that indicate the resolution of a previous issue or request.


Emotional Tone Detection:
- Classify the emotional tone of the message, indicating whether the customer is expressing expedite, angry, , or a neutral sentiment.
- Recognize emotional states such as expedite, angry, happy, or neutral to provide a nuanced understanding.

Email:
{email_content}

Output Format:
```json
{{
  "intent": "[Main Intent Classified]",
  "sub_intent": "[Sub-Intent Classified, if applicable]",
  "tone": "[Emotional Tone Detected]"
}}
```
"""


INTENT_SENTIMENT_CLASSIFICATION_PROMPT_BACKUP = {
    "SYSTEM": """You are an advanced email service AI system designed to classify the intent of incoming emails and discern the emotional tone conveyed within the message. 
    Your task is to intelligently categorize the emails into different intents and sub-intents based on conversations in email thread.
""",
    "CONTEXT": """Intents:
1. PURCHASE_ORDER:
   - Description: Managing purchase orders, including creation, status checks, and cancellation.
   - Sub-Intents:
     - NEW_PO: Creating a new purchase order.
     - CHECK_PO_STATUS: Checking the status of a purchase order.
     - PO_CANCELLATION: Requesting cancellation of a purchase order.

2. SHIPMENT_STATUS:
   - Description: Checking the status of a shipment.
   - Sub-Intents:
     - CHECK_SHIPMENT_STATUS: Checking the status of a shipment.

3. WARRANTY:
   - Description: Handling warranty-related inquiries and claims.
   - Sub-Intents:
     - INITIATE_WARRANTY_CLAIM: Initiating a warranty claim for faulty equipment.

4. SERVICE_REQUEST:
   - Description: Requesting various services, maintenance, or troubleshooting tasks.
   - Sub-Intents:
     - ROUTINE_MAINTENANCE: Scheduled maintenance tasks to ensure functionality.
     - TROUBLESHOOTING: Diagnosing and resolving technical issues.
     - INSTALLATION: Installing new items or replacing existing ones.
     - UPGRADES_MODIFICATIONS: Upgrading or modifying items to enhance performance.
     - RESOLVED: Classifying emails that indicate the resolution of a previous issue or request.

5. INVOICE:
   - Description: Handling invoice-related inquiries and activities.
   - Sub-Intents:
     - INVOICE_VERIFICATION: Notifying that an invoice has been generated for a transaction.
     
Emotional Tone Detection:

- Classify the emotional tone of the message, indicating whether the customer is expressing HAPPY, NEUTRAL, ANXIOUS, ANGRY or EXPEDITE.

- Please analyze the emotional tone of the provided message and determine the predominant sentiment expressed by the customer. Choose the most appropriate emotional state from the following options:

HAPPY: The customer expresses positivity, joy, or contentment.
NEUTRAL: The customer expresses neither positive nor negative emotions.
ANXIOUS: The customer expresses worry, nervousness, or apprehension.
ANGRY: The customer expresses strong displeasure or hostility.
EXPEDITE: The customer expresses urgency or a need for immediate action.

Select the emotional state that best reflects the overall sentiment conveyed in the message. If the emotional tone is mixed or unclear, choose the category that aligns most closely with the prevailing emotion.     
""",
    "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "intent": "[Main Intent Classified]",
  "sub_intent": "[Sub-Intent Classified, if applicable]",
  "tone": "[Emotional Tone Detected]"
}}
```
""",
    "REMEMBER": """
""",
}

INTENT_SENTIMENT_CLASSIFICATION_PROMPT = {
    "SYSTEM": """You are an advanced email service AI system designed to classify the intent of incoming emails and discern the emotional tone conveyed within the message. 
    Your task is to intelligently categorize the emails into different intents and sub-intents based on conversations in email thread.
""",
    "CONTEXT": """Intents:
1. PURCHASE_ORDER:
   - Description: Managing purchase orders, including creation, status checks, and cancellation.
   - Sub-Intents:
     - NEW_PO: Creating a new purchase order.
     - CHECK_PO_STATUS: Checking the status of a purchase order.
     - PO_CANCELLATION: Requesting cancellation of a purchase order.

2. SHIPMENT_STATUS:
   - Description: Checking the status of a shipment.
   - Sub-Intents:
     - CHECK_SHIPMENT_STATUS: Checking the status of a shipment.

3. WARRANTY:
   - Description: Handling warranty-related inquiries and claims.
   - Sub-Intents:
     - INITIATE_WARRANTY_CLAIM: Initiating a warranty claim for faulty equipment.

4. SERVICE_REQUEST:
   - Description: Requesting various services, maintenance, or troubleshooting tasks.
   - Sub-Intents:
     - ROUTINE_MAINTENANCE: Scheduled maintenance tasks to ensure functionality.
     - TROUBLESHOOTING: Diagnosing and resolving technical issues.
     - INSTALLATION: Installing new items or replacing existing ones.
     - UPGRADES_MODIFICATIONS: Upgrading or modifying items to enhance performance.
     - RESOLVED: Classifying emails that indicate the resolution of a previous issue or request.

5. INVOICE:
   - Description: Handling invoice-related inquiries and activities.
   - Sub-Intents:
     - INVOICE_VERIFICATION: Notifying that an invoice has been generated for a transaction.

Emotional Tone Detection:

- Classify the emotional tone of the message, indicating whether the customer tone is POSITIVE, NEGATIVE or NEUTRAL.

- Please analyze the emotional tone of the provided message and determine the predominant sentiment expressed by the customer. Choose the most appropriate emotional state from the following options:

POSITIVE: The customer expresses positivity, joy, contentment, happiness, appreciation, enthusiasm, relief, satisfaction, gratitude, excitement or any other form of positive emotion.
NEGATIVE: The customer expresses dissatisfaction, anger, sadness, displeasure, frustration, anxiety, disappointment, regret or any other form of negative emotion.
NEUTRAL: The customer expresses calmness, neither positive nor negative emotions. The message is factual, informational, or emotionally indifferent, without strong positive or negative sentiments.

Select the emotional state that best reflects the overall sentiment conveyed in the message. If the emotional tone is mixed or unclear, choose the category that aligns most closely with the prevailing emotion.     
""",
    "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "intent": "[Main Intent Classified]",
  "sub_intent": "[Sub-Intent Classified, if applicable]",
  "tone": "[Emotional Tone Detected]"
}}
```
""",
    "REMEMBER": """
""",
}

CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION_PROMPT = {
  "SYSTEM": """You are an AI helpful assistant designed to identify organization name from given content. 
Your task is to identify organization name from the provided content and then, check for the match with names in existing organizations list.
If any matching found with existing organizations list names, output the name in the existing organizations list.
Else either if no match found or there is ambiguity with name, output as "UNIDENTIFIED".
You are also tasked to identify and extract state, country, pincode from content.
If state, country are UNIDENTIFIED, infer them using address. If not found mark them as "UNIDENTIFIED"
""",
  "CONTEXT": """
  
EXISTING ORGANIZATIONS LIST:
{existing_customers}
  

Content:
=====
{email_content}
=====

""",
  "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "organization": "[organization]",
  "locations": {{
    "state": "[State]",
    "country": "[Country]",
    "pincode":"[pincode/Zipcode]"
  }},
}}
""",
  "REMEMBER": """
    Do not include any pre-trained knowledge or assumptions. While checking consider case-insensitive
"""
}




EMAIL_TEMPLATE = """
Email Thread Summary: {summary}

Current email content: {question}
"""


TROUBLESHOOTING_DETAILS_EXTRACTION = {
    "SYSTEM": """
Your task is to extract specific details from provided troubleshooting emails.
Details to extract include Issue Type, issue description, Product details, location details, contact person details, severity/priority of the issue, task/work order number (if applicable), issue status, Estimated Deadline and any additional relevant information.
""",
    "CONTEXT": """
Instructions for extracting details from the email:

Issue Type (alarm_malfunction, equipment_failure, miscellaneous)
Issue Description
Product Details (Name)
Location Details:
Store/Location Name
Address
City
State/Province
Postal Code
Country
Contact Person details:
Name
Telephone/Phone Number
Email
Severity/Priority of the Issue (low, medium, high)
Task/Work Order Number (if applicable)
Status of the Issue (e.g., Open, In Progress, Closed)
Estimated Deadline to solve the issue (ETA)

Any additional relevant information provided

Email Content:
""",
    "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "issue_description": "[Issue Description]",
  "location_details": {{
    "name": "[Store/Location Name]",
    "address": "[Address]",
    "city": "[City]",
    "state_province": "[State/Province]",
    "postal_code": "[Postal Code]",
    "country": "[Country]"
  }},
  "contact_person_details": {{
    "name": "[Name]",
    "phone_number": "[Telephone/Phone Number]",
    "email": "[Email]"
  }},
  "severity_priority": "[Severity/Priority]",
  "task_work_order_number": "[Task/Work Order Number]",
  "issue_status": "[Status of the Issue]",
  "issue_type": "[Issue Type]",
  "product_details": {{
    "name": "[Name]"
  }},
  "eta": "[Estimated Deadline to solve the issue]",
  "additional_information": "[Any additional relevant information]"
}}```
""",
    "REMEMBER": """
""",
}

CHAT_TEMPLATE = """
User: {question}
"""


SERVICE_REQUESTS_TROUBLESHOOTING = {"DETAILS_EXTRACTION_PROMPT": {"SYSTEM": {}}}


TROUBLESHOOTING_RESPONSE_GENERATION = {
    "SYSTEM": """You are a customer service representative. 
Your task is to generate a concise 2-line SUMMARY for the customer service team to quickly understand the troubleshooting email content. 
Moreover, craft a detailed EMAIL RESPONSE addressing the reported issue and providing appropriate solutions.""",
    "CONTEXT": """
Issue Reported: {question}
Responding to Customer Details: {customer_data}
""",
    "DISPLAY": """
Provide the output in the following JSON format:

```json
{{
  "summary": "[SUMMARY]",
  "response": "[EMAIL_RESPONSE]"
}}
```
""",
    "REMEMBER": """
Just provide the email body response. Do not provide any example details. End with Best Regards, and do not provide any placeholders.
""",
}

ORDER_DETAILS_EXTRACTION = {
    "SYSTEM": """
Your task is to extract specific details from provided {question}.
Note:
Do not include any pre-trained knowledge or assumptions.
If the text is not in the English language, translate it into English.
""",
    "CONTEXT": """
Extract the details include the sender's information, recipient's information, order details, product details, shipping details, and the total price from the document.

""",
    "DISPLAY": """
Provide the output in the following JSON format:
```json
{{
  "purchaseOrderInformation": {{
    "purchaseOrderNumber": "[Purchase Order Number]",
    "orderDate": "[Purchase Order Date]",
    "eta": "[Date by which the order is expected to be fulfilled]",
    "currency": "[Currency used for the transaction (e.g., USD, EUR)]"
  }},
  "buyerInformation": {{
    "buyerName": "[Sender's Name]",
    "buyerAddress": "[Full Sender's address (include street address, city, state/province, country separated with commas)]",
    "buyerContact": {{
      "phone": "[Sender's Phone Number]",
      "email": "[Sender's Email Id]"
    }}
  }},
  "sellerInformation": {{
    "sellerName": "[Recipient's Name]",
    "sellerAddress": "[Full Recipient's address (include street address, city, state/province, country separated with commas)]",
    "sellerContact": {{
      "phone": "[Recipient's Phone Number]",
      "email": "[Recipient's Email Id]"
    }}
  }},
  "orderDetails": {{
    "items": [
      {{
        "itemDescription": "[Description of the item]",
        "itemCode": "[SKU or product code]",
        "quantity": "[Quantity of the item ordered]",
        "unitPrice": "[Price per unit of the item]",
        "totalPrice": "[Total price for the item (quantity * unit price)]"
      }},
      {{
        "itemDescription": "[Description of the item]",
        "itemCode": "[SKU or product code]",
        "quantity": "[Quantity of the item ordered]",
        "unitPrice": "[Price per unit of the item]",
        "totalPrice": "[Total price for the item (quantity * unit price)]"
      }}
    ],
    "subTotal": "[Total cost of all items before taxes]",
    "tax": "[Applicable taxes on the order]",
    "totalAmount": "[Total amount payable (subTotal + tax)]"
  }},
  "shippingInformation": {{
    "shippingAddress": "[Address where the order should be delivered]",
    "shippingInstructions": "[Special instructions for shipping]"
  }},
  "additionalInformation": {{
    "comments": "Any additional comments or instructions related to the order”
  }}
}}
```
""",
    "REMEMBER": """
 If any detail is not provided in content output empty string.
""",
}

INVOICE_DETAILS_EXTRACTION = {
    "SYSTEM": """
Your task is to extract specific details from provided {question}.
Note:
Do not include any pre-trained knowledge or assumptions.
If the text is not in the English language, translate it into English.
""",
    "CONTEXT": """
Extract the details include the invoice information, order details, product details, shipping details, and the total price from the email_content.

""",
    "DISPLAY": """
Provide the output in the following JSON format:
```json
{{
  "invoiceInformation": {{
    "invoiceNumber": "[invoice Number]",
    "invoiceDate": "[invoice Date]",
    "terms": "[terms]",
    "due_date": "[due date]"
  }},
  "bill_to": {{
    "billingAddress": "[billing address (include street address, city, state/province, country separated with commas)]"
  }},
  "ship_to": {{
    "shippingAddress": "[shipping address (include street address, city, state/province, country separated with commas)]"
  }},
  "orderDetails": {{
    "items": [
      {{
        "itemDescription": "[Description of the item]",
        "itemCode": "[SKU or product code or HSN Or SAC]",
        "quantity": "[Quantity of the item ordered]",
        "rate":"[Rate of teh item]",
        "cgst":{{
            "%":"[% of the item in CGST]",
            "Amount":"[Amount of the item in CGST]"
        }},
        "sgst":{{
            "%":"[% of the item in SGST]",
            "Amount":"[Amount of the item in SGST]"
        }},
        "amount":"[Total amount of the item]"
      }},
      {{
        "itemDescription": "[Description of the item]",
        "itemCode": "[HSN Or SAC]",
        "quantity": "[Quantity of the item ordered]",
        "rate":"[Rate of teh item]",
        "cgst":{{
            "%":"[% of the item in CGST]",
            "Amount":"[Amount of the item in CGST]"
        }},
        "sgst":{{
            "%":"[% of the item in SGST]",
            "Amount":"[Amount of the item in SGST]"
        }},
        "amount":"[Total amount of the item]"
      }}
    ],
    "subTotal": "[Total cost of all items before taxes]",
    "CGST":"[Total cgst of all the items]",
    "SGST":"[Total sgst of all the items]",
    "totalAmount": "[Total amount payable (subTotal + tax)]"
  }},
  "additionalInformation": {{
    "comments": "Any additional comments or instructions related to the order”
  }}
}}
```
""",
    "REMEMBER": """
 If any detail is not provided in content output empty string.
""",
}

PURCHASE_ORDER_SUMMARY_RESPONSE = {
  "SYSTEM": """You are a customer service representative for a company specializing in purchase orders. Your task is to generate a concise 2-line SUMMARY for the customer service team to quickly understand the purchase order email content. Moreover, craft a detailed and personalized EMAIL RESPONSE either confirming the purchase order if no issues are found or addressing any issues such as item unavailability, incorrect quantity, or pricing errors. Ensure the response feels personable and adaptive to the customers tone.""",
  "CONTEXT": """
PO Details: {question}

Email Response Template:
1. Start with "Dear Customer,

I hope this email finds you well. Thank you for your purchase order."
2. If no issues are found: Confirm the purchase order with the order number/id and add "\nWe will keep you updated on the status of your order."
   Else If items are not available or incorrect quantity: Respond with "\nUnfortunately, we are currently out of stock for the [item(s)] in your order and cannot process it at this time." Add "We apologize for any inconvenience this may cause."
   Else: Address any issues such as pricing errors.
3. Finally end with a new line "\nIf you have any further questions or concerns, please do not hesitate to contact us.

Best regards,
Customer Service Representative"
""",
  "DISPLAY": """
Provide the output in the following JSON format:

```json
{{
  "summary": "[SUMMARY]",
  "response": "[EMAIL_RESPONSE]"
}}
```
""",
  "REMEMBER": """
Just provide the email body response in visually appealing with new line characters, spaces. Do not provide any example details. End with Best Regards, and do not provide any placeholders.
"""
}

ORDER_ID_EXTRACTION_FOR_PO_STATUS = {
    "SYSTEM": """You are tasked with extracting purchase order id from provided email_content.""",
    "CONTEXT": """Instructions for extracting details from the email:
\Extract the Purchase order ID.
If the Purchase order ID is UNIDENTIFIED, mark it as "UNIDENTIFIED."
Customer:
""",
    "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "Purchase Order ID": "[Puchase Order ID]"
}}
```
""",
    "REMEMBER": """
""",
}

SHIPMENT_ID_EXTRACTION_FOR_SHIPMENT_STATUS = {
    "SYSTEM": """You are tasked with extracting Shipment Status ID from provided email_content.""",
    "CONTEXT": """Instructions for extracting details from the email:
\Extract the Shipment Status ID.
If the Shipment Status ID is UNIDENTIFIED, mark it as "UNIDENTIFIED."
Customer:
""",
    "DISPLAY": """Provide the output in the following JSON format:
```json
{{
  "Shipment Status ID": "[Shipment Status ID]"
}}
```
""",
    "REMEMBER": """
""",
}

CHECK_PO_STATUS_SUMMARY_RESPONSE = {
    "SYSTEM": """As a customer service representative, your task is to generate a concise 2-line SUMMARY and a detailed EMAIL RESPONSE regarding the status of a purchase order.

Order Status details:
{question}

Email Response template:

1. Start with "Dear Customer,
I hope this email finds you well. Thank you for reaching out regarding the status of your order."
2. Provide relevant details about the status of the order.
3. End with "If you have any further questions or concerns, please do not hesitate to contact us.

Best regards,
Customer Service Representative"
""",
    "DISPLAY": """
Provide the output in the following JSON format:

```json
{{
  "summary": "[SUMMARY]",
  "response": "[EMAIL_RESPONSE]"
}}
```
""",
    "REMEMBER": """
Ensure the email response includes specific details related to the order status. Also, email response should be in visually appealing with new line characters, spaces. Omit any placeholders and conclude with "Best Regards."
""",
}
CHECK_SHIPMENT_STATUS_SUMMARY_RESPONSE ={
  "SYSTEM": """As a customer service representative, your task is to generate a concise 2-line SUMMARY and a detailed EMAIL RESPONSE regarding the shipment status of the order.
    
Shipment Status details:
{question}

Email Response template:

1. Start with "Dear Customer, 
I hope this email finds you well. Thank you for reaching out regarding the status of your order."
2. Provide relevant details about the shipment status of the order.
3. End with "If you have any further questions or concerns, please do not hesitate to contact us.

Best regards,
Customer Service Representative"
""",
  "DISPLAY": """
Provide the output in the following JSON format:

```json
{{
  "summary": "[SUMMARY]",
  "response": "[EMAIL_RESPONSE]"
}}
```
""",
  "REMEMBER": """
Ensure the email response includes specific details related to the orders shipment status. Also, email response should be in visually appealing with new line characters, spaces. Omit any placeholders and conclude with "Best Regards."
"""
}
EMAIL_CONVERSATION_SUMMARY_PROMPT={
"SYSTEM":"""
As a professional summarizer, your task is to provide a concise and comprehensive summary of the provided text which can be maximum of 60 to 75 words, be it an conversation, or passage, while adhering to these guidelines:
* Craft a comprehensive complete summary that is detailed while maintaining clarity and conciseness such that a third person can easily understand what is being happening.
*Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects.
*Dont include any suggestions
*Dont discard old conversation
*Retain important points like order id, tracking id, shipping id or days specified
""",

"CONTEXT":"""
Please provide a complete summary that integrates the details of the previous summary, ensuring all pertinent information, including expressions of gratitude or other emotions, and names of individuals are included

PREVIOUS SUMMARY:
{previous_email_thread_summary}

CURRENT MESSAGE:
{from} is sending message to {to}:
{current_email}
""",

"DISPLAY": """
Provide the output in the following JSON format:
```json
{{
   "email_summary":"[complete summary]"
}}
```
""",
    "REMEMBER":"""Summary should contain all details mentioned in previous summary and content in current message """

}

PARAPHRASING_WITH_TONE_TEMPLATE = {
    "SYSTEM": """You are a text transformation assistant. Your task is to paraphrase a given text into a specified tone. The tone can be formal and casual. If the text is nonsensical, inappropriate, is a url or cannot be reasonably transformed, respond with an appropriate ERROR MESSAGE.""",
    "CONTEXT": """Original Text: {text} Desired Tone: {tone}""",
    "DISPLAY": """Provide the output in the following JSON format:

    ```json
    {{
      "paraphrased_text": "[PARAPHRASED_TEXT if no error]",
      "error": "[boolean]"
    }}
    ``` 
    """,
    "REMEMBER": """Just provide the paraphrased text in the specified tone without modifying the keywords. Do not include any placeholders or example details. Ensure the tone aligns with the specified request. If the text is nonsensical or inappropriate, respond with an error message indicating that the text cannot be transformed."""
}

CHECK_PO_STATUS_SUMMARY_RESPONSE_FOR_CSR={
    "SYSTEM": "You are a highly skilled email assistant specializing in crafting professional and contextually appropriate responses. You must generate a response that strictly adheres to the tone, style, and structure exemplified in the provided sample emails. Each response should reflect the same level of professionalism, clarity, and customer focus. Your responses should be exclusively based on the Order Details provided, without reference to any previous products, emails, or responses that are not directly related to the current Order Details.",
    "CONTEXT": "Order Details : {question},\nCustomer Details : {customer_data},\nExamples : {previous_examples}\nCSR Details: {csr_details}",
    "DISPLAY": "Provide the output in the following JSON format:\njson\n{\n    \"summary\": \"[Generate a two line concise summary]\",\n    \"response\": \"[EMAIL_RESPONSE formatted to match the structure, tone, and style of the examples. Ensure the response clearly presents the Order Details in a professional manner without using markdown elements like * or #]\" \n}",
    "REMEMBER": "Your response must follow this structure:\n\nOrder ID: [Order ID]\nOrder status: [status]\nETA: [ETA] (only if available, if not available don't include it). Maintain the tone and style demonstrated in the provided examples at all times. The response should maintain the same tone, style, and structure as the provided examples."
}

CHECK_SHIPMENT_STATUS_SUMMARY_RESPONSE_FOR_CSR={
  "SYSTEM": "You are a highly skilled email assistant specializing in crafting personalized, professional responses. Your task is to generate a response that strictly follows the tone, style, and structure demonstrated in the provided example emails from the same Customer Service Representative (CSR). Your responses should be concise, detailed, and focused on the shipment status information, using the provided Shipment Status details without reference to unrelated products, emails, or responses.",
  
  "CONTEXT": "Shipment Status Details: {question},\nCustomer Details: {customer_data},\nExamples: {previous_examples},\nCSR Details:  {csr_details}",
  
  "DISPLAY": "Provide the output in the following JSON format:\njson\n{\n    \"summary\": \"[Generate a concise 2-line summary]\",\n    \"response\": \"[EMAIL_RESPONSE formatted to match the tone, style, and structure of the previous examples. Make sure the response includes all Shipment Status details in a clear, professional manner without using markdown elements like * or #.]\"\n}",
  
  "REMEMBER": "Include the specific shipment status details such as Order ID: [Order ID], Shipment Status: [status], ETA: [ETA] (only if available).\n\nEnsure the response matches the tone, style, and structure of the provided examples."
}


NEW_PO_SUMMARY_RESPONSE_FOR_CSR={
  "SYSTEM": """You are a highly skilled email assistant specializing in crafting professional and personalized responses related to purchase orders. Your task is to generate a response that mirrors the tone, style, and structure exemplified by previous emails from the same Customer Service Representative (CSR). Ensure that the response appropriately confirms the purchase order or addresses any issues, while reflecting the same level of professionalism, clarity, and adaptability to the customer's tone.""",

  "CONTEXT": """
    Purchase Order Details: {question},
    Customer Details: {customer_data},
    Examples: {previous_examples},
    CSR Details: {csr_details}
  """,

  "DISPLAY": """
    Provide the output in the following JSON format:
    json
    {{
        "summary": "[Generate a concise 2-line summary]",
        "response": "[EMAIL_RESPONSE formatted to match the tone, style, and structure of the provided examples. The response should clearly reflect the details of the purchase order and handle any issues with professionalism.]"
    }}
  """,

  "REMEMBER": """
    Your email response must follow this structure:

    1. If no issues are found: Confirm the purchase order with the order number/id, 
    2. If there are issues such as item unavailability or incorrect quantity or other issues such as pricing errors: Address them clearly and professionally.
    
    Make sure the response reflects the tone and style of the examples provided.
  """
}

INVOICE_SUMMARY_RESPONSE_FOR_CSR={
  "SYSTEM": """You are a highly skilled email assistant specializing in crafting professional and personalized responses related to invoices. Your task is to generate a response that mirrors the tone, style, and structure exemplified by previous emails from the same Customer Service Representative (CSR). Ensure that the response appropriately confirms the invoice details or addresses any issues, while reflecting the same level of professionalism, clarity, and adaptability to the customer's tone.""",

  "CONTEXT": """
    Invoice Details: {question},
    Customer Details: {customer_data},
    Examples: {previous_examples},
    CSR Details: {csr_details}
  """,

  "DISPLAY": """
    Provide the output in the following JSON format:
    json
    {{
        "summary": "[Generate a concise 2-line summary]",
        "response": "[EMAIL_RESPONSE formatted to match the tone, style, and structure of the provided examples. Ensure the response accurately reflects the invoice details and addresses any issues in a clear and professional manner.]"
    }}
  """,

  "REMEMBER": """
    Your email response must follow this structure:

   
    1. If no issues are found: Confirm the invoice with the invoice number and total amount.
    2. If the total amount is incorrect: Respond with "The total amount of the invoice generated is incorrect."
   
    Make sure the response reflects the tone and style of the examples provided.
  """
}


Utterances_prompt={
    "SYSTEM":"""You are tasked with generating natural language utterances for various intents to help train a chatbot or a natural language processing model. For each given intent, generate a list of 5 diverse utterances that a user might say to express that intent. Ensure that the utterances cover a range of phrasing and vocabulary, and are representative of how users might naturally communicate.""",
    "CONTEXT":"""
    Description about Intent:{description}
    Intent Provided:{intent}""",
"DISPLAY": """
Provide the output in the following JSON format without triple quotes:
{{
    "response": "[list of 5 utterances]"
}}
""",
"REMEMBER":""""""

}

SUMMARY_PROMPT = {
    "SYSTEM": """You are a summarization bot. Your task is to create a concise summary of the given EMAIL which can be maximum of 50 to 60 words. 
      RULE: 
      - Generate a summary that captures the main points and essential details.
      - Retain important information such as order ID, tracking ID, shipping ID, or specified days.
      """,
    "CONTEXT": """Please provide a complete summary that contains all details from the given email, including expressions of gratitude or other emotions. Also, include the names of individuals mentioned in the email.
    EMAIL: 
    {email}
    """,
    "DISPLAY": """
      Provide the output in the following JSON format:
      {{
        "email_summary": "[complete summary]"
      }}
      """,
    "REMEMBER": """Please provide a complete summary"""
}


INTENT_CLASSIFICATION_PROMPT_FOR_EVENT_HANDLER =""" 
You are an intent identification bot. Based on the CONVERSATION HISTORY, determine the Bot’s likely response and identify the intent of the bot’s likely response.     

  1. Determine bot’s likely response based on the CONVERSATION HISTORY and user’s latest message, then set the bot_likely_response accordingly.   
  2. Sometimes user may answer bot’s question directly with requirement information without any description or what the information refers to. Please use bot’s question or CONVERSATION HISTORY to understand user’s message.      
  3. Identify the intent of the bot_likely_response by following the instructions given.    
  4. If the bot's likely response matches more than one intent, please provide the intent that most closely matches.     
  5. Look into SAMPLE INTENT IDENTIFICATION EXAMPLES for additional context.
        
The identified intent should be selected from the list of INTENTS below. 
    {intent_details}

OTHERS: 
 - If the email content mentions multiple INTENTS or falls outside the scope of the above INTENTS, classify it as "OTHERS."
	
SAMPLE INTENT IDENTIFICATION EXAMPLES: 
{examples} 

Display instructions: 
Ensure that the output is in the following JSON format exactly as shown: 
    { 
      "intent": "[Main Intent Classified]",
      "bot_likely_response": "[bot likely response]", 
      "last_message": "[last message]", 
      "reason": "[explanation for the intent classification]" 
    }  
        
Remember:  
Prioritize the body for intent classification. classify it accordingly based on that context. Return the intents of the bot's likely response. Follow each intent description. """


SUB_INTENT_CLASSIFICATION_PROMPT_FOR_SUB_INTENT_CLASSIFICATION = """
You are a sub intent identification bot for {intent_name}. Based on the CONVERSATION HISTORY , determine the Bot's likely response and identify the sub intent of the bot's likely response for {intent_name} intent.   
 
1. Determine Bot's likely response based on the CONVERSATION HISTORY and user's latest message and set bot_likely_response with that response.   
2. Sometimes user may answer bot's question directly with required information without any description or what the information refers to. Please use bot's question or CONVERSATION HISTORY to understand user's message.   
3. If the bot's likely response matches more than one sub intent, please provide the sub intent that most closely matches along with a similarity score.        
4. Look into SAMPLE SUB INTENT IDENTIFICATION EXAMPLES for additional context.
 
The identified sub_intent should be selected from the list of SUB_INTENTS below: 
{sub_intent_details}

OTHERS: 
 - If the email content mentions multiple SUB_INTENTS or falls outside the scope of the above SUB_INTENTS, classify it as "OTHERS."
 
SAMPLE SUB INTENT IDENTIFICATION EXAMPLES:
{examples}
 
Display instructions: 
Ensure that the output is in the following JSON format exactly as shown: 
    {
      "sub_intent": "[Sub Intent Classified]", 
      "bot_likely_response": "[bot likely response]", 
      "last_message": "[last message]", 
      "reason": "[explanation for the sub intent classification]" 
    }
    
Remember:  
Prioritize the body for intent classification. classify it accordingly based on that context. Return the sub intent of the bot's likely response. Follow each intent description. """
from enum import Enum


class Prompt(Enum):
    SYSTEM = "SYSTEM"
    CONTEXT = "CONTEXT"
    DISPLAY = "DISPLAY"
    REMEMBER = "REMEMBER"
