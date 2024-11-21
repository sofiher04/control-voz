import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import json
import paho.mqtt.client as paho

def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("sofikings")
client1.on_message = on_message

st.title("Cuida tu planta con Umi")
st.subheader("Habla para regar o ponerle semillas a tu planta")

# Imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

# Botón con reconocimiento de voz
st.write("Toca el Botón y habla")

stt_button = Button(label="Inicio", width=200)

# Código JavaScript como cadena literal
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };
    recognition.start();
"""))

# Procesar eventos
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# Publicar el texto reconocido en MQTT
if result and "GET_TEXT" in result:
    text_input = result.get("GET_TEXT").strip()
    st.write(f"Texto reconocido: {text_input}")

    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": text_input})
    client1.publish("control", message)

    # Crear directorio temporal
    os.makedirs("temp", exist_ok=True)

