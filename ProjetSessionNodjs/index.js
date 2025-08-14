const express = require('express');
const axios = require('axios').default;
const path = require('path'); // N'oubliez pas d'importer path
const app = express();
const cors = require('cors');
// Configuration des vues
app.set('views', path.join(__dirname, 'views')); // Une seule configuration suffit
app.set('view engine', 'ejs');

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cors());

// Route pour la page d'accueil
app.get('/', (req, res) => {
    res.render('accueil'); 
});


// // Route pour récupérer les conditions
// app.get('/getAll', async (req, res) => {
//     try {
//         const response = await axios.get('http://127.0.0.1:5000/v1/activite/conditions');
//         const conditions = response.data.conditions || [];
//         res.render('choix', { conditions });
//     } catch (error) {
//         console.error("Erreur:", error);
//         res.status(500).render('error', { 
//             message: "Échec du chargement des conditions",
//             error: error.message 
//         });
//     }
// });


// app.get('/getReponse', async (req, res) => {
//     try {
//         const selectedCondition = req.query.condition;
        
//         const response = await axios.post(
//             'http://127.0.0.1:5000/v1/activite/statut',
//             { condition: selectedCondition }
//         );

//         res.render('afficherReponse', { 
//             activite: response.data.activite,
//             message: response.data.message,
//             condition: selectedCondition
//         });
//     } catch (error) {
//         console.error("Erreur:", error);
//         res.status(500).render('error', { 
//             message: "Échec de la récupération",
//             error: error.response?.data || error.message
//         });
//     }
// });



//  récupérer les conditions et le reponses en JSON
app.get('/getalldata', async (req, res) => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/v1/activite/conditions');
        const conditions = response.data.conditions || [];
        res.json({ conditions }); // Retourne les données en JSON
    } catch (error) {
        console.error("Erreur:", error);
        res.status(500).json({ 
            error: true,
            message: "Échec du chargement des conditions",
            details: error.message 
        });
    }
});
///////////////
app.get('/getdata', async (req, res) => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/v1/activite/alldata');
        const donnees = response.data.donnees || [];
        

        res.json({ donnees: donnees });
        

    } catch (error) {
        console.error("Erreur:", error);
        res.status(500).json({ 
            error: true,
            message: "Échec du chargement des données",
            details: error.message 
        });
    }
});

// recuperer la condition et evloyer la reponse
app.post('/getreponse', async (req, res) => {
    try {
        const selectedCondition = req.body.condition;
        
        if (!selectedCondition) {
            return res.status(400).json({ 
                message: "Le paramètre 'condition' est requis" 
            });
        }

        const response = await axios.post(
            'http://127.0.0.1:5000/v1/activite/statut',
            { condition: selectedCondition }
        );

        res.json(response.data);
    } catch (error) {
        console.error("Erreur:", error);
        const statusCode = error.response?.status || 500;
        res.status(statusCode).json({
            message: "Échec de la récupération",
            error: error.response?.data || error.message
        });
    }
});



// Route pour ajouter une condition

app.post('/addcondition', async (req, res) => {
    try {
        const { condition, reponse } = req.body;

        // Validation des données
        if (!condition || !reponse) {
            return res.status(400).json({
                message: "Condition et reponse sont requises"
            });
        }

        // Appel au middleware Python
        const response = await axios.post(
            'http://127.0.0.1:5000/v1/activite/insertion',
            { condition, reponse }
        );

        // Retourner la réponse du middleware
        res.status(response.status).json(response.data);

    } catch (error) {
        console.error("Erreur:", error);
        const statusCode = error.response?.status || 500;
        res.status(statusCode).json({
            message: "Échec de l'ajout de la condition",
            error: error.response?.data || error.message
        });
    }
});


// suprrimer les datas
app.delete('/deletedata', async (req, res) => {
    try {
        if (!req.body.condition) {
            return res.status(400).json({ 
                error: "Le paramètre 'condition' est requis" 
            });
        }

        const response = await axios.post(
            'http://127.0.0.1:5000/v1/activite/suppression',
            { condition: req.body.condition }
        );

        res.status(response.status).json(response.data);

    } catch (error) {
        const status = error.response?.status || 500;
        const message = error.response?.data || error.message;
        
        res.status(status).json({ 
            error: "Échec de la suppression",
            details: message 
        });
    }
});
// 
app.put('/updatedata/:id', async (req, res) => {
    try {
        const { condition, reponse } = req.body;
        const { id } = req.params;

        // Validation
        if (!condition || !reponse) {
            return res.status(400).json({
                error: "Les paramètres 'condition' et 'reponse' sont requis"
            });
        }

        if (!id || isNaN(id)) {
            return res.status(400).json({
                error: "ID invalide ou manquant"
            });
        }

        // Appel au service Flask avec PUT
        const response = await axios.put(
            'http://127.0.0.1:5000/v1/activite/update',
            { 
                id: parseInt(id), // Conversion en nombre
                condition, 
                reponse 
            }
        );

        res.status(response.status).json(response.data);
    } catch (error) {
        console.error("Erreur update:", error);
        const status = error.response?.status || 500;
        const message = error.response?.data || error.message;
        
        res.status(status).json({
            error: "Échec de la mise à jour",
            details: message
        });
    }
});


app.get('/byid/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        // 
        const response = await axios.get(
            `http://127.0.0.1:5000/v1/activite/select_activites_byid/${id}`
        );
        
        res.status(response.status).json(response.data);
        
    } catch (error) {
        if (error.response) {

            // erreur
            res.status(error.response.status).json(error.response.data);
        } else {

            // Erreur de connexion 
            res.status(500).json({ 
                error: 'Erreur interne du serveur',
                details: error.message 
            });
        }
    }
});

app.listen(3005, () => {
    console.log(`Server Started at ${3005}`);
});