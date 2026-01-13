from __future__ import annotations
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI


class ProviderLike:
    code: str


class ModelApiKeyLike:
    provider: ProviderLike
    purpose: Any | None
    api_key: str | None
    endpoint_url: str | None
    extra: dict[str, Any] | None


def get_chat_model(
    model_name: str, model_api_key: ModelApiKeyLike, **kwargs: Any
) -> BaseChatModel:
    """
    Summary: 제공자별 ChatModel 클라이언트를 생성합니다.

    Contract:
        - provider.code와 purpose.code="chat"이 필요합니다.
        - OpenAI/Azure OpenAI만 지원합니다.

    Args:
        model_name: 모델명 또는 배포명.
        model_api_key: 제공자/키/엔드포인트 정보를 가진 객체.
        **kwargs: temperature/timeout 등 공통 옵션.

    Returns:
        BaseChatModel: LangChain ChatModel 인스턴스.

    Raises:
        ValueError: 필수 정보 누락 또는 미지원 제공자.
    """
    provider = getattr(model_api_key.provider, "code", None)
    if not provider:
        raise ValueError("model_api_key.provider.code 가 필요합니다.")

    if not (
        getattr(model_api_key, "purpose", None)
        and getattr(model_api_key.purpose, "code", None) == "chat"
    ):
        raise ValueError("purpose.code 가 'chat' 인 키만 사용할 수 있습니다.")

    if provider == "openai":
        if not model_api_key.api_key:
            raise ValueError("OpenAI Chat: api_key 필요")
        return ChatOpenAI(model=model_name, api_key=model_api_key.api_key, **kwargs)

    if provider == "azure_openai":
        if not (model_api_key.api_key and model_api_key.endpoint_url):
            raise ValueError("Azure OpenAI Chat: api_key/endpoint_url 필요")
        api_version = (model_api_key.extra or {}).get("api_version")
        if not api_version:
            raise ValueError("Azure OpenAI Chat: extra.api_version 필요")
        return AzureChatOpenAI(
            model=model_name,
            api_key=model_api_key.api_key,
            azure_endpoint=model_api_key.endpoint_url,
            api_version=api_version,
            **kwargs,
        )

    raise ValueError(f"지원하지 않는 provider: {provider}")
