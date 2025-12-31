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
    엔드포인트 기반 ChatModel 생성. (자체 서빙 X)
    - model_name: 공급자 모델/배포명 (OpenAI: "gpt-4o-mini", Azure: 배포명)
    - model_api_key: 미리 로드된 ModelApiKey (관계 .provider.code 접근 가능해야 함)
    - kwargs: temperature / timeout 등 모델 공통 옵션
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
