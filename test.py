from flask import Flask, render_template, Response, request, jsonify
from sql import init_db, start_session,  Message
from func import get_response_stream, search, scrape
from dotenv import load_dotenv
from uuid import uuid4
import os
import concurrent.futures

load_dotenv(os.getcwd() + '/.env')

engine = init_db()
start_session(engine)