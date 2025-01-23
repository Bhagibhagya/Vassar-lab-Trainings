import importlib
import inspect
import logging
from asgiref.sync import sync_to_async
from typing import Any, Dict, List, Optional
from DBServices.models import EmailConversations, Step, WorkFlow
from EventHub.send_sync import EventHubProducerSync
# from EmailApp.constant.constants import ChannelTypesUUID

# Define the logger
logger = logging.getLogger(__name__)


# class

# def __init__(self) -> None:
#     logger.info(f"Initialized {__class__.__name__}")


def get_start_or_end_step(workflow_uuid, step_type):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.info(f"Fetching {step_type} step for workflow {workflow_uuid}")
    step = Step.objects.filter(step_type=step_type, workflow_uuid=workflow_uuid).first()
    if not step:
        logger.error(f"No {step_type} step found for workflow {workflow_uuid}")
        raise ValueError(f"No {step_type} step found for workflow {workflow_uuid}")
    return step


def get_step(step_uuid):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.info(f"Fetching step details for step UUID {step_uuid}")
    step = Step.objects.filter(step_uuid=step_uuid).first()
    if not step:
        logger.error(f"No step found with UUID {step_uuid}")
        raise ValueError(f"No step found with UUID {step_uuid}")
    return step


def resolve_params(params: dict, input_data: dict):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.debug(f"Defined Params : {params}, input_data: {input_data}")
    resolved_params = {}
    for key, value in params.items():
        if key in input_data:
            resolved_params[key] = input_data.get(key, value)
        elif value is not None:
            resolved_params[key] = value
        else:
            logger.error(f"Required input param {key} is missing")
            raise ValueError(f"Required input param {key} is missing")
    return resolved_params


def execute_function(module_name, type_, code, params):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.info(f"Executing {type_} {code.get('name')} in module {module_name} with params {params}")
    try:
        module = importlib.import_module(module_name)
        if type_ == "class":
            class_ = getattr(module, code['name'])
            constructor_params = resolve_params(code['constructor_params'], params)
            class_instance = class_(**constructor_params)
            method = getattr(class_instance, code['method']['name'])
            method_params = resolve_params(code['method']['params'], params)
            return method(**method_params)
        elif type_ == "function":
            _function = getattr(module, code['name'])
            function_params = resolve_params(code['params'], params)
            return _function(**function_params)
    except Exception as e:
        logger.error(f"Error executing {type_} {code.get('name')} in module {module_name}: {e}")
        raise


def execute_start_step(step, input_data):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.info(f"Executing start step with UUID {step.step_uuid}")
    return step.step_details_json['next_step_info'], input_data


def execute_process_step(step: Step, input_data):
    logger.info(f"Executing process step with UUID {step.step_uuid}")
    logger.debug(f"Input Data : {input_data}")
    code_details = step.step_details_json['code']
    module_name = code_details['module']
    type_ = code_details['type']
    code = code_details.get(type_, {})

    if not code:
        logger.error("Function or class missing in step details.")
        raise ValueError("Function or class missing in step details.")

    try:
        result = execute_function(module_name, type_, code, input_data)
    except Exception as e:
        logger.error(f"Error executing process step: {e}")
        raise ValueError(f"Error executing process step: {e}")

    logger.debug(f"Output: {result}")

    if result.get('status') == 'success':
        next_step_info = step.step_details_json['next_step_info']
        output_data = result.get('data')
        return next_step_info, output_data
    else:
        logger.error("Process step execution failed.")
        raise ValueError("Process step execution failed.")


def execute_decision_step(step: Step, input_data):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    logger.info(f"Executing decision step with UUID {step.step_uuid}")
    conditions = step.step_details_json['conditions']

    for condition in conditions:
        type_ = condition['type']
        try:
            if type_ == 'function':
                module_name = condition['module']
                code = condition.get('function', {})
                if not code:
                    logger.error("Function is missing in condition details.")
                    raise ValueError("Function is missing in condition details.")

                if execute_function(module_name=module_name, type_=type_, code=code, params=input_data):
                    logger.info(f"Condition met for function {code.get('name')}, proceeding to next step.")
                    return condition['next_step_info'], input_data
            else:
                if eval(condition['bool'], {}, {'x': input_data}):
                    logger.info("Condition met for boolean expression, proceeding to next step.")
                    return condition['next_step_info'], input_data
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            continue

    logger.warning("No condition met for decision step, proceeding to default next step if available.")
    return step.step_details_json.get('default_next_step_info'), input_data


