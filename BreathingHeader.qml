import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    visible: true
    width: 800
    height: 200
    title: "Breathing Header Title - Shader Effect"
    color: "#333333"

    // Container for the header
    Item {
        id: header
        anchors.fill: parent

        // Shader-based breathing glow effect behind the title
        ShaderEffect {
            id: breathingGlow
            anchors.fill: parent
            property real phase: 0.0
            property color glowColor: "#AA00FF"
            fragmentShader: "
                uniform float phase;
                uniform vec4 glowColor;
                varying vec2 qt_TexCoord0;
                void main() {
                    vec2 center = vec2(0.5, 0.5);
                    float dist = distance(qt_TexCoord0, center);
                    float baseAlpha = 1.0 - smoothstep(0.0, 0.6, dist);
                    float pulse = 0.5 + 0.5 * sin(phase);
                    float alpha = baseAlpha * pulse;
                    gl_FragColor = vec4(glowColor.rgb, alpha);
                }"
            NumberAnimation on phase {
                from: 0
                to: 6.28318  // 2*PI for a full cycle
                duration: 2000
                loops: Animation.Infinite
                easing.type: Easing.InOutQuad
            }
        }

        // Title text rendered on top of the shader effect
        Text {
            id: titleText
            anchors.centerIn: parent
            text: "ABU MUKH CAR PARTS"
            font.pixelSize: 40
            font.bold: true
            color: "white"
        }
    }
}
