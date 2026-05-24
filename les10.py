
'''
input word
give back word 
integrate tts

'''
import sys
import requests
import pyttsx3

URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_definition(word):
    response = requests.get(URL + word)

    if response.status_code != 200:
        print("Word not found.")
        return

    data = response.json()
    results = []
    parts = []
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("rate", 140)
    engine.setProperty("voice", voices[1].id)

    for entry in data:
        print(f"\nWord: {entry.get('word', '')}")
        
        meanings = entry.get("meanings", [])
        for meaning in meanings:
            part = meaning.get("partOfSpeech", "")
            print(f"({part})")
            parts.append(part)
            
            for d in meaning.get("definitions", []):
                definition = d.get("definition", "")
                print(" -", d.get("definition", ""))
                results.append(definition) 

    
    engine.say(f"{word};" +"".join(parts)+" ".join(results))

    engine.runAndWait()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python define.py <word>")
    else:
        get_definition(sys.argv[1])


