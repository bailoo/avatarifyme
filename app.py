import requests
import streamlit as st

from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

def main_loop():
    st.title("Secret Chat with Avatars")
    st.subheader("Imagine & Say Anything!")
    #st.text("Some Avatars are Real ;)")

    image_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if not image_file:
        return None

    original_image = Image.open(image_file)
    st.image(original_image)

    stt_button = Button(label="Say", width=100)

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
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    tts_button = Button(label="Listen", width=100)

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

    if result:
        if "GET_TEXT" in result:
            text = result.get("GET_TEXT")
            st.write(text)
        
            prompt_data = {
                "prompt": "\n\n### Instructions:\n"+text+"\n\n### Response:\n",
                "stop": ["\n","###"]
            }
            url_post = "http://localhost:8000/v1/completions"
            response = requests.post(url_post, json=prompt_data)
            json = response.json()
            ans = json['choices'][0]['text']
            st.write(ans)

            tts_button.js_on_event("button_click", CustomJS(code=f"""
                var u = new SpeechSynthesisUtterance();
                u.text = "{ans}";
                u.lang = 'en-US';

                speechSynthesis.speak(u);
                """))

    st.bokeh_chart(tts_button)

if __name__ == '__main__':
    main_loop()
