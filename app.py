from flask import Flask, render_template, request, url_for, redirect
import mysql.connector


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def accueil():
    return render_template('vueAccueil.html')


@app.route('/ajoutMatiereMenu', methods=['GET'])
def ajoutMatiereMenu():
    return render_template('vueAjoutMatiere.html')


@app.route('/ajoutMatiereMenu/<idMatiere>', methods=['GET'])
def modifierMatiereMenu(idMatiere):
    storage = Storage()
    data = storage.loadMatiere(idMatiere)
    matiere = {'id': str(data[0][0]), 'nom': data[0][1], 'description': data[0][2], 'heures': str(data[0][3])}
    return render_template('vueModifierMatiere.html', matiere=matiere)


@app.route('/voirMatieres', methods=['GET'])
def voirMatieres():
    matieres = []
    storage = Storage()
    data = storage.loadAll()
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

@app.route('/modifierMatiere', methods=['POST'])
def modifierMatiere():
    data = request.form
    matiere = {'nom': data['nom'], 'description': data['description'], 'heures': int(data['heures'])}
    storage = Storage()
    storage.updateMatiere(matiere)
    return render_template('vueAccueil.html')


@app.route('/supprimerMatiere/<idMatiere>', methods=['GET'])
def supprimerMatiere(idMatiere):
    storage = Storage()
    storage.deleteMatiere(idMatiere)
    return redirect(url_for('voirMatieres'))


class Storage:
    def __init__(self):
        self.db = mysql.connector.connect(
            user='AdminPartiel',
            passwd='PARTIELaws1#',
            db='Partieldatabase',
            host='partielrds.c46hgutu5jsv.us-east-1.rds.amazonaws.com',
            port=3306
        )

    def loadAll(self):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres ''')
        data = cur.fetchall()
        return data

    def loadMatiere(self, idMatiere):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres WHERE id = %s ''', idMatiere)
        matiere = cur.fetchall()
        return matiere

    def addMatiere(self, matiere):
        cur = self.db.cursor()
        cur.execute(''' INSERT INTO Matieres(nom, description, heures) VALUES (%s, %s, %s) '''
                    , (matiere['nom'], matiere['description'], matiere['heures']))
        self.db.commit()

    def deleteMatiere(self, idMatiere):
        cur = self.db.cursor()
        cur.execute(''' DELETE FROM Matieres WHERE id = %s) '''
                    , idMatiere)
        self.db.commit()

    def updateMatiere(self, matiere):
        cur = self.db.cursor()
        cur.execute(''' UPDATE Matieres SET nom = %s, description = %s, heures = %s WHERE id = %s) '''
                    , (matiere['nom'], matiere['description'], matiere['heures']))
        self.db.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
