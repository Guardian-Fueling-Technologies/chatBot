import nltk
from nltk.stem import WordNetLemmatizer
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State

lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from tensorflow.keras.models import load_model
import json
import random

# Load the chatbot model, intents, words, and classes
model = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

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
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
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
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def textbox(text, box="AI", name="Chatbot"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "100%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        return dbc.Card(text, style=style, body=True, color="light", inverse=False)

    else:
        raise ValueError("Incorrect option for `box`.")
    
# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.InputGroupText(dbc.Button("Submit", id="submit")),
    ]
)
app.layout = dbc.Container(
    fluid=False,
    className="main-container",  # Add a custom class for main container styling
    children=[
        html.Div(
            dbc.Row([
                dbc.Col(
                    [
                        html.H1("Chatbot", className="mt-3 mb-4 chatbot-title"),
                        html.Hr(className="chatbot-hr"),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="https://raw.githubusercontent.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/main/Header.jpg",
                            className="chatbot-image",style={"width": "120%", "height": "auto", "padding": "10%"},
                        ),
                    ],
                    width=4,
                ),
            ]),
            className="header-row",
        ),
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Store(id="store-conversation", data=""),
                            conversation,
                            html.Div(controls),
                            dbc.Spinner(html.Div(id="loading-component")),
                        ],
                        width=12,
                    ),
                ],
                className="chatbot-row",
            )
        ),
    ],
)

@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]

@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""

@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)

def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    name = "Chatbot"
    chat_history += f"You: {user_input}<split>{name}:"
    chatbot_res = chatbot_response(user_input)
    chat_history += f"{chatbot_res}<split>"
    return chat_history, None

if __name__ == "__main__":
    app.run_server(debug=False)
