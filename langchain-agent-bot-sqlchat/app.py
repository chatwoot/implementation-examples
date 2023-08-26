import requests

from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from flask import Flask, request

# Database details
postgresql_host = ''
postgresql_port = ''
postgresql_user = ''
postgresql_pass = ''
postgresql_dbname = ''

# OpenAI API Key
key = ''

# Include only tables that you needed
include_tables=[]

# ChatWoot config
chatwoot_url = ""
chatwoot_bot_token = ""

# SQLDatabase connection string
conn_stg = f"postgresql+psycopg2://{postgresql_user}:{postgresql_pass}@{postgresql_host}/{postgresql_dbname}"

llm = OpenAI(temperature=0, openai_api_key=key) # type: ignore
db = SQLDatabase.from_uri(conn_stg, include_tables=include_tables)
db_chain = SQLDatabaseChain.from_llm(llm, db, use_query_checker=True)

app = Flask(__name__)

def send_to_chatwoot(account, conversation, message):
    data = {
        'content': message
    }
    url = f"{chatwoot_url}/api/v1/accounts/{account}/conversations/{conversation}/messages"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "api_access_token": f"{chatwoot_bot_token}"}

    r = requests.post(url,
                      json=data, headers=headers)
    return r.json()


@app.route('/langchain', methods=['POST']) # type: ignore
def langchain():

    chatwoot_msg = 'None'

    data = request.get_json()

    message_type = data['message_type']
    message = data['content']
    conversation = data['conversation']['id']
    contact = data['sender']['id']
    account = data['account']['id']

    if message_type == 'incoming':
        ai_msg = db_chain.run(message) # type: ignore
        chatwoot_msg = send_to_chatwoot(account, conversation, ai_msg)

    return chatwoot_msg
