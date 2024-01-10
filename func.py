from sql import init_db, start_session, Message
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import json
import logging
import tiktoken
import openai
import time
import os
import re
import requests

MAX_TOKENS = 4000

load_dotenv(os.getcwd() + '/.env')

engine = init_db()

def get_tokens(text):
    try:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        token_count = len(enc.encode(text))
        logging.debug(f"Token count for text: {token_count}")
        return token_count
    except Exception as e:
        logging.error(f"An error occurred while calculating tokens: {e}")
        return 0

def get_response_stream(key,id,messages,temperature,max_tokens,top_p,frequency_penalty,presence_penalty,model='gpt_35_turbo',save=True,urls=[],chat_id=None):

    try:

        openai.api_key=key

        start_time = time.time()

        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=True
        )

        answer=""

        for trunk in response:

            if len(trunk.choices) > 0:

                if trunk.choices[0].finish_reason is not None:

                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    if len(urls) > 0:
                        url_list = "<br><br>" + "<br>".join(array_to_html_links(urls))
                    else:
                        url_list = ""

                    data = json.dumps({"response": "<END>", "urls":url_list, "prompt_tokens":get_tokens(" ".join([item["content"] for item in messages])), "completion_tokens":get_tokens(answer), "completion_time":elapsed_time})

                    yield data + "\n"

                else:

                    chunk=trunk.choices[0].delta.content.replace("\n","<br>")

                    data = json.dumps({"response":chunk})
                    answer += chunk

                    yield data + "\n"
                    time.sleep(0.02)


        if save:

            system = messages[0]["content"]
            prompt = messages[-1]["content"]

            save_data(id,system,answer,prompt,temperature,max_tokens,top_p,frequency_penalty,presence_penalty,model)

    except Exception as e:
        return str(e)


def save_data(id,system,response,prompt,temperature,max_token,top_p,frequency_penalty,presence_penalty,model):

    try:

        with start_session(engine) as session:

            message = Message(chat_id=id,model=model,system=system,prompt=prompt,response=response,temperature=temperature,max_token=max_token,top_p=top_p,frequency=frequency_penalty,presence=presence_penalty)
            session.add(message)

            session.commit()

    except Exception as e:
        logging.info(str(e))


def fix_encoding(s):
    try:
        byte_str = s.encode('ISO-8859-1')
        return byte_str.decode('utf-8')
    except UnicodeEncodeError as e:
        print(str(e))
        return s
    except UnicodeDecodeError as e:
        print(str(e))
        return s

def escape_unicode(s):
    try:
        return s.encode('ISO-8859-1').decode('unicode-escape')
    except UnicodeEncodeError:
        return s

def search(key, query, n):
  try:

    openai.api_key=key

    system_prompt = "Du bist ein Experte für Google-Suchanfragen. Deine Aufgabe besteht darin, bestehende Suchanfragen zu analysieren und so umzuformulieren, dass sie mit hoher Wahrscheinlichkeit zu besseren und relevanteren Suchergebnissen führen. Berücksichtige dabei Schlüsselwörter, spezifische Suchparameter und fortgeschrittene Suchtechniken. Nutze dein Wissen über Suchalgorithmen und das Internet und seine Inhalte, um die bestmöglichen Ergebnisse zu erzielen. Gib als Antwort nur die neue Suchanfrage aus!"
    user_prompt = f"Verbessere die folgende Suchanfrage:\n###\n{query}\n###"

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    revised_query = openai.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      messages=messages,
      temperature=0.25,
      max_tokens=50,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    print(revised_query.choices[0].message.content.replace('"',''))

    response = requests.get(
      'https://www.googleapis.com/customsearch/v1',
      params={
        'key': os.getenv("GOOGLE_API_KEY"),
        'cx': os.getenv("GOOGLE_API_CX"),
        'q': revised_query.choices[0].message.content.replace('"',''),
        'lr':'lang_de'
      },
    )

    response.raise_for_status()
    search_results = response.json().get('items', [])[:n]
    links = [result['link'] for result in search_results]

    print(links)

    return links

  except Exception:
    return []

# Diese Funktion ruft den Inhalt einer URL ab und gibt den rohen Text zurück
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_raw_content(url):

    try:
        response = requests_retry_session().get(url)
        response.raise_for_status()

        return response.text
    except requests.exceptions.HTTPError as errh:
        print(f'HTTP Error: {errh}')
        return ""
    except requests.exceptions.ConnectionError as errc:
        print(f'Error Connecting: {errc}')
        return ""
    except requests.exceptions.Timeout as errt:
        print(f'Timeout Error: {errt}')
        return ""
    except requests.exceptions.RequestException as err:
        print(f'Error: {err}')
        return ""

