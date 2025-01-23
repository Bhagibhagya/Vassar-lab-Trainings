import logging

from langchain.agents import tool

logger = logging.getLogger(__name__)


def tools():
    @tool
    def get_intents():
        """ Use this tool to fetch intent and its description """
        intent_desc = {
            "Order Status": "Queries about the status of an order, including delivery tracking, estimated arrival times, or shipment inquiries.",
            "Product Information": "Questions regarding product details, specifications, availability, compatibility, or features.",
            "Payments": "Queries related to making payments, payment methods, billing issues, transaction problems, or invoices.",
            "Returns": "Requests or questions about returning a product, return policies, procedures, or exchange options.",
            "Feedback": "User comments, reviews, or general feedback about products, services, or experiences.",
            "Generic Flow": "Queries that are the common conversation that will come under the Generic Flow.",
            "Intent Not Identified": "Queries that cannot be categorized into any predefined intent and do not fit under 'Intent Not Identified'."
        }
        return intent_desc

    return [get_intents]
