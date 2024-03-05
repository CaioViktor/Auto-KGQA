from sparql.Endpoint import Endpoint
from nlp.normalizer import *
from index.whoosh_index import *
from configs import *
from persistence.Questions_Dataset import Questions_Dataset
from flask import Flask,render_template,request, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin
import os.path
from dotenv import load_dotenv
import openai

from core.ChatHandler import ChatHandler

#OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#Normalizer
normalizer = Normalizer()

#T-Box
endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
t_box_index = TBoxIndex(endpoint_t_box,normalizer)

#A-Box
endpoint_a_box = endpoint_t_box
if ENDPOINT_A_BOX_URL and ENDPOINT_T_BOX_URL != ENDPOINT_A_BOX_URL:
    endpoint_a_box = Endpoint(ENDPOINT_A_BOX_URL)
a_box_index = ABoxIndex(endpoint_a_box,normalizer)

#ChatHadler
chatHandler = ChatHandler(endpoint_a_box,t_box_index,normalizer,a_box_index)

#Question Dataset
dataset = Questions_Dataset(DATASET_FILE)
if os.path.isfile(DATASET_FILE):
    dataset = Questions_Dataset.load(DATASET_FILE)

#Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/query/*": {"origins": "*"},r"/feedback*": {"origins": "*"}})


@app.route("/")
def index():
	return """Server Running...<br/>
	/query/&lt;ID&gt;?query=&lt;NL_QUESTION&gt;
	"""

@app.route("/query/<id>/")
def query(id,methods=['GET']):
    query = request.args.get('query',default="")
    # print("question: "+query)
    qa = chatHandler.getChat(id)
    result = qa.processQuestion(query)
    # print(result)
    result = dataset.add(result)
    dataset.save()
    return jsonify(result)

@app.route("/feedback")
def feedback(methods=['GET']):
    question_id = request.args.get('question_id',default="")
    value = request.args.get('value',default="1")
    if question_id != "":
        dataset.feedback(question_id,value)
        dataset.save()
    return jsonify({'result':"ok"})

if __name__ == "__main__":
	app.run(host='0.0.0.0',port=5000)