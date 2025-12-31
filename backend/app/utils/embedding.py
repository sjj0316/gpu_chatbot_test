from __future__ import annotations

from typing import Callable, Protocol, Any
from langchain_core.embeddings import Embeddings


class ProviderLike(Protocol):
    code: str


class ModelApiKeyLike(Protocol):
    provider: ProviderLike
    purpose: str
    api_key: str | None
    endpoint: str | None
    api_version: str | None
    organization: str | None
    extra: dict[str, Any] | None


Factory = Callable[[str, ModelApiKeyLike], Embeddings]
_FACTORIES: dict[str, Factory] = {}


def register_factory(provider_code: str):
    """provider_code → 팩토리 함수 매핑"""

    def deco(fn: Factory) -> Factory:
        _FACTORIES[provider_code.lower()] = fn
        return fn

    return deco


@register_factory("openai")
def _build_openai(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    from langchain_openai import OpenAIEmbeddings

    if not key.api_key:
        raise ValueError("OpenAIEmbeddings: api_key가 필요합니다.")
    return OpenAIEmbeddings(
        model=model_name,
        api_key=key.api_key,
    )


@register_factory("azure_openai")
def _build_azure_openai(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    from langchain_openai import AzureOpenAIEmbeddings

    if not key.api_key:
        raise ValueError("AzureOpenAIEmbeddings: api_key가 필요합니다.")
    if not getattr(key, "endpoint", None):
        raise ValueError("AzureOpenAIEmbeddings: endpoint가 필요합니다.")
    if not getattr(key, "api_version", None):
        raise ValueError("AzureOpenAIEmbeddings: api_version이 필요합니다.")
    return AzureOpenAIEmbeddings(
        model=model_name,  # 보통 Azure에선 'deployment name'
        api_key=key.api_key,
        azure_endpoint=key.endpoint,  # type: ignore[attr-defined]
        api_version=key.api_version,  # type: ignore[attr-defined]
    )


@register_factory("huggingface")
def _build_huggingface(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    """
    - 로컬 sentence-transformers 우선 (api_key 없어도 됨)
    - 미설치/실패 시 HF Inference API로 폴백 (api_key 필요)
    """
    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception:
        from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

        if not key.api_key:
            raise ValueError("HuggingFace Inference API: api_key가 필요합니다.")
        return HuggingFaceInferenceAPIEmbeddings(
            model_name=model_name,
            api_key=key.api_key,
        )


@register_factory("cohere")
def _build_cohere(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    from langchain_cohere import CohereEmbeddings

    if not key.api_key:
        raise ValueError("CohereEmbeddings: api_key가 필요합니다.")
    return CohereEmbeddings(
        model=model_name,
        cohere_api_key=key.api_key,
    )


@register_factory("voyage")
def _build_voyage(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    from langchain_community.embeddings import VoyageEmbeddings

    if not key.api_key:
        raise ValueError("VoyageEmbeddings: api_key가 필요합니다.")
    return VoyageEmbeddings(
        model=model_name,
        voyage_api_key=key.api_key,
    )


@register_factory("ollama")
def _build_ollama(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    from langchain_community.embeddings import OllamaEmbeddings

    return OllamaEmbeddings(
        model=model_name,
        base_url=getattr(key, "endpoint", None) or None,
    )


def get_embedding(model_name: str, model_api_key: ModelApiKeyLike) -> Embeddings:
    """
    DB 조회 없이, 주어진 model_name과 model_api_key(프로바이더/목적/키 정보)를 바탕으로
    올바른 LangChain Embeddings 인스턴스를 반환합니다.
    """
    if not getattr(model_api_key, "provider", None) or not getattr(
        model_api_key.provider, "code", None
    ):
        raise ValueError("model_api_key.provider.code가 필요합니다.")

    if getattr(model_api_key.purpose, "code", None) != "embedding":
        raise ValueError(f"purpose가 'embedding'이 아닙니다: {model_api_key.purpose!r}")

    provider_code = model_api_key.provider.code.lower()
    factory = _FACTORIES.get(provider_code)
    if not factory:
        raise ValueError(f"지원하지 않는 provider_code: {provider_code}")

    return factory(model_name, model_api_key)
