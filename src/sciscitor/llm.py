"""The only module that knows about langchain."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .config import Config

ChatFactory = Callable[[Config, "str | None"], Any]


def build_chat_model(config: Config, model: str | None = None) -> ChatOpenAI:
    """Create a client for any OpenAI-compatible endpoint."""
    return ChatOpenAI(
        model=model or config.model,
        base_url=config.base_url,
        api_key=config.api_key,
    )


def chunk_text(chunk: Any) -> str:
    """Return the text carried by one streamed chunk.

    langchain types content as ``str | list[str | dict]`` but cannot enforce it:
    a provider answering ``null`` or sending a single block would otherwise kill
    the stream or silently drop text, so anything else is normalized first.
    """
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if not content:  # None, or nothing left to read
        return ""

    blocks = content if isinstance(content, (list, tuple)) else [content]
    parts: list[str] = []
    for block in blocks:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts)


async def stream_reply(
    config: Config,
    prompt: str,
    model: str | None = None,
    *,
    chat_factory: ChatFactory = build_chat_model,
) -> AsyncIterator[str]:
    """Yield the answer piece by piece as the endpoint produces it."""
    chat = chat_factory(config, model)
    async for chunk in chat.astream([HumanMessage(content=prompt)]):
        text = chunk_text(chunk)
        if text:
            yield text


async def stream_answer(
    config: Config,
    prompt: str,
    model: str | None,
    on_piece: Callable[[str], None],
    *,
    chat_factory: ChatFactory = build_chat_model,
) -> str:
    """Consume the reply, handing every piece to on_piece, and return all of it.

    Cancelling the surrounding task aborts the request; pieces already handed to
    on_piece stay with the caller, which is what the window keeps showing.
    """
    answer = ""
    async for piece in stream_reply(config, prompt, model, chat_factory=chat_factory):
        answer += piece
        on_piece(piece)
    return answer
