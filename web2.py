import os
from flask import Flask, request, jsonify, send_from_directory
import azure.cognitiveservices.speech as speechsdk
import requests
from moviepy.editor import ffmpeg_tools
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem

app = Flask(__name__, static_folder='static')

# Azure 語音和翻譯服務配置
SPEECH_KEY = '6ead9d9817a84c4a96440a548778459f'
SPEECH_REGION = 'eastus'
TRANSLATE_KEY = 'b3a256b701fc42b4a01273da192fd092'
TRANSLATE_ENDPOINT = 'https://api.cognitive.microsofttranslator.com/'
TRANSLATE_REGION = 'eastus'

# 音檔儲存路徑
UPLOAD_FOLDER = '.'  # 或自定義路徑如 '/app/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 語音轉文字函數
def speech_to_text(audio_path):
    print(audio_path)
    ffmpeg_tools.ffmpeg_extract_audio("audio.webm", "audio.wav")
    # clip = moviepy.AudioFileClip("audio.webm")
    # clip.write_audiofile("audio.wav")
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY, region=SPEECH_REGION)
    file_config = speechsdk.audio.AudioConfig(filename='audio.wav')
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=file_config)

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    return None

# 翻譯函數
def Translator(target):
    text_translator = TextTranslationClient(
        endpoint=TRANSLATE_ENDPOINT,
        credential=TranslatorCredential(TRANSLATE_KEY, TRANSLATE_REGION)
    )
    targets = []
    targets.append(InputTextItem(text=target))

    responses = text_translator.translate(
        content=targets, to=["zh-hant"], from_parameter="en")

    return responses

# 翻譯函數
def translate_text(text, to_lang='zh-Hant'):
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATE_KEY,
        'Ocp-Apim-Subscription-Region': TRANSLATE_REGION,
        'Content-type': 'application/json'
    }
    params = {'api-version': '3.0', 'to': to_lang}
    body = [{'text': text}]
    response = requests.post(
        TRANSLATE_ENDPOINT, params=params, headers=headers, json=body, timeout=10)
    print(response)
    response_json = response.json()
    return response_json[0]['translations'][0]['text']


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    audio_file.save(audio_path)

    text = speech_to_text(audio_path)
    if not text:
        return jsonify({'error': 'Speech recognition failed'}), 500

    # translated_text = translate_text(text)
    translated_text = Translator(text)

    # 刪除暫存音檔
    os.remove(audio_path)

    return jsonify({'text': text, 'translation': translated_text[0].translations[0].text})


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
