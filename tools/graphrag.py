import asyncio
import shutil
import time
import warnings
from typing import Any

import pandas as pd
import tiktoken
import uvloop
import yaml
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from graphrag.config import (
    GraphRagConfig,
    LLMType,
    create_graphrag_config,
)
from graphrag.index import PipelineConfig, create_pipeline_config
from graphrag.index.run import run_pipeline_with_config
from graphrag.model import (
    CommunityReport,
    Entity,
)
from graphrag.query.context_builder.builders import GlobalContextBuilder
from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_reports,
)
from graphrag.query.llm.base import BaseLLM
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.llm.text_utils import num_tokens
from graphrag.query.structured_search.base import SearchResult
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch

DEFAULT_MAP_LLM_PARAMS = {
    "max_tokens": 1000,
    "temperature": 0.0,
}

DEFAULT_REDUCE_LLM_PARAMS = {
    "max_tokens": 2000,
    "temperature": 0.0,
}
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


class GraphRAG:
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
        self.search_engine = get_global_search_engine(
            config,
            reports=reports,
            entities=entities,
            response_type="multiple paragraphs",
        )

    def chat(self, query):
        result = self.search_engine.search(query)
        return result


def _create_graphrag_config(root_dir, config_path: str, api_key, llm_model):
    with open(config_path, "rb") as file:
        import yaml

        content = file.read().decode(encoding="utf-8", errors="strict")
        content = content.replace("${OPENAI_API_KEY}", api_key)
        content = content.replace("${LLM_MODEL}", llm_model)
        data = yaml.safe_load(content)
        return create_graphrag_config(data, root_dir)


def get_llm(config: GraphRagConfig) -> ChatOpenAI:
    """Get the LLM client."""
    is_azure_client = (
        config.llm.type == LLMType.AzureOpenAIChat
        or config.llm.type == LLMType.AzureOpenAI
    )
    debug_llm_key = config.llm.api_key or ""
    llm_debug_info = {
        **config.llm.model_dump(),
        "api_key": f"REDACTED,len={len(debug_llm_key)}",
    }
    if config.llm.cognitive_services_endpoint is None:
        cognitive_services_endpoint = "https://cognitiveservices.azure.com/.default"
    else:
        cognitive_services_endpoint = config.llm.cognitive_services_endpoint
    print(f"creating llm client with {llm_debug_info}")  # noqa T201
    return ChatOpenAI(
        api_key=config.llm.api_key,
        azure_ad_token_provider=(
            get_bearer_token_provider(
                DefaultAzureCredential(), cognitive_services_endpoint
            )
            if is_azure_client and not config.llm.api_key
            else None
        ),
        api_base=config.llm.api_base,
        organization=config.llm.organization,
        model=config.llm.model,
        api_type=OpenaiApiType.AzureOpenAI if is_azure_client else OpenaiApiType.OpenAI,
        deployment_name=config.llm.deployment_name,
        api_version=config.llm.api_version,
        max_retries=config.llm.max_retries,
    )


def get_global_search_engine(
    config: GraphRagConfig,
    reports: list[CommunityReport],
    entities: list[Entity],
    response_type: str,
):
    """Create a global search engine based on data + configuration."""
    token_encoder = tiktoken.get_encoding(config.encoding_model)
    gs_config = config.global_search

    return GlobalSearch2(
        llm=get_llm(config),
        context_builder=GlobalCommunityContext(
            community_reports=reports, entities=entities, token_encoder=token_encoder
        ),
        token_encoder=token_encoder,
        max_data_tokens=gs_config.data_max_tokens,
        map_llm_params={
            "max_tokens": gs_config.map_max_tokens,
            "temperature": gs_config.temperature,
            "top_p": gs_config.top_p,
            "n": gs_config.n,
        },
        reduce_llm_params={
            "max_tokens": gs_config.reduce_max_tokens,
            "temperature": gs_config.temperature,
            "top_p": gs_config.top_p,
            "n": gs_config.n,
        },
        allow_general_knowledge=False,
        json_mode=False,
        context_builder_params={
            "use_community_summary": False,
            "shuffle_data": True,
            "include_community_rank": True,
            "min_community_rank": 0,
            "community_rank_name": "rank",
            "include_community_weight": True,
            "community_weight_name": "occurrence weight",
            "normalize_community_weight": True,
            "max_tokens": gs_config.max_tokens,
            "context_name": "Reports",
        },
        concurrent_coroutines=gs_config.concurrency,
        response_type=response_type,
    )


