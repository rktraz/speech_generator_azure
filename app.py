import requests
import json
import os
import base64
import docx
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from functions import *


app = Flask(__name__)
app.secret_key = 'secret'

# Load environment variables from .env file
load_dotenv()

base_folder = "ssml_files"
voice_configurations = generate_voice_configurations(base_folder)
# print(voice_configurations)

# Configure Azure Speech Service
subscription_key = os.getenv('SUBSCRIPTION_KEY')
service_region = os.getenv('SERVICE_REGION')
translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')
text_analytics_endpoint = os.getenv('TEXT_ANALYTICS_ENDPOINT')

speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
ta_credential = AzureKeyCredential(subscription_key)

text_analytics_client = TextAnalyticsClient(
            endpoint=text_analytics_endpoint, 
            credential=ta_credential)

languages_list = [
    {"code": "en", "value": "English", "default": True, "label": "English"},
    {"code": "fr", "value": "French", "default": False, "label": "French"},
    # {"code": "es", "value": "Spanish", "default": False, "label": "Spanish"},
    # {"code": "hi", "value": "Hindi", "default": False, "label": "Hindi"}
]

languages_to_code = {
    "English": "en",
    # "Spanish": "es",
    "French": "fr",
    # "Hindi": "hi"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Save the form values in the session
        session['original_text'] = request.form.get('original_text')
        session['translated_text'] = request.form.get('translated_text')
        session['target_lang'] = request.form.get('target-lang-select')
        session['selected_voice'] = request.form.get('selected_voice')
        
        # print(session)

        # Generate the speech
        if 'selected_voice' in session:
            selected_voice = session['selected_voice']

            target_lang_code = languages_to_code[session['target_lang']]
            session['voices_list'] = list(voice_configurations[target_lang_code].keys())

            ssml_string = voice_configurations[target_lang_code][selected_voice].read_text()
            ssml_string_modified = modify_ssml(ssml_string, session['translated_text'])
            result = speech_synthesizer.speak_ssml_async(ssml_string_modified).get()
            audio_data = base64.b64encode(result.audio_data).decode('utf-8')


        return render_template('index.html', original_text=session['original_text'], translated_text=session['translated_text'],
                               languages_list=languages_list, voices_list=session['voices_list'],
                               target_lang=session['target_lang'], audio_data=audio_data)
        
    else:
        # Retrieve the form values from the session
        original_text = session.get('original_text', "")
        translated_text = session.get('translated_text', "")
        selected_voice = session.get('selected_voice', "")
        target_lang = session.get('target_lang', "")

        return render_template('index.html', languages_list=languages_list, original_text=original_text,
                               translated_text=translated_text, selected_voice=selected_voice,
                               target_lang=target_lang)


@app.route('/extract_text', methods=['POST'])
def extract_text():
    file = request.files['file']
    doc = docx.Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

@app.route('/translate', methods=['POST'])
def translate_text():
    text_to_translate = request.json['original_text']
    target_lang = request.json['target_lang']
    target_lang_code = languages_to_code[target_lang]

    original_lang_response = text_analytics_client.detect_language(documents=[text_to_translate])[0]
    original_lang_code = original_lang_response.primary_language.iso6391_name

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': service_region
    }

    params = {
        'api-version': '3.0',
        'from': original_lang_code,
        'to': target_lang_code
    }

    body = [{
        'text': text_to_translate
    }]

    response = requests.post(f'{translator_endpoint}/translate', headers=headers, params=params, json=body)
    translated_text = response.json()[0]['translations'][0]['text']

    voices_list = list(voice_configurations[target_lang_code].keys())

    return json.dumps({'translated_text': translated_text, 'voices_list': voices_list})



if __name__ == '__main__':
    app.run()
