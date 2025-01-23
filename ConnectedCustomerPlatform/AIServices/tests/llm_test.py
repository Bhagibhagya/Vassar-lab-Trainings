from django.test import TestCase

from AIServices.BOT.IntentSentimentClassification import IntentSentimentClassification
from AIServices.LLM.llm_chain import llm_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from AIServices.prompts.prompts import PURCHASE_ORDER_SUMMARY_RESPONSE, CHECK_PO_STATUS_SUMMARY_RESPONSE, \
    CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION_PROMPT, EMAIL_CONVERSATION_SUMMARY_PROMPT
from EmailApp.utils import validate_sensormatic_order_details, get_sensormatic_order_status
from EmailApp.constant.constants import INVENTORY_FILEPATH, ORDER_STATUS_FILEPATH
import json

class LLMTestCase(TestCase):
    def test_purcharse_order_response(self):
       
        prompt = PURCHASE_ORDER_SUMMARY_RESPONSE

        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT",""))
        ]
        
        # prompt_messages.append(HumanMessagePromptTemplate.from_template('{"question"}'))
        
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER","")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        llm_chain_instance = llm_chain(prompt=chat_prompt)

        json_data = json.loads("{\"purchaseorderinformation\": {\"purchaseOrderNumber\": \"73414\", \"orderDate\": \"4/11/2024\", \"eta\": \"4/12/2024\", \"currency\": \"USD\"}, \"buyerinformation\": {\"buyerName\": \"Axel Reyes\", \"buyerAddress\": \"Spencer Technologies, Inc, 10 Trotter Drive, Medway, MA 02053, US\", \"buyerContact\": {\"phone\": \"\", \"email\": \"APinvoice@spencertech.com\"}}, \"sellerinformation\": {\"sellerName\": \"Sensormatic\", \"sellerAddress\": \"6600 Congress Ave, ATTN: William Burkholder, Boca Raton, FL 33487, US\", \"sellerContact\": {\"phone\": \"\", \"email\": \"\"}}, \"orderdetails\": {\"items\": [{\"itemDescription\": \"Sensormatic SlimPad Deactivator, Universal Controller, Remote Alarm Module, Power Cord\", \"itemCode\": \"ZBSMP-SL\", \"quantity\": \"2\", \"unitPrice\": \"$707.25\", \"totalPrice\": \"$1414.50\"}, {\"itemDescription\": \"LABOR\", \"itemCode\": \"LABOR\", \"quantity\": \"1\", \"unitPrice\": \"$601.54\", \"totalPrice\": \"$601.54\"}], \"subTotal\": \"$2016.04\", \"tax\": \"\", \"totalAmount\": \"$2016.04\"}, \"shippinginformation\": {\"shippingAddress\": \"Academy Sports & Outdoors-69, 445 Forest Square St, Longview, TX 75605, US\", \"shippingInstructions\": \"\"}, \"additionalinformation\": {\"comments\": \"Please confirm price and del to procurement@spencertech.com\"}}")

        validate_order = validate_sensormatic_order_details(json_data=json_data,csv_file=INVENTORY_FILEPATH)

        # print(validate_order)

        customer_data = {"firstname": "Rohit"}

        result = llm_chain_instance.run(inputs={"question":validate_order,"customer_data":customer_data})

        # print(result)

        result_json = json.loads(result)

        print(result_json.get("response"))

    def test_check_po_status_response(self):
        prompt = CHECK_PO_STATUS_SUMMARY_RESPONSE

        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM","")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT",""))
        ]

        # prompt_messages.append(HumanMessagePromptTemplate.from_template('{"question"}'))

        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY","")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER","")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        llm_chain_instance = llm_chain(prompt=chat_prompt)

        validate_details = get_sensormatic_order_status({"purchase_order_id":"73414"}, ORDER_STATUS_FILEPATH)


        customer_data = {"firstname": "Rohit"}

        result = llm_chain_instance.run(inputs={"question":validate_details,"customer_data":customer_data})

        # print(result)

        result_json = json.loads(result)

        print(result_json.get('response'))


    def test_customer_and_geography_response(self):
        prompt = CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION_PROMPT

        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM", "")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT", ""))
        ]

        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY", "")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER", "")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        llm_chain_instance = llm_chain(prompt=chat_prompt)

        organizations = [
            "walgreen National",
            "tcs",
            "google",
            "sensormatic",
            "Rite Aid"
        ]

        json_object = {
            "organizations": organizations
        }

        # Convert to a JSON string for display or storage
        json_str = json.dumps(json_object, indent=4)
        #print("customers", customers)
        email_content = """
            This job has been rated UNSATISFACTORY by the store with the following comment:
            "We need the system to be replaced. Tech said he didn't know how to service our old model."
            Immediate attention is required; contact the store and update the work order notes ASAP. Status changed from
            Completed / Pending Confirmation to IN PROGRES/UNSATISFACTORY.
            Tracking #: 270046037
            Provider: Checkpoint Systems Inc
            Provider's Phone:8002537580
            Rite Aid
            Location: 03109 -1560 PARKMAN
            Address: 1560 PARKMAN ROAD NW WARREN OH 44485-2159 US
            Phone: 330-392-7555
            """

        result = llm_chain_instance.run(inputs={"existing_customers":{json_str},"email_content":{email_content}})

        print(result)

        result_json = json.loads(result)

        print("customer",result_json)
    def test_intent_and_sentiment_classification_response(self):
        email_content = """
        I placed an order (Order #12345) last week, and I wanted to inquire about the shipping status. Could you please provide me with an estimated delivery date?"
        """
        result = IntentSentimentClassification().query(email_content=email_content)

        print(result)
       
    def test_email_conversation_summary(self):
        prompt = EMAIL_CONVERSATION_SUMMARY_PROMPT

        prompt_messages = [
            SystemMessagePromptTemplate.from_template(prompt.get("SYSTEM", "")),
            HumanMessagePromptTemplate.from_template(prompt.get("CONTEXT", ""))
        ]

        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("DISPLAY", "")))
        prompt_messages.append(SystemMessagePromptTemplate.from_template(prompt.get("REMEMBER", "")))
        chat_prompt = ChatPromptTemplate.from_messages(prompt_messages)

        llm_chain_instance = llm_chain(prompt=chat_prompt)
        existing_email_thread="Walmart is inquiring about the delivery status of their order from Sensormatic Service, expressing concern over the delay after several days have passed since the order was placed."
        fr="Sensormatic service"
        to="walmart"
        current_email="Your order will be delivered soon,you can track your order with this tracking ID 2367823"
        result = llm_chain_instance.run(inputs={"previous_email_thread_summary":{existing_email_thread},"current_email":{current_email},"from":{fr},"to":{to}})
        result_json = json.loads(result)
        print(result_json)
