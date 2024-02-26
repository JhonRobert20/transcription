import whisper

def transcribe_audio_to_text(audio_path):
    # Carga el modelo de Whisper
    model = whisper.load_model("large")

    # Transcribe el audio
    result = model.transcribe(audio_path)

    # Retorna el texto transcrito
    return result['text']

# Ejemplo de cómo usar la función
audio_path = 'test.mp3'  # Asegúrate de reemplazar esto con la ruta a tu archivo de audio
text = transcribe_audio_to_text(audio_path)
print(text)
