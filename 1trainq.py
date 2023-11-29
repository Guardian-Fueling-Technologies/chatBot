import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json

def generate_questions(passage):
    # Load pre-trained T5 model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("potsawee/t5-large-generation-squad-QuestionAnswer")
    model = AutoModelForSeq2SeqLM.from_pretrained("potsawee/t5-large-generation-squad-QuestionAnswer")

    # Tokenize the passage and generate questions
    inputs = tokenizer.encode("generate questions: " + passage, return_tensors="pt", max_length=1024, truncation=True)
    outputs = model.generate(inputs, max_length=256, num_beams=4, early_stopping=True)

    # Decode the generated questions
    generated_questions = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_questions.split("<pad>")

if __name__ == "__main__":
    # Example usage
    passage = "Guardian Fueling Technologies is pleased to announce the formation of a new division, Guardian EVI which will support Electric Vehicle Infrastructure and the significant growth in EV charger demand in the United States.  Deployment of electric vehicle chargers is growing in popularity with Guardian’s traditional retail and commercial customers that want to offer electric fueling to their customers and fleets in addition to the new EV charging markets including hospitality, multi-family, workplace and parking. Guardian EVI has received a significant investment from the company, and it has added several industry veterans to its team in areas such as service, installation, project management and business development.  Best-in-class product lines and a full-service approach from planning and grant development to fully developed locations including installation and on-going service are cornerstones of the Guardian EVI business unit.  “Deployment of EV’s has reached a place where significant investments are flowing to EV infrastructure and Guardian EVI stands ready to support the electrification of America” said Guardian Fueling Technologies CEO, Joey Batchelor.  “The expertise we have added to the Guardian EVI division will allow us to offer real-world experience with specification development and cost-effective solutions from a variety of vendors to meet every market need”. Guardian EVI will leverage other Guardian divisions such as Guardian Connect, the company’s remote service delivery platform that provides real-time notifications of service issues and then acts upon them within minutes versus days or weeks in traditional service models.  EV charging technology continues to evolve, and Guardian EVI will maximize its expertise in the fueling experience to deliver products and services to fit any application. For more information, please visit our website at www.guardianfueltech.com and click the Guardian EVI tab under solutions."

    generated_questions = generate_questions(passage)
    
    generated_question = generated_questions[0]
    question_prefix = generated_question.split("?")[0].strip()
    response = generated_question.split("?")[1].strip()

    new_intent = {
    "tag": "CEO",
    "patterns": [question_prefix],
    "responses": [response],
    "context": [""]
    }
    print(new_intent)
    json_new_intent = json.dumps(new_intent, indent=4)

    print(json_new_intent)