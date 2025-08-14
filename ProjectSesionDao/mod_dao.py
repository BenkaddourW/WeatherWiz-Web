import sqlite3

import requests

from mod_classe import Activite

from flask import Flask, jsonify, request

app=Flask(__name__)

def creer_connexion():
    #creer connecion
    return sqlite3.connect('WeatherWizBD.dbf')

def fermer_connexion(conn):
    conn.close()

def creer_table(cde_ddl):
    # obtenir connexion
    conn = creer_connexion()
    # Obtenir le curseur
    curseur = conn.cursor()
    # Creation de la table
    curseur.execute(cde_ddl)

    fermer_connexion(conn)
@app.route('/v1/dao/ins_activite', methods=['POST'])
def inserer_data():
    data=request.get_json()
    #insertion
    cde_ins = '''insert into activite(condition,reponse)values(?,?)
    '''
    # obtenir connexion
    conn = creer_connexion()
    # Obtenir le curseur
    curseur = conn.cursor()
    curseur.execute(cde_ins, [data['condition'],data['reponse']])
    conn.commit()
    fermer_connexion(conn)
    return jsonify({'message': 'insertion OK'}), 201


@app.route('/v1/dao/select_activites', methods=['POST'])
def selectionner_data():
    data = request.get_json()

    if 'condition' not in data:
        return jsonify({'error': 'Condition non fournie'}), 400

    # obtenir connexion
    conn = creer_connexion()
    # Obtenir le curseur
    curseur = conn.cursor()

    # Requête
    requete = 'SELECT reponse FROM activite WHERE condition = ?'
    curseur.execute(requete, [data['condition']])

    resultat = curseur.fetchone()
    fermer_connexion(conn)

    if resultat:
        return jsonify({'reponse': resultat[0]}), 200
    else:
        return jsonify({'error': 'Aucune activité trouvée pour cette condition'}), 404


@app.route('/v1/dao/delete_activite', methods=['POST'])
def supprimer_data():
    data = request.get_json()

    if 'condition' not in data:
        return jsonify({'error': 'Condition non fournie'}), 400

    try:

        # obtenir connexion
        conn = creer_connexion()
        # Obtenir le curseur
        curseur = conn.cursor()

        # D'abord vérifier si l'entrée existe
        curseur.execute('SELECT COUNT(*) FROM activite WHERE condition = ?', [data['condition']])
        existe = curseur.fetchone()[0] > 0

        if not existe:
            return jsonify({'error': 'Aucune activité trouvée pour cette condition'}), 404


        curseur.execute('DELETE FROM activite WHERE condition = ?', [data['condition']])
        nb_lignes = curseur.rowcount
        conn.commit()

        return jsonify({
            'message': f'{nb_lignes} activité(s) supprimée(s)',
            'deleted': True
        }), 200

    except sqlite3.Error as e:
        return jsonify({'error': 'Erreur base de données', 'detail': str(e)}), 500
    finally:
        if conn:
            fermer_connexion(conn)


@app.route('/v1/dao/select_conditions', methods=['GET'])
def selectionner_tout_conditions_data():

    try:
        # obtenir connexion
        conn = creer_connexion()
        # Obtenir le curseur
        curseur = conn.cursor()

        # Requete
        requete = 'SELECT DISTINCT condition FROM activite'
        curseur.execute(requete)

        # Récupérer tous les résultats
        resultats = curseur.fetchall()
        conditions = [row[0] for row in resultats]

        fermer_connexion(conn)
        return jsonify({'conditions': conditions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/v1/dao/select_data', methods=['GET'])
def selectdata():
    try:
        # obtenir connexion
        conn = creer_connexion()
        # Obtenir le curseur
        curseur = conn.cursor()

        # Modifiez la requête pour inclure l'ID
        requete = 'SELECT id, condition, reponse FROM activite'  # Ajout de 'id'
        curseur.execute(requete)

        resultats = curseur.fetchall()
        # Mettez à jour la construction des données pour inclure l'ID
        donnees = [{'id': row[0], 'condition': row[1], 'reponse': row[2]} for row in resultats]

        fermer_connexion(conn)
        return jsonify({'donnees': donnees}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @app.route('/v1/dao/modifie_data', methods=['PUT'])
# def modifie_data():
#     data = request.get_json()
#
#     # Validation minimale - l'ID est requis mais ne sera pas modifié
#     if not data or 'id' not in data:
#         return jsonify({'error': 'ID requis pour identification'}), 400
#
#     conn = creer_connexion()
#     try:
#         curseur = conn.cursor()
#         # Mise à jour explicite uniquement des champs modifiables
#         curseur.execute('''
#             UPDATE activite
#             SET condition = COALESCE(?, condition),
#                 reponse = COALESCE(?, reponse)
#             WHERE id = ?''',
#                         (data.get('condition'), data.get('reponse'), data['id'])
#                         )
#         conn.commit()
#
#         if curseur.rowcount == 0:
#             return jsonify({'warning': 'Aucun enregistrement trouvé avec cet ID'}), 404
#         return jsonify({'success': 'Mise à jour effectuée (ID inchangé)'}), 200
#
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'error': str(e)}), 500
#     finally:
#         conn.close()
@app.route('/v1/dao/modifie_data', methods=['PUT'])
def modifie_data():
    data = request.get_json()

    # Validation minimale - l'ID est requis mais ne sera pas modifié
    if not data or 'id' not in data:
        return jsonify({'error': 'ID requis pour identification'}), 400

    conn = creer_connexion()
    try:
        curseur = conn.cursor()
        # Mise à jour explicite uniquement des champs modifiables
        curseur.execute('''
            UPDATE activite 
            SET condition = COALESCE(?, condition),
                reponse = COALESCE(?, reponse)
            WHERE id = ?''',
                        (data.get('condition'), data.get('reponse'), data['id'])
                        )
        conn.commit()

        if curseur.rowcount == 0:
            return jsonify({'warning': 'Aucun enregistrement trouvé avec cet ID'}), 404
        return jsonify({'success': 'Mise à jour effectuée (ID inchangé)'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/v1/activite/select_activites_byid/<int:id>', methods=['GET'])
def get_activite_by_id(id):
    conn = creer_connexion()
    curseur = None
    try:
        curseur = conn.cursor()  # Create cursor without 'with'

        requete = 'SELECT condition, reponse FROM activite WHERE id = ?'
        curseur.execute(requete, (id,))
        resultat = curseur.fetchone()

        if resultat:
            response = jsonify({
                'id': id,
                'condition': resultat[0],
                'reponse': resultat[1]
            })
        else:
            response = jsonify({'erreur': 'Activité non trouvée'}), 404

    except Exception as e:
        response = jsonify({'erreur': str(e)}), 500
    finally:
        if curseur:
            curseur.close()
        fermer_connexion(conn)

    return response

if __name__ == '__main__':
    app.run(debug=True,port=5600)