def send_to_event_hub(next_step_info, output_data):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    next_step_uuid = next_step_info.get('uuid', '')
    next_event_hub = next_step_info.get('topic', '')
    producer = EventHubProducerSync(eventhub=next_event_hub)

    if isinstance(output_data, list):
        for next_step_params in output_data:
            next_event_data = {
                'step_uuid': next_step_uuid,
                'data': {
                    'params': next_step_params
                }
            }
            producer.send_event_data_batch(event_data=next_event_data)
    elif isinstance(output_data, dict):
        next_event_data = {
            'step_uuid': next_step_uuid,
            'data': {
                'params': output_data
            }
        }
        producer.send_event_data_batch(event_data=next_event_data)

    producer.close()


def update_status_in_email_conversation(step_uuid, step_name, output_data):
    conversation_uuid = output_data.get('conversation_uuid') if output_data else None
    if conversation_uuid:
        conversation = EmailConversations.objects.get(conversation_uuid=conversation_uuid)
        process_details = conversation.email_process_details
        if process_details is None:
            process_details = []
        process_details.append(
            {
                'step_uuid': step_uuid,
                'step_name': step_name,
                'output_data': output_data
            }
        )
        conversation.email_process_details = process_details
        conversation.save()


def process_steps(step: Step, input_data: Optional[Dict[str, Any]], topic=''):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    while True:
        try:
            if step.step_type == 'process':
                next_step_info, output_data = execute_process_step(step, input_data)
            elif step.step_type == 'decision':
                next_step_info, output_data = execute_decision_step(step, input_data)
            elif step.step_type == 'end':
                break
            else:
                logger.error(f"Unknown step type: {step.step_type}")
                raise ValueError(f"Unknown step type: {step.step_type}")

            if not next_step_info:
                logger.info(f"Next step is not defined for this step: {step.step_uuid}")
                break

            next_step_uuid = next_step_info['uuid']
            next_topic = next_step_info.get('topic', '')

            logger.debug(
                f"NextStepTopic: {next_topic}, CurrentStepTopic: {step.step_details_json.get('next_step_info', {}).get('topic', '')}")

            if next_topic != topic:
                send_to_event_hub(next_step_info, output_data)
                break

            if isinstance(output_data, list):
                for data in output_data:
                    update_status_in_email_conversation(step.step_uuid, step.step_name, data)
                    next_step = get_step(next_step_uuid)
                    process_steps(next_step, data, topic=topic)
                return

            update_status_in_email_conversation(step.step_uuid, step.step_name, output_data)
            step = get_step(next_step_uuid)
            input_data = output_data


        except Exception as e:
            logger.error(f"Error processing steps: {e}")
            raise ValueError(f"Error processing steps: {e}")

    logger.info(f"Step execution completed for step UUID {step.step_uuid}")
def start_wise_flow(customer_uuid: str, application_uuid:str, channel_type_uuid: str):
    logger.info(f"In {inspect.currentframe().f_code.co_name}")

    workflow = WorkFlow.objects.filter(customer_uuid=customer_uuid, application_uuid=application_uuid, channel_type_uuid=channel_type_uuid).first()

    if not workflow:
        logger.error(f"No workflow found for customer: {customer_uuid}, channel_type: {channel_type_uuid}")
        return None, None

    step = get_start_or_end_step(workflow_uuid=workflow.workflow_uuid, step_type='start')
    next_step_info = step.step_details_json['next_step_info']
    # input_data = step_params
    # next_step_info, output_data = execute_start_step(step, input_data)
    # input_data = output_data
    next_step_uuid = next_step_info['step_uuid']
    next_topic = next_step_info.get('topic', '')

    return next_step_uuid, next_topic


def continue_wiseflow_execution(step_uuid: str, data: Dict[str, Any], topic):
    logger.info(f" In {inspect.currentframe().f_code.co_name}")
    params = data.get('params', {})

    step = get_step(step_uuid)
    input_data = params
    process_steps(step, input_data, topic)