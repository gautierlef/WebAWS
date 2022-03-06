from flask import Flask, render_template, request
import mysql.connector


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def accueil():
    return render_template('vueAccueil.html')


@app.route('/ajoutMatiereMenu', methods=['GET'])
def ajoutMatiereMenu():
    return render_template('vueAjoutMatiere.html')


@app.route('/voirMatieres', methods=['GET'])
def voirMatieres():
    matieres = []
    storage = Storage()
    data = storage.load()
    print(data)
    for row in data:
        matieres.append({'id': str(row[0]), 'nom': row[1], 'description': row[2], 'heures': str(row[3])})
    return render_template('vueMatieres.html', matieres=matieres)


@app.route('/ajoutMatiere', methods=['POST'])
def ajoutMatiere():
    data = request.form
    matiere = {'nom': data['nom'], 'description': data['description'], 'heures': int(data['heures'])}
    storage = Storage()
    storage.addMatiere(matiere)
    return render_template('vueAccueil.html')


class Storage:
    def __init__(self):
        self.db = mysql.connector.connect(
            user='AdminPartiel',
            passwd='PARTIELaws1#',
            db='Partieldatabase',
            host='partielrds.c46hgutu5jsv.us-east-1.rds.amazonaws.com',
            port=3306
        )

    def load(self):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres ''')
        data = cur.fetchall()
        return data

    def addMatiere(self, matiere):
        cur = self.db.cursor()
        cur.execute(''' INSERT INTO Matieres(nom, description, heures) VALUES (%s, %s, %s) '''
                    , (matiere['nom'], matiere['description'], matiere['heures']))
        self.db.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)