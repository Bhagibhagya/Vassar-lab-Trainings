from dataclasses import field, dataclass
from typing import Optional, List, Dict, get_args, get_origin
from pydantic import BaseModel
from rest_framework import status

from ConnectedCustomerPlatform.exceptions import CustomException
from Platform.constant.error_messages import ErrorMessages
from Platform.constant import constants

from typing import Any

@dataclass
class PromptTemplateDetailsJson:
    system_prompt: str
    context_prompt: str
    display_prompt: str
    remember_prompt: str


@dataclass
class PromptDetailsJson:
    prompt_template_uuid: str
    system_prompt: str
    context_prompt: Optional[str] = field(default=None)
    display_prompt: Optional[str] = field(default=None)
    remember_prompt: Optional[str] = field(default=None)


@dataclass
class DimensionTypeDetailsJson:
    description: str

    @staticmethod
    def create(data):
        return DimensionTypeDetailsJson(**data)

@dataclass
class DimensionDetailsJson:
    description: str

    @staticmethod
    def create(data):
        return DimensionDetailsJson(**data)



@dataclass
class ParameterJson:
    name: str
    description: str
    type: str


@dataclass
class CodeDetailsJson:
    customer_uuid: str
    code: str
    response_type: str
    handle_error: Optional[str] = field(default=None)
    parameter: List[ParameterJson] = field(default_factory=list)


@dataclass
class CustomerClientDetailsJson:
    email: str
    address: str

@dataclass
class ClientUserInfoJson:
    domain: str
    address: str


@dataclass
class EmailExtractorDimesionDetailsJson:
    customer_client_uuid: str
    customer_client_tier_uuid: str

    def __post_init__(self):
        if not self.customer_client_uuid:
            raise CustomException(ErrorMessages.CUSTOMER_ID_NOT_NULL, status_code=status.HTTP_400_BAD_REQUEST)
        if not self.customer_client_tier_uuid:
            raise CustomException(ErrorMessages.CUSTOMER_CLIENT_TIER_UUID_NOT_NULL,
                                  status_code=status.HTTP_400_BAD_REQUEST)

class MainMessage(BaseModel):
    message: str
    font_family: str
    font_size: int
    color: str
    text_align: str

class SubMessage(BaseModel):
    message: str
    font_family: str
    font_size: int
    color: str
    text_align: str

class WelcomeMessage(BaseModel):
    main_message: MainMessage
    sub_message: SubMessage

class PanelConfiguration(BaseModel):
    width: int
    height: int
    has_box_shadow: bool
    welcome_message: WelcomeMessage
    assistance_message: str
    default_intents: List[str]
    input_box: str

class HomeScreenConfiguration(BaseModel):
    background_fill_type: str
    background_color: str
    logo: str
    logo_width: int
    logo_height: int
    show_logo: bool
    show_home_button: bool
    show_history_button: bool
    show_close_button: bool

class BubbleConfiguration(BaseModel):
    bubble_type: str
    bubble_animation_type: str
    bubble_icon_type: int
    custom_bubble_icon: Optional[str] = None
    animation_duration: int
    background_color: str
    text_color: str
    label_style: str

class LandingPageConfiguration(BaseModel):
    bubble_configuration: BubbleConfiguration
    home_screen_configuration: HomeScreenConfiguration
    panel_configuration: PanelConfiguration

class LandingPageData(BaseModel):
    landing_page_configuration: LandingPageConfiguration

    # Intent Page Data
class ChatAvatar(BaseModel):
    avatar: str
    avatar_shape: str
    avatar_type: str
    gender: str

class Header(BaseModel):
    title: str
    text_color: str
    background_fill_type: str
    background_color: str
    show_logo: bool
    show_close_button: bool
    enable_mute: bool

class BotMessage(BaseModel):
    background_color: str
    text_color: str
    typing_indicator: str
    is_speech_enabled: bool
    voice: str
    suggestion_button_styles: str

class UserMessage(BaseModel):
    background_color: str
    text_color: str
    delivery_status: bool

class Footer(BaseModel):
    enable_attachments: bool
    enable_text: bool
    enable_speech: bool
    enable_send: bool

class IntentPagePanelConfiguration(BaseModel):
    width: int
    height: int
    has_header: bool
    has_box_shadow: bool
    header: Header
    bot_message: BotMessage
    user_message: UserMessage
    footer: Footer

class IntentPageConfiguration(BaseModel):
    chat_avatar: ChatAvatar
    intent_page_panel_configuration: IntentPagePanelConfiguration

class IntentPageData(BaseModel):
    intent_page_configuration : IntentPageConfiguration

@dataclass
class EmailDetails:
    primary_email_address: str

    @staticmethod
    def create(data):
        return EmailDetails(**data)


@dataclass
class LLMConfigurationDetailsJson:
    llm_provider: str
    deployment_name: str
    model_name: str
    api_base: str
    api_type: str
    api_version: str
    api_key: Optional[str] = field(default=None)
