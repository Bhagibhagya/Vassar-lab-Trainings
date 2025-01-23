import json
from dataclasses import dataclass, asdict, field
from typing import Any, Dict

@dataclass
class NextStepInfo:
    uuid: str
    topic: str

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'NextStepInfo':
        return NextStepInfo(
            uuid=data.get('uuid', ''),
            topic=data.get('topic', '')
        )

@dataclass
class StepDetailsJSON:
    code: Dict[str, Any]
    next_step_info: NextStepInfo = field(default_factory=NextStepInfo)

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'StepDetailsJSON':
        return StepDetailsJSON(
            code=data.get('code', {}),
            next_step_info=NextStepInfo.from_json(data.get('next_step_info', {}))
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'next_step_info': asdict(self.next_step_info)
        }