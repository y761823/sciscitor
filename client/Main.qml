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
    title: qsTr("Sciscitor")

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: qsTr("Model")
            }

            TextField {
                id: modelField
                Layout.fillWidth: true
                text: "qwen3:14b"
                placeholderText: qsTr("Model name")
            }
        }

        TextArea {
            id: promptField
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            wrapMode: TextArea.Wrap
            placeholderText: qsTr("Enter one or more sentences")
        }

        Button {
            id: sendButton
            Layout.fillWidth: true
            text: backend.busy ? qsTr("Thinking…") : qsTr("Send")
            enabled: !backend.busy

            onClicked: {
                answerField.text = ""
                backend.request(promptField.text, modelField.text)
            }
        }

        TextArea {
            id: answerField
            Layout.fillWidth: true
            Layout.fillHeight: true
            readOnly: true
            wrapMode: TextArea.Wrap
            placeholderText: qsTr("Answer")
        }
    }

    Connections {
        target: backend

        function onAnswered(text) {
            answerField.text = text
        }

        function onFailed(message) {
            answerField.text = message
        }
    }
}
