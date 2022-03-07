from flask import Flask, render_template, request, url_for, redirect, current_app, send_from_directory, Response
import mysql.connector
import boto3
import os


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def accueil():
    return render_template('vueAccueil.html')


@app.route('/ajoutMatiereMenu', methods=['GET'])
def ajoutMatiereMenu():
    return render_template('vueAjoutMatiere.html')


@app.route('/modifierMatiereMenu/<idMatiere>', methods=['POST'])
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
    for row in data:
        matieres.append({'id': str(row[0]), 'nom': row[1], 'description': row[2], 'heures': str(row[3])})
    return render_template('vueMatieres.html', matieres=matieres)


@app.route("/telechargerCSV")
def telechargerCSV():
    s3client = boto3.client("s3")
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-east-1",
        aws_access_key_id="AKIAZMSAVZUGSJ7DUL5J",
        aws_secret_access_key="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"
    )
    parielaws1 = s3.Bucket('parielaws1')
    for obj in parielaws1.objects.all():
        path, filename = os.path.split(obj.key)
        parielaws1.download_file(obj.key, filename)
    with open("matieres.csv") as f:
        csv = f.read()
    f.close()
    os.remove("matieres.csv")
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=matieres.csv"})


@app.route('/envoyerRDStoS3', methods=['GET'])
def envoyerRDStoS3():
    storage = Storage()
    data = storage.loadAll()
    newCSV = 'id,nom,description,heures\n'
    for row in data:
        newCSV += str(row[0]) + ',' + row[1] + ',' + row[2] + ',' + str(row[3]) + '\n'
    f = open("matieres.csv", "w")
    f.write(newCSV)
    f.close()
    s3Client = boto3.client("s3")
    s3Client.upload_file(
        Filename="matieres.csv",
        Bucket="parielaws1",
        Key="matieres.csv",
    )
    os.remove("matieres.csv")
    return redirect('/')


@app.route('/envoyerS3toRDS', methods=['GET'])
def envoyerS3toRDS():
    s3client = boto3.client("s3")
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-east-1",
        aws_access_key_id="AKIAZMSAVZUGSJ7DUL5J",
        aws_secret_access_key="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"
    )
    parielaws1 = s3.Bucket('parielaws1')
    for obj in parielaws1.objects.all():
        path, filename = os.path.split(obj.key)
        parielaws1.download_file(obj.key, filename)
    with open("matieres.csv") as f:
        csv = f.read()
    f.close()
    storage = Storage()
    storage.replaceFromCSV(csv)
    os.remove("matieres.csv")
    return redirect('/')


@app.route('/ajoutMatiere', methods=['POST'])
def ajoutMatiere():
    data = request.form
    matiere = {'nom': data['nom'], 'description': data['description'], 'heures': int(data['heures'])}
    storage = Storage()
    storage.addMatiere(matiere)
    return redirect(url_for('voirMatieres'))


@app.route('/modifierMatiere/<idMatiere>', methods=['POST'])
def modifierMatiere(idMatiere):
    data = request.form
    matiere = {'id': idMatiere, 'nom': data['nom'], 'description': data['description'], 'heures': int(data['heures'])}
    storage = Storage()
    storage.updateMatiere(matiere)
    return redirect(url_for('voirMatieres'))


@app.route('/supprimerMatiere/<idMatiere>', methods=['POST'])
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
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres WHERE id = %s ''', (idMatiere, ))
        matiere = cur.fetchall()
        return matiere

    def addMatiere(self, matiere):
        cur = self.db.cursor()
        cur.execute(''' INSERT INTO Matieres(nom, description, heures) VALUES (%s, %s, %s) '''
                    , (matiere['nom'], matiere['description'], matiere['heures']))
        self.db.commit()

    def deleteMatiere(self, idMatiere):
        cur = self.db.cursor()
        cur.execute(''' DELETE FROM Matieres WHERE id = %s ''', (idMatiere, ))
        self.db.commit()

    def updateMatiere(self, matiere):
        cur = self.db.cursor()
        cur.execute(''' UPDATE Matieres SET nom = %s, description = %s, heures = %s WHERE id = %s '''
                    , (matiere['nom'], matiere['description'], matiere['heures'], matiere['id']))
        self.db.commit()

    def replaceFromCSV(self, csv):
        cur = self.db.cursor()
        cur.execute('''DELETE FROM Matieres''')
        matieres = csv.split('\n')
        matieres.pop(0)
        matieres.pop()
        for matiere in matieres:
            data = matiere.split(',')
            cur.execute(''' INSERT INTO Matieres(id, nom, description, heures) VALUES (%s, %s, %s, %s) '''
                        , (data[0], data[1], data[2], data[3]))
        self.db.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