class GlobalSearch2(GlobalSearch):
    def __init__(
        self,
        llm: BaseLLM,
        context_builder: GlobalContextBuilder,
        token_encoder: tiktoken.Encoding | None = None,
        response_type: str = "multiple paragraphs",
        allow_general_knowledge: bool = False,
        json_mode: bool = True,
        max_data_tokens: int = 8000,
        map_llm_params: dict[str, Any] = DEFAULT_MAP_LLM_PARAMS,
        reduce_llm_params: dict[str, Any] = DEFAULT_REDUCE_LLM_PARAMS,
        context_builder_params: dict[str, Any] | None = None,
        concurrent_coroutines: int = 32,
    ):
        super().__init__(
            llm=llm,
            context_builder=context_builder,
            token_encoder=token_encoder,
            max_data_tokens=max_data_tokens,
            map_llm_params=map_llm_params,
            reduce_llm_params=reduce_llm_params,
            allow_general_knowledge=allow_general_knowledge,
            json_mode=json_mode,
            context_builder_params=context_builder_params,
            concurrent_coroutines=concurrent_coroutines,
            response_type=response_type,
        )

    async def asearch(
        self,
        query: str,
        conversation_history: ConversationHistory | None = None,
        **kwargs: Any,
    ):
        """
        Perform a global search.

        Global search mode includes two steps:

        - Step 1: Run parallel LLM calls on communities' short summaries to generate answer for each batch
        - Step 2: Combine the answers from step 2 to generate the final answer
        """
        # Step 1: Generate answers for each batch of community short summaries
        start_time = time.time()
        context_chunks, context_records = self.context_builder.build_context(
            conversation_history=conversation_history, **self.context_builder_params
        )

        if self.callbacks:
            for callback in self.callbacks:
                callback.on_map_response_start(context_chunks)  # type: ignore
        map_responses = await asyncio.gather(
            *[
                self._map_response_single_batch(
                    context_data=data, query=query, **self.map_llm_params
                )
                for data in context_chunks
            ]
        )
        if self.callbacks:
            for callback in self.callbacks:
                callback.on_map_response_end(map_responses)
        map_llm_calls = sum(response.llm_calls for response in map_responses)
        map_prompt_tokens = sum(response.prompt_tokens for response in map_responses)

        # Step 2: Combine the intermediate answers from step 2 to generate the final answer
        reduce_response = await self._reduce_response(
            map_responses=map_responses,
            query=query,
            **self.reduce_llm_params,
        )

        return reduce_response

    async def _reduce_response(
        self,
        map_responses: list[SearchResult],
        query: str,
        **llm_kwargs,
    ):
        """Combine all intermediate responses from single batches into a final answer to the user query."""
        text_data = ""
        search_prompt = ""
        start_time = time.time()
        try:
            # collect all key points into a single list to prepare for sorting
            key_points = []
            for index, response in enumerate(map_responses):
                if not isinstance(response.response, list):
                    continue
                for element in response.response:
                    if not isinstance(element, dict):
                        continue
                    if "answer" not in element or "score" not in element:
                        continue
                    key_points.append(
                        {
                            "analyst": index,
                            "answer": element["answer"],
                            "score": element["score"],
                        }
                    )

            # filter response with score = 0 and rank r esponses by descending order of score
            filtered_key_points = [
                point
                for point in key_points
                if point["score"] > 0  # type: ignore
            ]

            if len(filtered_key_points) == 0 and not self.allow_general_knowledge:
                # return no data answer if no key points are found
                return query

            filtered_key_points = sorted(
                filtered_key_points,
                key=lambda x: x["score"],  # type: ignore
                reverse=True,  # type: ignore
            )

            data = []
            total_tokens = 0
            for point in filtered_key_points:
                formatted_response_data = []
                formatted_response_data.append(
                    f'----Analyst {point["analyst"] + 1}----'
                )
                formatted_response_data.append(
                    f'Importance Score: {point["score"]}'  # type: ignore
                )
                formatted_response_data.append(point["answer"])  # type: ignore
                formatted_response_text = "\n".join(formatted_response_data)
                if (
                    total_tokens
                    + num_tokens(formatted_response_text, self.token_encoder)
                    > self.max_data_tokens
                ):
                    break
                data.append(formatted_response_text)
                total_tokens += num_tokens(formatted_response_text, self.token_encoder)
            text_data = "\n\n".join(data)

            search_prompt = self.reduce_system_prompt.format(
                report_data=text_data, response_type=self.response_type
            )
            if self.allow_general_knowledge:
                search_prompt += "\n" + self.general_knowledge_inclusion_prompt
            return f"{search_prompt}---User Questions---\n\n{query}"

        except Exception:
            return 0


graph_rag = GraphRAG()
