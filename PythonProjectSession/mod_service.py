import requests
from flask import Flask, request, jsonify
from flasgger import Swagger

app=Flask(__name__)

# Configuration de Swagger
app.config['SWAGGER'] = {
    'title': 'API Statut Activité',
    'version': '1.0',
    'description': 'API pour obtenir le statut des activités selon une condition',
    'uiversion': 3
}
Swagger(app)

@app.route('/v1/activite/statut', methods=['GET','POST'])
def get_statut():
    """
        Endpoint pour obtenir le statut des activités selon une condition
        ---
        tags:
          - Activité
        parameters:
          - name: condition
            in: query
            type: string
            required: true
            description: Condition de recherche pour filtrer les activités
        responses:
          200:
            description: Liste des activités correspondant à la condition
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Réponse contenant les activités
          400:
            description: Condition non fournie
          404:
            description: Aucune activité trouvée
          500:
            description: Erreur serveur
        """
    if request.method == 'GET':
        condition = request.args.get('condition')
        if not condition:
            return jsonify({'error': 'Condition non fournie'}), 400
        data = {'condition': condition}
    else:  # POST
        data = request.get_json()
        if not data or 'condition' not in data:
            return jsonify({'error': 'Condition non fournie'}), 400

    # Interroger le DAO pour obtenir la réponse
    dao_response = requests.post(
        'http://127.0.0.1:5600/v1/dao/select_activites',
        json={'condition': data['condition']}
    )

    if dao_response.status_code == 200:
        message = dao_response.json()['reponse']
        return jsonify({'message': message}), 200
    elif dao_response.status_code == 404:
        return jsonify({'error': 'Aucune activite trouvee pour cette condition'}), 404
    else:
        return jsonify({'error': 'Erreur lors de la recherche de la condition'}), dao_response.status_code

#####################################################

@app.route('/v1/activite/insertion', methods=['POST'])
def inserer_data():
    """
                Endpoint pour insérer une nouvelle activité
                ---
                tags:
                  - Activité
                description: Insère une nouvelle activité avec une condition et une réponse associée
                consumes:
                  - application/json
                produces:
                  - application/json
                parameters:
                  - in: body
                    name: body
                    description: Données de l'activité à insérer
                    required: true
                    schema:
                      type: object
                      required:
                        - condition
                        - reponse
                      properties:
                        condition:
                          type: string
                          description: Condition pour l'activité
                          example: "status=active"
                        reponse:
                          type: string
                          description: Réponse associée à la condition
                          example: "L'activité est active"
                responses:
                  200:
                    description: Insertion réussie
                    schema:
                      type: object
                      properties:
                        message:
                          type: string
                          example: "Insertion réussie"
                  400:
                    description: Données manquantes ou invalides
                    schema:
                      type: object
                      properties:
                        error:
                          type: string
                          example: "Condition et reponse sont requises"
                  500:
                    description: Erreur lors de l'insertion
                    schema:
                      type: object
                      properties:
                        error:
                          type: string
                          example: "Erreur lors de l'insertion"
                        detail:
                          type: string
                          example: "Erreur de connexion à la base de données"
                """
    data = request.get_json()

    if 'condition' not in data or 'reponse' not in data:
        return jsonify({'error': 'Condition et reponse sont requises'}), 400

    # Faire un POST vers le DAO
    uri_ins = 'http://127.0.0.1:5600/v1/dao/ins_activite'
    dao_response = requests.post(uri_ins, json=data)

    if dao_response.status_code == 201:
        return jsonify({'message': 'Insertion réussie'}), 200
    else:
        return jsonify({'error': 'Erreur lors de l\'insertion', 'detail': dao_response.text}), 500

#####################################################

@app.route('/v1/activite/suppression', methods=['POST'])
def delete_statut():
    """
       Endpoint pour supprimer une activité
       ---
       tags:
         - Activité
       description: Supprime une activité selon une condition
       consumes:
         - application/json
       produces:
         - application/json
       parameters:
         - in: body
           name: body
           description: Condition pour identifier l'activité à supprimer
           required: true
           schema:
             type: object
             required:
               - condition
             properties:
               condition:
                 type: string
                 example: "id=123"
       responses:
         200:
           description: Suppression réussie
           schema:
             $ref: '#/definitions/StandardResponse'
         400:
           description: Condition non fournie
         404:
           description: Activité non trouvée
         500:
           description: Erreur serveur
       """

    data = request.get_json()
    if 'condition' not in data:
        return jsonify({'error': 'Condition non fournie'}), 400

    dao_response = requests.post(
        'http://127.0.0.1:5600/v1/dao/delete_activite',
        json={'condition': data['condition']}
    )

    return jsonify(dao_response.json()), dao_response.status_code


