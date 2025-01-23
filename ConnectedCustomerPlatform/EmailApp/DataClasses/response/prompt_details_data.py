from dataclasses import dataclass

@dataclass
class PromptDetailData:
    display_prompt: str
    content_prompt: str
    remember_prompt: str
    system_prompt: str