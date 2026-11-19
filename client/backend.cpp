#include "backend.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <QJsonDocument>
#include <QTimer>
#include <QtEndian>

#include <cstring>

namespace {

constexpr auto kPipeName = "sciscitor-server";
constexpr int kConnectRetries = 15;
constexpr int kConnectRetryDelayMs = 200;
constexpr quint32 kMaxFrameSize = 1u << 20;

} // namespace

Backend::Backend(QObject *parent) : QObject(parent) {
    QObject::connect(&m_socket, &QLocalSocket::connected, this, [this]() {
        m_retries = 0;
        writePending();
    });

    QObject::connect(&m_socket, &QLocalSocket::readyRead, this, &Backend::readFrames);

    QObject::connect(
        &m_socket, &QLocalSocket::errorOccurred, this, [this](QLocalSocket::LocalSocketError) {
            if (!m_busy)
                return;

            // The pipe instance may not exist yet right after the
            // server starts.
            if (m_socket.state() != QLocalSocket::ConnectedState && m_retries++ < kConnectRetries) {
                QTimer::singleShot(kConnectRetryDelayMs, this, &Backend::connectToServer);
                return;
            }

            finish(false, tr("Cannot reach sciscitor-server: %1").arg(m_socket.errorString()));
        });

    QObject::connect(&m_socket, &QLocalSocket::disconnected, this, [this]() {
        // The answer frame always arrives before the server closes the pipe.
        if (m_busy)
            finish(false, tr("The server closed the connection before answering."));
    });

    QObject::connect(qApp, &QCoreApplication::aboutToQuit, this, [this]() {
        if (m_server.state() != QProcess::NotRunning) {
            m_server.kill();
            m_server.waitForFinished(1000);
        }
    });
}

Backend::~Backend() {
    if (m_server.state() != QProcess::NotRunning) {
        m_server.kill();
        m_server.waitForFinished(1000);
    }
}

void Backend::request(const QString &prompt, const QString &model) {
    if (m_busy)
        return;

    if (prompt.trimmed().isEmpty()) {
        emit failed(tr("Enter a prompt first."));
        return;
    }

    m_pending = QJsonObject{
        {QStringLiteral("prompt"), prompt},
        {QStringLiteral("model"), model},
    };
    m_buffer.clear();
    m_retries = 0;
    setBusy(true);

    if (!ensureServer())
        return;

    if (m_socket.state() == QLocalSocket::ConnectedState)
        writePending();
    else
        connectToServer();
}

bool Backend::ensureServer() {
    if (m_server.state() != QProcess::NotRunning)
        return true;

    const QString clientDir = QCoreApplication::applicationDirPath();
    QString exe = QDir(clientDir).filePath(QStringLiteral("sciscitor-server.exe"));
    if (!QFileInfo::exists(exe))
        exe = QDir(clientDir).filePath(QStringLiteral("../bin/sciscitor-server.exe"));

    if (!QFileInfo::exists(exe)) {
        finish(false, tr("sciscitor-server.exe was not found next to the client or in ../bin."));
        return false;
    }

    m_server.start(QDir::cleanPath(exe),
                   {QStringLiteral("--pipe"), QString::fromLatin1(kPipeName)});
    if (!m_server.waitForStarted(3000)) {
        finish(false, tr("Failed to start sciscitor-server: %1").arg(m_server.errorString()));
        return false;
    }

    return true;
}

void Backend::connectToServer() {
    m_socket.abort();
    m_socket.connectToServer(QString::fromLatin1(kPipeName));
}

void Backend::writePending() {
    const QByteArray payload = QJsonDocument(m_pending).toJson(QJsonDocument::Compact);
    const quint32 size = qToLittleEndian(static_cast<quint32>(payload.size()));

    QByteArray frame(reinterpret_cast<const char *>(&size), sizeof(size));
    frame.append(payload);

    m_socket.write(frame);
    m_socket.flush();
}

void Backend::readFrames() {
    m_buffer.append(m_socket.readAll());

    while (m_buffer.size() >= static_cast<int>(sizeof(quint32))) {
        quint32 size = 0;
        std::memcpy(&size, m_buffer.constData(), sizeof(size));
        size = qFromLittleEndian(size);

        if (size == 0 || size > kMaxFrameSize) {
            finish(false, tr("Received a malformed frame from the server."));
            return;
        }
        if (m_buffer.size() < static_cast<int>(sizeof(size) + size))
            return;

        const QByteArray payload = m_buffer.mid(sizeof(size), static_cast<int>(size));
        m_buffer.remove(0, static_cast<int>(sizeof(size) + size));

        const QJsonObject frame = QJsonDocument::fromJson(payload).object();
        const QString error = frame.value(QStringLiteral("error")).toString();
        if (!error.isEmpty()) {
            finish(false, error);
            return;
        }

        m_socket.disconnectFromServer();
        finish(true, frame.value(QStringLiteral("text")).toString());
        return;
    }
}

void Backend::finish(bool ok, const QString &message) {
    m_pending = {};
    m_buffer.clear();
    setBusy(false);

    if (ok)
        emit answered(message);
    else
        emit failed(message);
}

void Backend::setBusy(bool busy) {
    if (m_busy == busy)
        return;

    m_busy = busy;
    emit busyChanged();
}
