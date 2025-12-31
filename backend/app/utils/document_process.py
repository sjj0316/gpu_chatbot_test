import logging
import uuid

from fastapi import UploadFile
from langchain_community.document_loaders.parsers import (
    BS4HTMLParser,
    PDFPlumberParser,
)
from langchain_community.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain_community.document_loaders.parsers.msword import MsWordParser
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_core.documents.base import Blob, Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

LOGGER = logging.getLogger(__name__)

HANDLERS = {
    "application/pdf": PDFPlumberParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
    "text/markdown": TextParser(),
    "text/x-markdown": TextParser(),
    "application/msword": MsWordParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        MsWordParser()
    ),
}

SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())

MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
    handlers=HANDLERS,
    fallback_parser=None,
)


async def process_document(
    file: UploadFile,
    metadata: dict | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """업로드한 파일을 LangChain 문서로 가공합니다."""
    file_id = uuid.uuid4()
    contents = await file.read()

    mime_type = file.content_type or "text/plain"

    if mime_type == "application/octet-stream" and file.filename:
        filename_lower = file.filename.lower()
        if filename_lower.endswith(".md") or filename_lower.endswith(".markdown"):
            mime_type = "text/markdown"
        elif filename_lower.endswith(".txt"):
            mime_type = "text/plain"
        elif filename_lower.endswith(".html") or filename_lower.endswith(".htm"):
            mime_type = "text/html"
        elif filename_lower.endswith(".pdf"):
            mime_type = "application/pdf"
        elif filename_lower.endswith(".doc"):
            mime_type = "application/msword"
        elif filename_lower.endswith(".docx"):
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    blob = Blob(data=contents, mimetype=mime_type)
    docs = MIMETYPE_BASED_PARSER.parse(blob)

    if metadata:
        for doc in docs:
            if not hasattr(doc, "metadata") or not isinstance(doc.metadata, dict):
                doc.metadata = {}
            doc.metadata.update(metadata)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    split_docs = text_splitter.split_documents(docs)

    for idx, split_doc in enumerate(split_docs):
        if not hasattr(split_doc, "metadata") or not isinstance(
            split_doc.metadata, dict
        ):
            split_doc.metadata = {}

        split_doc.metadata.update(
            {
                "file_id": str(file_id),
                "chunk_index": idx,
                "source": file.filename,
            }
        )

    return split_docs
