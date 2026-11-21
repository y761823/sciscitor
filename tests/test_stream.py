"""Smoke tests for the streaming layer. Nothing here imports Qt."""

from __future__ import annotations

import asyncio
import os

import pytest

from sciscitor import llm
from sciscitor.config import Config, load_config


class FakeChunk:
    def __init__(self, content: object) -> None:
        self.content = content


class FakeChat:
    def __init__(self, pieces: list[object], delay: float = 0.0) -> None:
        self._pieces = pieces
        self._delay = delay

    async def astream(self, messages: list[object]):
        for piece in self._pieces:
            if self._delay:
                await asyncio.sleep(self._delay)
            yield FakeChunk(piece)


CONFIG = Config(base_url="http://127.0.0.1:1/v1", api_key="test", model="fake")


def factory(pieces: list[object], delay: float = 0.0) -> llm.ChatFactory:
    def build(config: Config, model: str | None) -> FakeChat:
        return FakeChat(pieces, delay)

    return build


async def test_stream_answer_collects_pieces():
    seen: list[str] = []

    answer = await llm.stream_answer(
        CONFIG, "hello", None, seen.append, chat_factory=factory(["Hel", "", "lo"])
    )

    assert answer == "Hello"
    assert seen == ["Hel", "lo"]


async def test_content_blocks_are_flattened():
    blocks = [{"type": "text", "text": "Hi"}, " there"]

    answer = await llm.stream_answer(
        CONFIG, "hello", None, lambda piece: None, chat_factory=factory([blocks])
    )

    assert answer == "Hi there"


async def test_null_content_is_skipped():
    answer = await llm.stream_answer(
        CONFIG, "hello", None, lambda piece: None, chat_factory=factory([None, "ok"])
    )

    assert answer == "ok"


async def test_single_block_outside_a_list_is_read():
    block = {"type": "text", "text": "Hi"}

    answer = await llm.stream_answer(
        CONFIG, "hello", None, lambda piece: None, chat_factory=factory([block])
    )

    assert answer == "Hi"


async def test_cancelled_request_keeps_partial_output():
    seen: list[str] = []
    task = asyncio.ensure_future(
        llm.stream_answer(
            CONFIG,
            "hello",
            None,
            seen.append,
            chat_factory=factory(["a", "b", "c"], delay=0.1),
        )
    )

    while not seen:
        await asyncio.sleep(0.01)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert seen == ["a"]


def test_defaults_when_nothing_is_set(monkeypatch: pytest.MonkeyPatch, tmp_path):
    for name in ("SCISCITOR_BASE_URL", "SCISCITOR_API_KEY", "SCISCITOR_MODEL"):
        monkeypatch.delenv(name, raising=False)

    config = load_config(env_file=tmp_path / "missing.env")

    assert config.base_url == "http://127.0.0.1:11434/v1"
    assert config.api_key == "ollama"
    assert config.model == "qwen3:14b"


def test_environment_wins_over_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("SCISCITOR_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("SCISCITOR_API_KEY", "secret")
    monkeypatch.setenv("SCISCITOR_MODEL", "gpt-4o-mini")

    config = load_config(env_file=tmp_path / "missing.env")

    assert config.base_url == "https://api.example.com/v1"
    assert config.api_key == "secret"
    assert config.model == "gpt-4o-mini"


def test_dotenv_file_is_loaded(monkeypatch: pytest.MonkeyPatch, tmp_path):
    for name in ("SCISCITOR_BASE_URL", "SCISCITOR_API_KEY", "SCISCITOR_MODEL"):
        monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("SCISCITOR_MODEL=from-file\n", encoding="utf-8")

    assert load_config(env_file=env_file).model == "from-file"


def test_blank_values_fall_back_to_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("SCISCITOR_MODEL", "   ")

    assert load_config(env_file=tmp_path / "missing.env").model == "qwen3:14b"
    assert os.environ["SCISCITOR_MODEL"] == "   "
