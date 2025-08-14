from doctest import debug

from mod_classe import Activite
from mod_dao import creer_table, inserer_data, selectionner_data

# from flask import Flask
# app=Flask(__name__)

def creer_activite():

    condition= input('Saisir la condition:')
    reponse = input('Saisir la reponse:')

    return Activite(condition,reponse)

def afficher_data(registre):
    for tmp in registre:
        print(tmp)

def main():
    cde_ddl = '''create table if not exists activite(
            id integer primary key autoincrement,
            condition text,
            reponse text
            )
            '''

    # creer table
    creer_table(cde_ddl)

    # creer un objet
    activite=creer_activite()
    #inserer
    inserer_data(activite)

    #selectionner
    registre = selectionner_data()
    # Afficher le contenu qui est dans la table selon condition
    afficher_data(registre)

# if __name__ == '__main__':
#     app.run(debug=True,port=5600)