#####################################################
@app.route('/v1/activite/conditions', methods=['GET'])
def get_all_conditions():
    """
       Endpoint pour récupérer toutes les conditions disponibles
       ---
       tags:
         - Activité
       description: Retourne la liste de toutes les conditions enregistrées
       responses:
         200:
           description: Liste des conditions
           schema:
             type: object
             properties:
               conditions:
                 type: array
                 items:
                   type: string
                 example: ["status=active", "type=event"]
         500:
           description: Erreur serveur
           schema:
             $ref: '#/definitions/ErrorResponse'
       """
    try:
        # Appel au DAO
        dao_response = requests.get('http://127.0.0.1:5600/v1/dao/select_conditions')

        if dao_response.status_code == 200:

            conditions = dao_response.json().get('conditions', [])
            return jsonify({'conditions': conditions}), 200
        else:
            return jsonify({
                'error': 'Erreur lors de la récupération des conditions',
                'details': dao_response.json()
            }), dao_response.status_code

    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

#########################################################
@app.route('/v1/activite/alldata', methods=['GET'])
def get_all_data():
    """
       Endpoint pour récupérer toutes les données d'activité
       ---
       tags:
         - Activité
       description: Retourne toutes les données d'activité (condition + réponse)
       responses:
         200:
           description: Liste complète des données
           schema:
             type: object
             properties:
               donnees:
                 type: array
                 items:
                   type: object
                   properties:
                     condition:
                       type: string
                     reponse:
                       type: string
         500:
           description: Erreur serveur
       """
    try:
        # Appel au DAO
        dao_response = requests.get('http://127.0.0.1:5600/v1/dao/select_data')

        if dao_response.status_code == 200:
            # Récupérer la liste des données contenant à la fois condition et reponse
            donnees = dao_response.json().get('donnees', [])
            return jsonify({'donnees': donnees}), 200
        else:
            return jsonify({
                'error': 'Erreur lors de la récupération des données',
                'details': dao_response.json()
            }), dao_response.status_code

    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

########################################

@app.route('/v1/activite/update', methods=['PUT'])
def update_data():
    """
    Endpoint pour mettre à jour une activité (sans modifier l'ID)
    ---
    tags:
      - Activité
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - id
            - condition
            - reponse
          properties:
            id:
              type: integer
              readOnly: true  # Marquer l'ID comme non modifiable
              example: 1
            condition:
              type: string
            reponse:
              type: string
    """
    data = request.get_json() or {}

    # Validation renforcée
    if 'id' not in data:
        return jsonify({'error': 'ID est requis pour identifier l\'enregistrement'}), 400

    if not isinstance(data['id'], int) or data['id'] <= 0:
        return jsonify({'error': 'ID doit être un entier positif'}), 400

    # Appel au DAO - Seuls condition et reponse sont transmis pour modification
    dao_response = requests.put(
        'http://127.0.0.1:5600/v1/dao/modifie_data',
        json={
            'id': data['id'],  # Utilisé seulement pour identification
            'condition': data.get('condition'),
            'reponse': data.get('reponse')
        },
        timeout=10
    )

    return jsonify(dao_response.json()), dao_response.status_code

##################byid############/
@app.route('/v1/activite/select_activites_byid/<int:id>', methods=['GET'])
def handle_activite_request(id):
    """
    Endpoint pour récupérer une activité par son ID
    ---
    tags:
      - Activité
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de l'activité à récupérer
    responses:
      200:
        description: Détails de l'activité
      404:
        description: Activité non trouvée
      502:
        description: Erreur de connexion au DAO
      504:
        description: Timeout du DAO
    """
    try:
        # Appel au DAO en GET
        dao_response = requests.get(
            f'http://127.0.0.1:5600/v1/activite/select_activites_byid/{id}',
            timeout=3
        )

        return jsonify(dao_response.json()), dao_response.status_code
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'DAO_TIMEOUT',
            'message': 'Le service DAO ne répond pas'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'DAO_CONNECTION_ERROR',
            'details': str(e)
        }), 502


if __name__ == '__main__':
    app.run(debug=True,port=5000)