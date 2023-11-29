import openai
import json
import time

with open("questions.json", "r") as f:
    data = json.load(f)

openai.api_key = "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"

def ask_question(question):
    prompt = f"Q: {question}\nA:"
    print(prompt)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    answer = response.choices[0].text.strip()
    return answer

def get_feedback():
    while True:
        feedback = input("How was the response? (good/mediocre/bad): ")
        if feedback in ["good", "mediocre", "bad"]:
            break
        else:
            print("Invalid feedback. Please enter 'good', 'mediocre', or 'bad'.")
    return feedback

training_data = []

while True:
    question = input("What's your question? (Type 'exit' to quit): \n")
    if question.lower() == "exit":
        break
    response = ask_question(question)
    print(f"Answer: {response}")
    feedback = get_feedback()
    training_data.append({"question": question, "answer": response, "feedback": feedback})
    time.sleep(1)


with open("training_data.json", "w") as f:
    json.dump(training_data, f)
