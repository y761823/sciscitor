import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic


ApplicationWindow {
    id: window
    width: 720
    height: 560
    minimumWidth: 360
    minimumHeight: 320
    visible: true
    title: "Sciscitor"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: "Model"
            }

            TextField {
                id: modelField
                Layout.fillWidth: true
                text: backend.defaultModel
                placeholderText: "Model name"
                enabled: !backend.busy
            }
        }

        TextArea {
            id: promptField
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            wrapMode: TextArea.Wrap
            placeholderText: "Enter one or more sentences"
            enabled: !backend.busy
        }

        Button {
            id: sendButton
            Layout.fillWidth: true
            text: backend.busy ? "Stop" : "Send"

            onClicked: {
                if (backend.busy) {
                    backend.stop()
                    return
                }

                answerField.text = ""
                answerField.cursorPosition = 0
                backend.request(promptField.text, modelField.text)
            }
        }

        TextArea {
            id: answerField
            objectName: "answer"
            Layout.fillWidth: true
            Layout.fillHeight: true
            readOnly: true
            wrapMode: TextArea.Wrap
            placeholderText: "Answer"
        }
    }

    Connections {
        target: backend

        function onChunk(piece) {
            answerField.text += piece
            answerField.cursorPosition = answerField.length
        }

        function onFailed(message) {
            answerField.text = message
        }
    }
}
