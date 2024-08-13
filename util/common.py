import yaml
from graphrag.config import (
    create_graphrag_config,
)
from graphrag.config.models import GraphRagConfig


def create_graphrag_config_from_yaml(
    root_dir: str, config_path: str, api_key: str, llm_model: str
) -> GraphRagConfig:
    with open(config_path, "rb") as file:
        content = file.read().decode(encoding="utf-8", errors="strict")
        content = content.replace("${OPENAI_API_KEY}", api_key)
        content = content.replace("${LLM_MODEL}", llm_model)
        data = yaml.safe_load(content)
        return create_graphrag_config(data, root_dir)
