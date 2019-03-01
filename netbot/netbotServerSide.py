from flask import Flask, send_from_directory, request, jsonify
from Scripts.seqAnalysis import process_sequence
import json

app = Flask(__name__, static_folder='./static', template_folder='./static')

@app.route('/')
def index():
    with open("Log.txt", "a") as f: #debug
        f.write("- Index home page called.\n") #debug
    return send_from_directory('./','index.html')

@app.route('/debug', methods=['GET','POST'])
def debug():
    return "echo debug works just fine."

@app.route('/sequence_submition', methods=['GET','POST'])
def sequence_submition():
    with open("Log.txt", "a") as f: #debug
        if request.method == 'POST':
            try:
                user_data = json.loads(request.data.decode())
                f.write("- recieved user_data: "+str(user_data)+"\n")#debug
                my_answer = {"ANSWER": process_sequence(user_data["User"])} #e.g. my_answer = {'ANSWER': '789'}
                f.write("- Processed: \n")#debug
                json_parsed = json.dumps(my_answer) #turn it into a json string
                f.write("- response parsed: "+str(my_answer)+" \n")#debug
                return jsonify(json_parsed)
            except Exception as e:
                f.write("- Server Error "+e+".\n") #debug
                return jsonify(json.dumps("Server Error"))




if __name__ == '__main__':
    app.run()