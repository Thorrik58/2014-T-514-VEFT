import json
from elasticsearch import Elasticsearch
from flask import Flask, request, Response
from db import Session
from models import Entry


app = Flask(__name__)


@app.route('/api/entries', methods=["GET", "POST"])
def list_entries():
    if request.method == 'POST':
        data = json.loads(request.data)
        title = data.get('title')
        content = data.get('content')

        session = Session()
        entry = Entry(title=title, content=content)
        session.add(entry)
        session.commit()

        return 'ok'

    else:
        session = Session()
        entries = session.query(Entry).all()
        return Response(json.dumps(
            [{"title": x.title, "content": x.content} for x in entries]),
                        mimetype='application/json')


@app.route('/api/search', methods=['POST'])
def search():
    res = []
    es = Elasticsearch()
    data = json.loads(request.data)

    search_body = {
        "query": {
            "query_string": {
                "query": data.get('search')
            }
        }
    }

    for x in es.search(body=search_body).get('hits').get('hits'):
        _src = x.get('_source')
        entry = {'id': x.get('_id')}
        entry.update(_src)
        res.append(entry)

    return json.dumps(res)
