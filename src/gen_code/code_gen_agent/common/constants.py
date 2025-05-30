from types import MappingProxyType
from typing import Mapping

# 定数名は慣習に従い大文字のスネークケースにします。
# この辞書がエージェント名と生成コードのキーをマッピングしていると仮定して命名します。
AGENT_STATE_KEYS: Mapping[str, str] = MappingProxyType({
    "CodeWriterAgent": "generated_code",
    "CodeRefactorerAgent": "refactored_code",
})
