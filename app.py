# app.py
from flask import Flask, session, redirect, render_template
from flask import request, make_response, json
from functools import wraps
import dictToXML
app = Flask(__name__)
app.secret_key = "notSoObviousSecretKey"

uuid_base = 'uuid_'


def authorization(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return decorated


@app.route('/login', methods=['POST', 'GET'])
def login():
    auth = request.authorization
    if auth and auth.username == 'TRAIN' and auth.password == 'TuN3L':
        session['logged_in'] = True
        return redirect('/hello')
    else:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required'})


@app.route('/logout', methods=['POST', 'GET'])
@authorization
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        return redirect('/')
    else:
        return redirect('/login')


@app.route('/')
def start():
    return "hello"


@app.route('/hello', methods=['GET'])
@authorization
def hello():
    return render_template('hello.html', user='TRAIN')


@app.route('/trains', methods=['POST'])
@authorization
def trains_post():
    with open('resources/trains.json', 'r') as f:
        try:
            data = json.load(f)
        except:
            data = None
    request_data = request.get_json(force=True)
    if data is None:
        data = dict()
        data[uuid_base + str(1)] = request_data
    else:
        trains_count = len(data)
        data[uuid_base + str(trains_count+1)] = request_data
    with open('resources/trains.json', 'w') as f:
        json.dump(data, f)
    return redirect('/trains/'+str(trains_count+1)+'?format=json')


@app.route('/trains', methods=['GET'], defaults={'id': None})
@app.route('/trains/<int:id>', methods=['GET'])
@authorization
def trains_get(id):
    with open('resources/trains.json', 'r') as f:
        data = json.load(f)
    data_format = request.args.get('format')
    if data_format == 'json':
        if id is not None:
            return json.jsonify(data[uuid_base+str(id)])
        else:
            return json.jsonify(data)
    else:
        return dictToXML.dict_to_xml(data)


if __name__ == '__main__':
    app.run(debug=True)
