#pragma once

#include <QJsonObject>
#include <QLocalSocket>
#include <QObject>
#include <QProcess>

// Owns the server process and speaks the pipe protocol: one JSON frame per
// direction, each preceded by a 4-byte little-endian length.
class Backend : public QObject {
    Q_OBJECT
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)

public:
    explicit Backend(QObject *parent = nullptr);
    ~Backend() override;

    bool busy() const { return m_busy; }

    Q_INVOKABLE void request(const QString &prompt, const QString &model);

signals:
    void answered(const QString &text);
    void failed(const QString &message);
    void busyChanged();

private:
    bool ensureServer();
    void connectToServer();
    void writePending();
    void readFrames();
    void finish(bool ok, const QString &message);
    void setBusy(bool busy);

    QProcess m_server;
    QLocalSocket m_socket;
    QByteArray m_buffer;
    QJsonObject m_pending;
    bool m_busy = false;
    int m_retries = 0;
};
