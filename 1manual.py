import streamlit as st
import json

def save_intent_data(intent_data):
    intents_file = 'intents.json'
    try:
        with open(intents_file, 'r') as f:
            intents = json.load(f)
    except FileNotFoundError:
        intents = {"intents": []}

    intents["intents"].append(intent_data)

    with open(intents_file, 'w') as f:
        json.dump(intents, f, indent=4)

    st.success('Data added successfully!')

def main():
    st.title('Intent Form')

    tag = st.text_input('Tag:')
    patterns = st.text_area('Patterns (separate with commas):')
    responses = st.text_area('Responses (separate with commas):')

    if st.button('Submit'):
        patterns_list = [p.strip() for p in patterns.split(',')]
        responses_list = [r.strip() for r in responses.split(',')]

        intent_data = {
            "tag": tag,
            "patterns": patterns_list,
            "responses": responses_list,
            "context": [""]
        }

        save_intent_data(intent_data)

if __name__ == '__main__':
    main()
