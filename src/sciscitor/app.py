"""Qt application window and the bridge between QML and the chat model."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import qasync
from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from . import llm
from .config import Config, load_config

QML_FILE = Path(__file__).with_name("Main.qml")


class Backend(QObject):
    """Exposed to QML as `backend`."""

    busyChanged = Signal()
    chunk = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, config: Config, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._task: asyncio.Task[str] | None = None
        self._answer = ""
        self._busy = False

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, constant=True)
    def defaultModel(self) -> str:
        return self._config.model

    @Slot(str, str)
    def request(self, prompt: str, model: str) -> None:
        if self._busy:
            return
        if not prompt.strip():
            self.failed.emit("Enter a prompt first.")
            return

        self._answer = ""
        self._set_busy(True)
        self._task = asyncio.ensure_future(self._run(prompt, model.strip() or None))

    @Slot()
    def stop(self) -> None:
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def _run(self, prompt: str, model: str | None) -> None:
        try:
            await llm.stream_answer(self._config, prompt, model, self._collect)
        except asyncio.CancelledError:
            # Whatever arrived before the stop stays on screen.
            self.finished.emit()
            raise
        except Exception as exc:  # shown verbatim in the window
            self.failed.emit(str(exc) or type(exc).__name__)
        else:
            self.finished.emit()
        finally:
            self._set_busy(False)

    def _collect(self, piece: str) -> None:
        self._answer += piece
        self.chunk.emit(piece)

    def _set_busy(self, busy: bool) -> None:
        if self._busy == busy:
            return
        self._busy = busy
        self.busyChanged.emit()


def main() -> int:
    config = load_config()
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Sciscitor")

    backend = Backend(config)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(str(QML_FILE)))
    if not engine.rootObjects():
        print(f"sciscitor: could not load {QML_FILE}", file=sys.stderr)
        return 1

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    app.aboutToQuit.connect(loop.stop)
    with loop:
        loop.run_forever()

    # Tear the QML tree down while the context property is still alive: during
    # interpreter shutdown the property turns null and Qt re-evaluates the
    # bindings that use it, which prints harmless but confusing TypeErrors.
    del engine
    return 0
