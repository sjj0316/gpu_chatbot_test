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
    """
    Why: provider_code별 임베딩 팩토리를 등록하는 데코레이터를 제공합니다.

    Args:
        provider_code: 제공자 코드.

    Returns:
        Callable: 팩토리 등록 데코레이터.
    """

    def deco(fn: Factory) -> Factory:
        _FACTORIES[provider_code.lower()] = fn
        return fn

    return deco


@register_factory("openai")
def _build_openai(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    """
    Why: OpenAI 임베딩 클라이언트를 생성합니다.

    Raises:
        ValueError: api_key가 없을 때.
    """
    from langchain_openai import OpenAIEmbeddings

    if not key.api_key:
        raise ValueError("OpenAIEmbeddings: api_key가 필요합니다.")
    return OpenAIEmbeddings(
        model=model_name,
        api_key=key.api_key,
    )


@register_factory("azure_openai")
def _build_azure_openai(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    """
    Why: Azure OpenAI 임베딩 클라이언트를 생성합니다.

    Raises:
        ValueError: api_key/endpoint/api_version 누락.
    """
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
    Summary: HuggingFace 임베딩 클라이언트를 생성합니다.

    Contract:
        - 로컬 sentence-transformers 우선(키 없이 가능).
        - 실패 시 HF Inference API로 폴백(키 필요).
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
    """
    Why: Cohere 임베딩 클라이언트를 생성합니다.

    Raises:
        ValueError: api_key가 없을 때.
    """
    from langchain_cohere import CohereEmbeddings

    if not key.api_key:
        raise ValueError("CohereEmbeddings: api_key가 필요합니다.")
    return CohereEmbeddings(
        model=model_name,
        cohere_api_key=key.api_key,
    )


@register_factory("voyage")
def _build_voyage(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    """
    Why: Voyage 임베딩 클라이언트를 생성합니다.

    Raises:
        ValueError: api_key가 없을 때.
    """
    from langchain_community.embeddings import VoyageEmbeddings

    if not key.api_key:
        raise ValueError("VoyageEmbeddings: api_key가 필요합니다.")
    return VoyageEmbeddings(
        model=model_name,
        voyage_api_key=key.api_key,
    )


@register_factory("ollama")
def _build_ollama(model_name: str, key: ModelApiKeyLike) -> Embeddings:
    """
    Why: 로컬 Ollama 임베딩 클라이언트를 생성합니다.

    Contract:
        - endpoint가 없으면 기본값을 사용합니다.
    """
    from langchain_community.embeddings import OllamaEmbeddings

    return OllamaEmbeddings(
        model=model_name,
        base_url=getattr(key, "endpoint", None) or None,
    )


def get_embedding(model_name: str, model_api_key: ModelApiKeyLike) -> Embeddings:
    """
    Summary: model_name과 모델 키 정보로 적절한 임베딩 클라이언트를 반환합니다.

    Contract:
        - model_api_key.provider.code와 purpose="embedding"이 필요합니다.

    Args:
        model_name: 임베딩 모델명.
        model_api_key: 제공자/목적/키 정보를 가진 객체.

    Returns:
        Embeddings: LangChain 임베딩 클라이언트.

    Raises:
        ValueError: provider_code/purpose 불일치 또는 미지원 제공자.
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
