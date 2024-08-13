import asyncio
import shutil
import warnings

import uvloop
from graphrag.index import create_pipeline_config
from graphrag.index.run import run_pipeline_with_config

from .common import create_graphrag_config_from_yaml

warnings.filterwarnings("ignore")


def create(
    root: str,
    api_key: str,
    llm_model: str,
    config_path: str = "config/graphrag.yaml",
):
    """Run the pipeline with the given config."""
    run_id = "default"
    _ = shutil.copytree("data/graphrag/prompts", f"{root}/prompts", dirs_exist_ok=True)

    graphrag_config = create_graphrag_config_from_yaml(
        root, config_path, api_key, llm_model
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
