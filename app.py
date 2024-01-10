from flask import Flask, render_template, Response, request, jsonify
from sql import init_db, start_session,  Message
from func import get_response_stream, search, scrape
from dotenv import load_dotenv
from uuid import uuid4
import os
import concurrent.futures

load_dotenv(os.getcwd() + '/.env')

engine = init_db()

app = Flask(__name__, template_folder='templates')
app.secret_key = str(uuid4())

@app.route('/')
def playground():
     return render_template('index.html',env=os.getenv("USERNAME"))

@app.route('/request', methods=['POST'])
def req():

    chat_id = request.json.get('chat_id')
    model = request.json.get('model')
    mode = request.json.get('mode')
    prompt = request.json.get('user_prompt')
    sites = int(request.json.get('sites'))

    key = os.getenv("OPENAI_API_KEY")

    if mode == "chat":

        messages=[]

        with start_session(engine) as session:
            chat_history = session.query(Message).filter(Message.chat_id == chat_id).all()

        messages.append({"role": "system", "content": "Du bist eine hilfreicher KI Assistent"})

        if chat_history:

            for record in chat_history:

                messages.append({"role": "user", "content": record.prompt})
                messages.append({"role": "assistant", "content": record.response})

        messages.append({"role": "user", "content": prompt})

        temperature=0.4
        max_token=4000
        top_p=0.9
        frequency=0.4
        presence=0.4

        response = Response(get_response_stream(key,chat_id,messages,temperature,max_token,top_p,frequency,presence,model=model), mimetype='text/event-stream')


    if mode == "research":

        sites = search(key,prompt, sites)

        research = ""
        sources = []
        index = 0

        # Scraping
        if isinstance(sites, list):

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(lambda site: scrape(key, site), sites))

                for result in results:
                    research += "[" + str(index+1) + "] " + sites[index] + "\n" + result + "\n\n"
                    sources.append("[" + str(index+1) + "] " + sites[index])
                    index = index + 1

        system_prompt= "Erstelle eine Antwort aus den vorgegebenen Zusammenfassungen der Websuche. Verwende nur die Zusammenfassungen. Sei unvoreingenommen und journalistisch. Füge die Informationen kohärent zusammen, ohne den Text zu wiederholen. Es ist zwingend erforderlich, dass du alle verwendeten Informationen mit ihrer entsprechenden Quellennummer zitierst ([Nummer]). Sprich gleichnamige Entitäten gesondert an. Du MUSST eine präzise, klare Antwort formulieren."
        user_prompt = f"###Zusammenfassungen der Websuche:###\n {research}"

        messages=[{"role": "system", "content": system_prompt }]
        messages.append({"role": "user", "content": user_prompt})

        temperature=0.25
        max_token=4000
        top_p=1.0
        frequency=0
        presence=0

        response = Response(get_response_stream(key,chat_id,messages,temperature,max_token,top_p,frequency,presence,model=model,save=False,urls=sites), mimetype='text/event-stream')

    response.headers['X-Accel-Buffering'] = 'no'

    return response

@app.route('/truncate', methods=['POST'])
def truncate():

    id = request.json.get('id')

    with start_session(engine) as session:
        session.query(Message).filter(Message.chat_id == id).delete()
        session.commit()

    return jsonify({'response': 'success'}), 200

if __name__ == '__main__':
    app.run(port=8001, debug=True)



