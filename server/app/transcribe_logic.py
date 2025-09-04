import whisper


def load_model(model_size: str = "base"):
    """
    Load the Whisper model.
    Default: base
    """
    print(f"Loading Whisper model: {model_size} ...")
    model = whisper.load_model(model_size)
    return model


def transcribe_audio(model, audio_path: str, language: str = None):
    """
    Transcribe audio with Whisper.
    
    Args:
        model: Whisper model object
        audio_path (str): Path to the audio file
        language (str, optional): Language hint (e.g., "en")
    
    Returns:
        dict: Full Whisper transcription result
    """
    print(f"Transcribing {audio_path} ...")
    result = model.transcribe(audio_path, language=language)
    return result


if __name__ == "__main__":
    # Example usage
    model = load_model("base")
    result = transcribe_audio(model, "example.wav", language="en")

    # Print just the text
    print("\n--- Transcription ---")
    print(result["text"])
