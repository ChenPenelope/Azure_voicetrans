from flask import Flask, request, jsonify
import azure.cognitiveservices.speech as speechsdk
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from msrest.authentication import CognitiveServicesCredentials
import requests

app = Flask(__name__)

# 配置 Azure 語音服務和翻譯服務
SPEECH_KEY = '6ead9d9817a84c4a96440a548778459f'
SPEECH_REGION = 'eastus'
TRANSLATE_KEY = 'b3a256b701fc42b4a01273da192fd092'
TRANSLATE_ENDPOINT = 'https://api.cognitive.microsofttranslator.com/'
TRANSLATE_REGION = 'eastus'

# 音檔儲存路徑
UPLOAD_FOLDER = '/tmp'  # 或自定義路徑如 '/app/uploads'

# 設置 Flask 的上傳路徑
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 語音轉文字函數
def speech_to_text(audio_data):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_data)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        return None

# 翻譯函數
def translate_text(text, to_lang='zh-Hant'):
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATE_KEY,
        'Ocp-Apim-Subscription-Region': TRANSLATE_REGION,
        'Content-type': 'application/json'
    }
    params = {'api-version': '3.0', 'to': to_lang}
    body = [{'text': text}]
    response = requests.post(TRANSLATE_ENDPOINT, params=params, headers=headers, json=body)
    response_json = response.json()
    return response_json[0]['translations'][0]['text']

@app.route('/transcribe' ,methods=['GET', 'POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400
    
    audio_file = request.files['audio']
    audio_path = '/tmp/' + audio_file.filename
    audio_file.save(audio_path)

    text = speech_to_text(audio_path)
    if not text:
        return jsonify({'error': 'Speech recognition failed'}), 500

    translated_text = translate_text(text)
    return jsonify({'text': text, 'translation': translated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
