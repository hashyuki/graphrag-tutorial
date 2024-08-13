import asyncio
from typing import Any

import pandas as pd
import tiktoken
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
from graphrag.query.structured_search.global_search.search import (
    DEFAULT_MAP_LLM_PARAMS,
    DEFAULT_REDUCE_LLM_PARAMS,
    GlobalSearch,
)
from graphrag.query.structured_search.local_search.search import LocalSearch

from .common import create_graphrag_config_from_yaml


def create_global_search_engine(
    root: str,
    api_key: str,
    llm_model: str,
    config_path: str = "config/graphrag.yaml",
) -> GlobalSearch:
    """Run a global search with the given query."""
    config = create_graphrag_config_from_yaml(root, config_path, api_key, llm_model)

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
    token_encoder = tiktoken.get_encoding(config.encoding_model)
    gs_config = config.global_search
    return GlobalSearchForAssistantsAPI(
        llm=ChatOpenAI(
            api_key=api_key,
            model=llm_model,
            api_type=OpenaiApiType.OpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
            max_retries=20,
        ),
        context_builder=GlobalCommunityContext(
            community_reports=reports,
            entities=entities,
            token_encoder=token_encoder,
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
        response_type="multiple paragraphs",
    )


class GlobalSearchForAssistantsAPI(GlobalSearch):
    """
    AssistantsAPIを利用するために、最終的な入力を返却するように修正したGlobalSearch
    """

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
        # Step 1: Generate answers for each batch of community short summaries
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
        text_data = ""
        search_prompt = ""
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


class LocalSearchForAssistantsAPI(LocalSearch):
    # TODO
    pass
