from django.test import TestCase
from unittest.mock import patch, MagicMock
import json
from EmailApp.Services.wise_flow import (
    WiseFlow,
)  # Adjust this import based on your actual module structure


class TestFlow(TestCase):

    @patch("DatabaseApp.models.Step.objects")  # Mock the Step model
    def test_workflow_execution(self, MockStep):
        # Define the mock steps data
        start_step = MagicMock()
        start_step.step_uuid = "start_step_uuid"
        start_step.step_type = "start"
        start_step.workflow_uuid = "test_workflow_uuid"
        start_step.step_details_json = {
            "code": {
                "module": "EmailApp.Services.email_classification_service",
                "class": "EmailClassificationService",
                "method": "initialize_flow",
                "params": {
                    "customer_uuid": "test_customer_uuid",
                    "conversation_uuid": "test_conversation_uuid",
                },
            },
            "next_step": "next_step_uuid",
        }

        end_step = MagicMock()
        end_step.step_uuid = "next_step_uuid"
        end_step.step_type = "end"
        end_step.step_details_json = {}  # Ensure this is JSON serialized

        # Set up the mock return values for database queries
        MockStep.filter.return_value.first.side_effect = [start_step, end_step]

        # Instantiate the Flow class and trigger the workflow
        flow = WiseFlow()
        flow.trigger_work_flow(workflow_uuid="test_workflow_uuid")

        # Assertions
        MockStep.filter.assert_any_call(
            step_type="start", workflow_uuid="test_workflow_uuid"
        )
        MockStep.filter.assert_any_call(step_uuid="next_step_uuid")
        self.assertEqual(
            start_step.step_details_json["params"]["customer_uuid"],
            "test_customer_uuid",
        )
        self.assertEqual(
            start_step.step_details_json["params"]["conversation_uuid"],
            "test_conversation_uuid",
        )
