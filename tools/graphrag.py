import asyncio
import shutil
import warnings

import pandas as pd
import uvloop
import yaml
from graphrag.config import create_graphrag_config
from graphrag.index import PipelineConfig, create_pipeline_config
from graphrag.index.run import run_pipeline_with_config
from graphrag.query.factories import get_global_search_engine
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_reports,
)

warnings.filterwarnings("ignore")


class GraphStore:
    def __init__(self, config_path: str = "config/graphrag.yaml"):
        self.config_path = config_path

    def create(
        self,
        root: str,
        api_key: str,
        llm_model: str,
    ):
        """Run the pipeline with the given config."""
        run_id = "default"
        _ = shutil.copytree(
            "data/graphrag/prompts", f"{root}/prompts", dirs_exist_ok=True
        )

        graphrag_config: str | PipelineConfig = _create_graphrag_config(
            root, self.config_path, api_key, llm_model
        )
        pipeline_config = create_pipeline_config(graphrag_config)

        def _run_workflow_async() -> None:
            async def execute():
                async for output in run_pipeline_with_config(
                    pipeline_config,
                    run_id=run_id,
                ):
                    if output.errors and len(output.errors) > 0:
                        return

            uvloop.install()

            asyncio.run(execute())

        _run_workflow_async()

    def _create_default_config(
        self,
        root_dir: str,
        api_key: str,
        llm_model: str,
    ) -> PipelineConfig:
        """Overlay default values on an existing config or create a default config if none is provided."""
        with open(self.config_path, "rb") as file:
            content = file.read().decode(encoding="utf-8", errors="strict")
            content = content.replace("${OPENAI_API_KEY}", api_key)
            content = content.replace("${LLM_MODEL}", llm_model)
            data = yaml.safe_load(content)
            parameters = create_graphrag_config(data, root_dir)

        result = create_pipeline_config(parameters)
        return result


graph_store = GraphStore()


class GlobalSearch:
    def __init__(self, config_path: str = "config/graphrag.yaml"):
        self.config_path = config_path

    def create(
        self,
        root: str,
        api_key: str,
        llm_model: str,
    ):
        """Run a global search with the given query."""
        config = _create_graphrag_config(root, self.config_path, api_key, llm_model)

        data_dir = f"{root}/output/default/artifacts"
        final_nodes: pd.DataFrame = pd.read_parquet(
            f"{data_dir}/create_final_nodes.parquet"
        )
        final_entities: pd.DataFrame = pd.read_parquet(
            f"{data_dir}/create_final_entities.parquet"
        )
        final_community_reports: pd.DataFrame = pd.read_parquet(
            f"{data_dir}/create_final_community_reports.parquet"
        )

        reports = read_indexer_reports(final_community_reports, final_nodes, 2)
        entities = read_indexer_entities(final_nodes, final_entities, 2)
        return get_global_search_engine(
            config,
            reports=reports,
            entities=entities,
            response_type="multiple paragraphs",
        )


def _create_graphrag_config(root_dir, config_path: str, api_key, llm_model):
    with open(config_path, "rb") as file:
        import yaml

        content = file.read().decode(encoding="utf-8", errors="strict")
        content = content.replace("${OPENAI_API_KEY}", api_key)
        content = content.replace("${LLM_MODEL}", llm_model)
        data = yaml.safe_load(content)
        return create_graphrag_config(data, root_dir)


global_search = GlobalSearch()