def truncate_text(text, max_tokens):
  try:
    tokens = text.split()
    while get_tokens(' '.join(tokens)) > max_tokens:
        tokens.pop()
    return ' '.join(tokens)
  except Exception:
    return ""

# Diese Funktion extrahiert und verarbeitet (bzw. bereinigt) den Inhalt einer Webseite
def scrape(key,url):
    try:

        openai.api_key=key

        response = get_raw_content(url)

        if not response:
            return "Kein Inhalt gefunden."

        soup = BeautifulSoup(response, 'html.parser')
        text = clean_text(soup)

        if len(text) == 0:
            return "Web-Scraping fehlgeschlagen."

        token_count = get_tokens(text)

        if token_count > 4000:
            text = truncate_text(text, 4000)

        system_prompt = f'Deine Aufgabe ist es, prägnante Zusammenfassungen für bereitgestellte Website-Inhalte zu erstellen.\n\nBefolge diese Schritte:\n\n1. Lies den Inhalt der Website.\n2. Fasse ihn zusammen, indem du dich auf die wichtigsten Informationen konzentrierst.\n\nDenke daran:\n- Verwende natürliche Sprache.\n- Stelle sicher, dass die Zusammenfassung objektiv ist.'
        user_prompt = f"### Anweisung ###\nWebsite-Inhalte = '{text}'\n\n### Deine Aufgabe ### Fasse den obigen Inhalt zusammen"

        #system_prompt = 'Du bist ein Kerninformations-Extraktor, ein Modell, das speziell von OpenAI entwickelt wurde, um die wichtigsten Informationen aus gescraptem Website-Content zu extrahieren.'
        #user_prompt = f"Bitte extrahiere die wichtigsten Informationen aus folgendem Text: {text}"

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            temperature=0.5,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )

        return response.choices[0].message.content

    except Exception:
        return ""

# Diese Funktion bereinigt den HTML-Inhalt einer Webseite und bereitet den Text für die weitere Verarbeitung vor
def clean_text(soup):
  try:

    for script in soup(["script", "style"]):
      script.extract()

    for tag in soup.find_all(['footer', 'nav', 'header']):
      tag.decompose()

    event_attributes = [
    "onabort", "onafterprint", "onbeforeprint", "onbeforeunload", "onblur", "oncanplay", "oncanplaythrough",
    "onchange", "onclick", "oncontextmenu", "oncopy", "oncut", "ondblclick", "ondrag", "ondragend",
    "ondragenter", "ondragleave", "ondragover", "ondragstart", "ondrop", "ondurationchange", "onemptied",
    "onended", "onerror", "onfocus", "onhashchange", "oninput", "oninvalid", "onkeydown", "onkeypress",
    "onkeyup", "onload", "onloadeddata", "onloadedmetadata", "onloadstart", "onmessage", "onmousedown",
    "onmousemove", "onmouseout", "onmouseover", "onmouseup", "onmousewheel", "onoffline", "ononline",
    "onpagehide", "onpageshow", "onpaste", "onpause", "onplay", "onplaying", "onprogress", "onratechange",
    "onreset", "onresize", "onscroll", "onsearch", "onseeked", "onseeking", "onselect", "onstalled",
    "onstorage", "onsubmit", "onsuspend", "ontimeupdate", "ontoggle", "onunload", "onvolumechange",
    "onwaiting", "onwheel"
    ]

    for event in event_attributes:
      elements_with_event = soup.find_all(attrs={event: True})
      for element in elements_with_event:
        element.decompose()

    for div in soup.find_all('div'):
      if len(div.get_text(strip=True)) < 20:
        div.decompose()

    cleaned_text = soup.get_text()

    cleaned_text = re.sub(r'http\S+', '', cleaned_text)
    cleaned_text = re.sub(r'[^a-zA-Z0-9äöüÄÖÜß.,!?%€$]', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    cleaned_text = re.sub(r',+', ', ', cleaned_text)

    sentences = cleaned_text.split('.')
    cleaned_sentences = [s.strip() for s in sentences if len(s.split()) > 3]
    cleaned_text = '. '.join(cleaned_sentences)

    return cleaned_text

  except Exception:
    return ""

def convert_references_to_links(input_string, urls):
    try:
        def replace_reference(match):
            try:
                ref_number = match.group(1)
                if ref_number.isdigit() and int(ref_number) <= len(urls):
                    return f'<a href="{urls[int(ref_number) - 1]}">[{ref_number}]</a>'
                else:
                    return match.group(0)
            except Exception:
                return match.group(0)

        pattern = r'\[(\d+)\]'
        output_string = re.sub(pattern, replace_reference, input_string)
        return output_string

    except Exception:
        return input_string


def array_to_html_links(urls):
    try:
        html_links = [f'<a href="{url}">[{i+1}] {url}</a>' for i, url in enumerate(urls)]
        return html_links
    except Exception:
        raise
