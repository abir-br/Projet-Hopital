from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect("../../bdd/hopital.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM personnel WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and user['mot_de_passe'] == password:
            session['user'] = user['id']
            session['user_type'] = user['type']  # Stocke le type d'utilisateur
            
            # Redirection selon le type d'utilisateur
            if user['type'] == 'medecin':
                return redirect(url_for('medecin'))
            elif user['type'] == 'infirmier':
                session['infirmier_id'] = user['id']  # Stocker l'ID de l'infirmier dans la session
                return redirect(url_for('infirmier'))
            else:
                return redirect(url_for('login'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')

    return render_template('index.html')

@app.route('/medecin')
def medecin():
    return render_template('medecin/medecin.html')

@app.route('/patients')
def patients():
    medecin_id = session.get('user')  # L'ID du médecin dans la session

    if not medecin_id:
        return redirect(url_for('login'))  # Si pas de médecin connecté, rediriger vers la page de connexion

    conn = get_db_connection()
    # Récupérer les patients liés à ce médecin, même s'ils n'ont pas encore de visite médicale
    patients = conn.execute('''
        SELECT patient.* 
        FROM patient 
        LEFT JOIN visite_medicale 
        ON patient.id = visite_medicale.patient_id
        WHERE visite_medicale.medecin_id = ? OR visite_medicale.medecin_id IS NULL
    ''', (medecin_id,)).fetchall()  # Utilisation de LEFT JOIN pour inclure les patients sans visite
    conn.close()

    return render_template('medecin/patients.html', patients=patients)



@app.route('/ajouter_patient', methods=['POST'])
def ajouter_patient():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        date_naissance = request.form['date_naissance']
        sexe = request.form['sexe']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        antecedents = request.form['antecedents']
        raison = request.form['raison']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO patient (nom, prenom, date_naissance, sexe, adresse, telephone, antecedents, raison_hospitalisation) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (nom, prenom, date_naissance, sexe, adresse, telephone, antecedents, raison)
        )
        conn.commit()
        conn.close()

        # Rediriger vers la page des patients après l'ajout
        return redirect(url_for('patients'))

    
@app.route('/get_patient/<int:id>', methods=['GET'])
def get_patient(id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patient WHERE id = ?', (id,)).fetchone()
    conn.close()

    if patient:
        return jsonify(dict(patient))
    else:
        return jsonify({'error': 'Patient non trouvé'}), 404


@app.route('/modifier_patient', methods=['POST'])
def modifier_patient():
    if request.method == 'POST':
        id = request.form['id']
        nom = request.form['nom']
        prenom = request.form['prenom']
        date_naissance = request.form['date_naissance']
        sexe = request.form['sexe']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        antecedents = request.form['antecedents']
        raison = request.form['raison']

        conn = get_db_connection()
        conn.execute(
            'UPDATE patient SET nom = ?, prenom = ?, date_naissance = ?, sexe = ?, '
            'adresse = ?, telephone = ?, antecedents = ?, raison_hospitalisation = ? '
            'WHERE id = ?',
            (nom, prenom, date_naissance, sexe, adresse, telephone, antecedents, raison, id)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('patients'))


@app.route('/visites/patient/<int:patient_id>')
def get_visites_patient(patient_id):
    conn = get_db_connection()
    visites = conn.execute('SELECT * FROM visite_medicale WHERE patient_id = ?', (patient_id,)).fetchall()
    conn.close()

    # Convertir en liste de dictionnaires
    visites_list = [dict(visite) for visite in visites]
    return jsonify(visites_list)

@app.route('/api/soins/<int:patient_id>', methods=['GET'])
def get_soins(patient_id):
    conn = get_db_connection()
    soins = conn.execute('SELECT * FROM soin WHERE patient_id = ?', (patient_id,)).fetchall()
    conn.close()

    soins_list = []
    for soin in soins:
        soins_list.append({
            'id': soin['id'],
            'infirmier_id': soin['infirmier_id'],
            'date_soin': soin['date_soin'],
            'heure_soin': soin['heure_soin'],
            'description': soin['description']
        })

    return jsonify(soins_list)


@app.route('/api/sejours/<int:patient_id>', methods=['GET'])
def get_sejours(patient_id):
    conn = get_db_connection()
    sejours = conn.execute('SELECT * FROM sejour WHERE patient_id = ?', (patient_id,)).fetchall()
    conn.close()

    sejours_list = []
    for sejour in sejours:
        sejours_list.append({
            'id': sejour['id'],
            'lit_id': sejour['lit_id'],
            'date_arrivee': sejour['date_arrivee'],
            'date_sortie_prevue': sejour['date_sortie_prevue'],
            'date_sortie_reelle': sejour['date_sortie_reelle'],
            'employe_admin_id': sejour['employe_admin_id']
        })

    return jsonify(sejours_list)

@app.route('/api/medicaments/<int:patient_id>')
def get_medicaments(patient_id):
    conn = get_db_connection()
    medicaments = conn.execute('''
        SELECT m.id, m.nom, ms.quantite 
        FROM medicament m
        JOIN medicament_soin ms ON m.id = ms.medicament_id
        JOIN soin s ON ms.soin_id = s.id
        WHERE s.patient_id = ?
    ''', (patient_id,)).fetchall()
    conn.close()
    return jsonify([dict(m) for m in medicaments])

# Route pour supprimer un patient
@app.route('/supprimer_patient/<int:patient_id>', methods=['DELETE'])
def supprimer_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Supprimer d'abord les dépendances (visites, soins, séjours) si elles existent !
    cursor.execute('DELETE FROM visite_medicale WHERE patient_id = ?', (patient_id,))
    cursor.execute('DELETE FROM soin WHERE patient_id = ?', (patient_id,))
    cursor.execute('DELETE FROM sejour WHERE patient_id = ?', (patient_id,))
    
    # Supprimer ensuite le patient
    cursor.execute('DELETE FROM patient WHERE id = ?', (patient_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/reunions')
def reunions():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']  # l'id du médecin connecté

    conn = get_db_connection()

    # On récupère d'abord toutes les réunions du médecin
    reunions_rows = conn.execute('''
        SELECT r.*
        FROM reunion r
        JOIN participants_reunion pr ON r.id = pr.reunion_id
        WHERE pr.personnel_id = ?
    ''', (user_id,)).fetchall()

    # Pour chaque réunion, on récupère les participants
    reunions = []
    for row in reunions_rows:
        participants_rows = conn.execute('''
            SELECT p.nom, p.prenom
            FROM personnel p
            JOIN participants_reunion pr ON p.id = pr.personnel_id
            WHERE pr.reunion_id = ?
        ''', (row['id'],)).fetchall()

        participants = [f"{p['prenom']} {p['nom']}" for p in participants_rows]

        reunions.append({
            'id': row['id'],
            'date_reunion': row['date_reunion'],
            'heure_reunion': row['heure_reunion'],
            'participants': participants
        })

    conn.close()

    return render_template('medecin/reunions.html', reunions=reunions)


@app.route('/services')
def services():
    if 'user' not in session:
        return redirect(url_for('login'))

    medecin_id = session['user']
    conn = get_db_connection()
    
    # Récupérer les informations du service dont le médecin est référent
    services = conn.execute(
        '''
        SELECT 
            s.id, 
            s.nom AS service_nom,
            p.id AS admin_id,
            p.nom AS admin_nom,
            p.prenom AS admin_prenom,
            m.id AS medecin_id,
            pm.nom AS medecin_nom,
            pm.prenom AS medecin_prenom
        FROM medecin m
        JOIN service s ON m.service_id = s.id
        LEFT JOIN admin a ON s.admin_responsable_id = a.id
        LEFT JOIN personnel p ON a.id = p.id
        JOIN personnel pm ON m.id = pm.id
        WHERE m.id = ?
        ''',
        (medecin_id,)
    ).fetchall()

    # Récupérer tous les médecins, infirmiers et patients du même service
    personnel_service = {'medecins': [], 'infirmiers': [], 'patients': []}
    if services:
        service_id = services[0]['id']
        
        # Médecins du service
        personnel_service['medecins'] = conn.execute('''
            SELECT p.id, p.nom, p.prenom 
            FROM medecin m
            JOIN personnel p ON m.id = p.id
            WHERE m.service_id = ?
        ''', (service_id,)).fetchall()
        
        # Infirmiers du service
        personnel_service['infirmiers'] = conn.execute('''
            SELECT p.id, p.nom, p.prenom 
            FROM infirmier i
            JOIN personnel p ON i.id = p.id
            WHERE i.service_id = ?
        ''', (service_id,)).fetchall()
        
        # Patients du service (utilisant votre requête)
        personnel_service['patients'] = conn.execute('''
            SELECT DISTINCT p.id, p.nom, p.prenom 
            FROM patient p
            JOIN visite_medicale vm ON p.id = vm.patient_id
            JOIN medecin m ON vm.medecin_id = m.id
            JOIN service s ON m.service_id = s.id
            WHERE s.id = ?
        ''', (service_id,)).fetchall()

    conn.close()

    return render_template('medecin/services.html', 
                         services=services,
                         personnel_service=personnel_service)



@app.route('/infirmier')
def infirmier():
    if 'user' not in session or session.get('user_type') != 'infirmier':
        return redirect(url_for('login'))
    
    # Récupérer les soins assignés à cet infirmier
    conn = get_db_connection()
    soins = conn.execute('''
        SELECT s.*, p.nom, p.prenom 
        FROM soin s
        JOIN patient p ON s.patient_id = p.id
        WHERE s.infirmier_id = ?
        ORDER BY s.date_soin DESC
    ''', (session['user'],)).fetchall()
    conn.close()
    
    return render_template('infirmier/infirmier.html', soins=soins)

@app.route('/infirmier/soins')  
def mes_soins():
    if 'user' not in session or session.get('user_type') != 'infirmier':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    # Requête avec jointure pour récupérer les médicaments
    soins_data = conn.execute('''
        SELECT s.id, s.date_soin, s.heure_soin, s.description,
               p.id as patient_id, p.nom as patient_nom, p.prenom as patient_prenom,
               m.nom as medicament_nom, ms.quantite
        FROM soin s
        JOIN patient p ON s.patient_id = p.id
        LEFT JOIN medicament_soin ms ON s.id = ms.soin_id
        LEFT JOIN medicament m ON ms.medicament_id = m.id
        WHERE s.infirmier_id = ?
        ORDER BY s.date_soin DESC, s.heure_soin DESC
    ''', (session['user'],)).fetchall()
    conn.close()

    # Grouper les médicaments par soin
    soins_groupes = {}
    for row in soins_data:
        soin_id = row['id']
        if soin_id not in soins_groupes:
            soins_groupes[soin_id] = {
                'id': soin_id,
                'date_soin': row['date_soin'],
                'heure_soin': row['heure_soin'],
                'description': row['description'],
                'patient_nom': row['patient_nom'],
                'patient_prenom': row['patient_prenom'],
                'medicaments': []
            }
        if row['medicament_nom']:  # Si un médicament est associé
            soins_groupes[soin_id]['medicaments'].append({
                'nom': row['medicament_nom'],
                'quantite': row['quantite']
            })

    return render_template('infirmier/soins.html', soins=list(soins_groupes.values()))

@app.route('/infirmier/reunions')
def infirmier_reunions():
    if 'user' not in session or session.get('user_type') != 'infirmier':
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Récupérer les réunions de l'infirmier
    reunions = conn.execute('''
        SELECT DISTINCT r.id, r.date_reunion, r.heure_reunion
        FROM soin s
        JOIN reunion r ON s.reunion_id = r.id
        WHERE s.infirmier_id = ? AND s.reunion_id IS NOT NULL
        ORDER BY r.date_reunion DESC, r.heure_reunion DESC
    ''', (session['user'],)).fetchall()

    # Pour chaque réunion, récupérer les participants
    enriched_reunions = []
    for reunion in reunions:
        participants = conn.execute('''
            SELECT p.nom, p.prenom
            FROM participants_reunion pr
            JOIN personnel p ON p.id = pr.personnel_id
            WHERE pr.reunion_id = ?
        ''', (reunion['id'],)).fetchall()

        reunion_dict = dict(reunion)
        reunion_dict['participants'] = participants
        enriched_reunions.append(reunion_dict)

    conn.close()
    return render_template('infirmier/reunions.html', reunions=enriched_reunions)



# Fonction pour récupérer les patients d'un infirmier
def get_patients_for_infirmier(infirmier_id):
    conn = sqlite3.connect("../../bdd/hopital.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.nom, p.prenom, p.date_naissance, p.sexe, p.adresse, p.telephone, p.antecedents, p.raison_hospitalisation
        FROM patient p
        JOIN soin s ON p.id = s.patient_id
        WHERE s.infirmier_id = ?
    ''', (infirmier_id,))
    columns = [desc[0] for desc in cursor.description]
    patients = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return patients



@app.route('/infirmier/patients')
def mes_patients():
    infirmier_id = session.get('infirmier_id')  # Assurez-vous que l'ID de l'infirmier est dans la session
    print("Infirmier connecté:", infirmier_id)  # Débogage pour afficher l'infirmier connecté
    if not infirmier_id:
        flash("Veuillez vous connecter en tant qu'infirmier", 'error')  # Affichage d'un message flash
        return redirect(url_for('login'))  # Redirection vers la page de connexion si l'infirmier n'est pas connecté
    
    patients = get_patients_for_infirmier(infirmier_id)
    print("Patients trouvés:", patients)  # Affiche les patients récupérés
    return render_template('infirmier/patients.html', patients=patients)









   
@app.route('/infirmier/patient/<int:patient_id>/soins')
def historique_soins_patient(patient_id):
    infirmier_id = session.get('infirmier_id')
    if not infirmier_id:
        flash("Veuillez vous connecter.", "error")
        return redirect(url_for('login'))
    
    # Récupérer les soins de ce patient pour cet infirmier spécifique
    soins = get_soins_for_patient_and_infirmier(patient_id, infirmier_id)
    
    # Retourner les soins sous forme de JSON
    return jsonify(soins)

def get_soins_for_patient_and_infirmier(patient_id, infirmier_id):
    conn = sqlite3.connect("../../bdd/hopital.db") 
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date_soin, heure_soin, description
        FROM soin
        WHERE patient_id = ? AND infirmier_id = ?
        ORDER BY date_soin DESC, heure_soin DESC
    ''', (patient_id, infirmier_id))
    soins = cursor.fetchall()
    conn.close()

    # Retourner les soins sous forme de liste de dictionnaires
    return [{'date_soin': soin[0], 'heure_soin': soin[1], 'description': soin[2]} for soin in soins]


@app.route('/reunion/<int:reunion_id>/participants')
def participants_reunion(reunion_id):
    conn = get_db_connection()
    participants = conn.execute('''
        SELECT p.id, p.nom, p.prenom, p.type
        FROM participants_reunion pr
        JOIN personnel p ON pr.personnel_id = p.id
        WHERE pr.reunion_id = ?
    ''', (reunion_id,)).fetchall()
    conn.close()

    # Retourner en JSON
    return jsonify([dict(row) for row in participants])



    
if __name__ == '__main__':
    app.run(debug=True)