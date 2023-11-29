import streamlit as st
import random
import pickle
import numpy as np
import json
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import time
lemmatizer = WordNetLemmatizer()

# Load the chatbot model, intents, words, and classes
model = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


if "showForm" not in st.session_state:
    st.session_state.showForm = "Main"
if "login" not in st.session_state:
        st.session_state.login = False

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    try:
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)
        return res
    except (Exception) as e:
        return "This has not been in record please add record"

def main():
    if(st.session_state.showForm == "Main"):
        header_col, image_col = st.columns([1, 1])
        header_col.title("Chatbot")
        image_col.image("https://raw.githubusercontent.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/main/Header.jpg",
                        use_column_width=True)
        st.markdown("---")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Accept user input
        if prompt := st.chat_input("What is up?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in str(chatbot_response(prompt)).split():
                    full_response += chunk + " "
                    
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        if len(st.session_state.messages) > 1:
            if(str(chatbot_response(prompt)) == "This has not been in record please add record"):
                if st.button("Add record"):
                    st.session_state.showForm = "edit"
                    st.experimental_rerun()
            elif(st.button("Don't Like")):
                st.session_state.showForm = "edit"
                st.experimental_rerun()
    else:
        edit()

def edit():
    if not st.session_state.login:
        st.title("Edit Credentials")
        st.session_state.username = st.text_input("Username")
        st.session_state.password = st.text_input("Password", type="password")
        st.session_state.database = st.text_input("Database")
        if st.button("Submit"):
            # api = mygeotab.API(username=st.session_state.username, password=st.session_state.password, database=st.session_state.database)
            # try:
            #     api.authenticate()
            # except mygeotab.AuthenticationException as ex:
            #     st.error("Credentials incorrect")
            if st.session_state.username or st.session_state.password or st.session_state.database:
                # after login container is cleaned
                st.success("Credentials correct!")
                st.session_state.login = True
                st.experimental_rerun()
    else:
        st.title('Intent Form')    
        intents_file = 'intents.json'     
        with open(intents_file, 'r') as f:
            intent_data = json.load(f)
        intent_data = intent_data["intents"]
        all_tags = list(intent['tag'] for intent in intent_data)
        all_tags = ["Add New"] + all_tags

        st.session_state.selected_tag_idx = 0
        selected_tags = st.selectbox("Tags", all_tags, index=st.session_state.selected_tag_idx)
        st.session_state.selected_tag_idx = all_tags.index(selected_tags)

        if selected_tags == "Add New":
            tag = st.text_input('Tag:')
            st.error('Do not enter statements with commas for Patterns and Responses')
            patterns = st.text_area('Patterns (separate with commas):')
            responses = st.text_area('Responses (separate with commas):')

            if st.button('Submit'):
                if tag:
                    patterns_list = [p.strip() for p in patterns.split(',')]
                    responses_list = [r.strip() for r in responses.split(',')]

                    intent_data = {
                        "tag": tag,
                        "patterns": patterns_list,
                        "responses": responses_list,
                        "context": [""]
                    }
                    intents["intents"].append(intent_data)
                    with open(intents_file, 'w') as f:
                        json.dump(intents, f, indent=4)
                    st.success('Data added successfully!')
                    time.sleep(2)  
                    st.experimental_rerun()
                else:
                    st.error("please input a Tag name as adding new tags")
        else:
            tag = st.text_input('Tag:', selected_tags, disabled=True)
            for intent in intent_data:
                if intent['tag'] == tag:
                    allPattern = ""
                    allResponse = ""
                    for pattern in intent['patterns']:
                        allPattern = pattern + ", " + allPattern
                    patterns = st.text_area('Patterns (separate with commas):', allPattern)
                    for response in intent['responses']:
                        allResponse = response + ", " + allResponse
                    responses = st.text_area('Responses (separate with commas):', allResponse)
            if st.button('Submit'):
                if tag:
                    patterns_list = [p.strip() for p in patterns.split(',')]
                    responses_list = [r.strip() for r in responses.split(',')]

                    intent_data = {
                        "tag": tag,
                        "patterns": patterns_list,
                        "responses": responses_list,
                        "context": [""]
                    }

                    intents["intents"][st.session_state.selected_tag_idx-1] = intent_data

                    with open(intents_file, 'w') as f:
                        json.dump(intents, f, indent=4)
                    st.success('Data added successfully!')
                    time.sleep(2)  
                    st.experimental_rerun()
        if st.button('Close'):
            st.session_state.showForm = "Main"
            st.experimental_rerun()

if __name__ == "__main__":
    main()