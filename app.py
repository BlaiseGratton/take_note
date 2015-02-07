from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/<name>')
def index(name="Colby"):
    return render_template("index.html", name=name)

@app.route('/notes')
def notes(note1="CRUD is crud!", note2="I'm sad today", note3="Today I'm not!"):
    context = {'note1': note1, 'note2': note2, 'note3': note3}
    return render_template("notes.html", notes=context)

# @app.route('/notes/<note>')

app.run(debug=True, port=8000, host='0.0.0.0')
