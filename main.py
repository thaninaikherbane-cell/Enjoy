import psycopg2
import db
import bcrypt
from  flask import Flask, render_template, request, redirect, url_for, session,flash

app=Flask(__name__)

app.secret_key = b'235f43e36aac09c471a896862b810846670bc0127a74e1936d8ef0f1ca389e3e'

@app.route("/accueil")
def accueil():
    return render_template("accueil.html")


@app.route("/connexion", methods=['GET', 'POST'])
def connexion():
    if "prenom" in session:
        return redirect(url_for('accueil'))
        
    return render_template("connexion.html")

@app.route("/check", methods=["POST"])
def check():
    mail = request.form.get("email")
    mdp = request.form.get("password")

    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT prenom, id_client, adresse_mail, mdp FROM client WHERE adresse_mail=%s',
                (mail,)
            )
            resultat = cur.fetchone()
            if resultat:
                hashed = resultat.mdp  # hash stocké en texte
                if bcrypt.checkpw(mdp.encode('utf-8'), hashed.encode('utf-8')):
                    session["prenom"] = resultat.prenom
                    session["id_client"] = resultat.id_client
                    return redirect(url_for('accueil'))
    return redirect(url_for('connexion'))


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if "id_client" in session:  # Vérifier si le client est déjà connecté
        return redirect(url_for("accueil"))
    
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        mail = request.form.get("mail")
        mdp = request.form.get("mdp")
        
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Vérifier si l'email existe déjà
                cur.execute("SELECT id_client FROM client WHERE adresse_mail=%s", (mail,))
                if cur.fetchone():  
                    flash("Cet email existe déjà", "error")
                    return redirect(url_for("inscription"))
                
                # Hash du mot de passe
                hashed = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Insérer et récupérer l'id_client généré
                cur.execute("""
                    INSERT INTO client(nom, prenom, adresse_mail, mdp)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_client
                """, (nom, prenom, mail, hashed))
                result = cur.fetchone()
                
                if result:
                    id_client = result[0]
                    conn.commit()
                    
                    # Créer la session du client
                    session["id_client"] = id_client
                    session["adresse_mail"] = mail
                    session["prenom"] = prenom
                    session["nom"] = nom
                    
                    return redirect(url_for("accueil"))
    
    return render_template("inscription.html")

@app.route("/connexionprive")
def connexionprive():
    if "prenom" in session:
        return redirect(url_for('profilprofessionnel')) 
        
    return render_template("connexionprive.html")

@app.route("/checkprive", methods=["POST"])
def checkprive():
    num_pro = request.form.get("numPro")
    mdp = request.form.get("password")

    with db.connect() as conn: 
        with conn.cursor() as cur: 
            cur.execute('SELECT matricule, prenom, mdp, numPro FROM livreur WHERE numPro=%s', (num_pro,))
            
            resultat = cur.fetchone()
            
            if resultat:
                hashed = resultat.mdp  
                if bcrypt.checkpw(mdp.encode('utf-8'), hashed.encode('utf-8')):
                    session["prenom"] = resultat.prenom
                    session["matricule"] = resultat.matricule
                    session["role"] = "livreur"
                    return redirect(url_for('accueil'))
    return redirect(url_for("connexionprive"))

@app.route("/inscriptionLivreur", methods=["GET", "POST"])
def inscriptionLivreur():
    if "matricule" in session:  # Vérifier avec 'matricule' pour cohérence
        return redirect(url_for("accueil"))
    
    if request.method == "POST":
        prenom = request.form.get("prenom")
        nom = request.form.get("nom")
        numpro = request.form.get("numpro")
        mdp = request.form.get("password")
        
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Vérifier si le numPro existe déjà
                cur.execute("SELECT matricule FROM livreur WHERE numPro=%s", (numpro,))
                if cur.fetchone():  
                    flash("Ce numéro professionnel existe déjà", "error")
                    return redirect(url_for("inscriptionLivreur"))
                
                # Hash du mot de passe
                hashed = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Insérer et récupérer le matricule généré
                cur.execute("""
                    INSERT INTO livreur(prenom, nom, numPro, mdp)
                    VALUES (%s, %s, %s, %s)
                    RETURNING matricule
                """, (prenom, nom, numpro, hashed))
                result = cur.fetchone()
                
                if result:
                    matricule = result[0]
                    conn.commit()
                    
                    # Créer la session du livreur
                    session["matricule"] = matricule
                    session["numPro"] = numpro
                    session["prenom"] = prenom
                    session["nom"] = nom
                    
                    return redirect(url_for("accueil"))
        
       
    
    return render_template("inscriptionLivreur.html")


@app.route("/pagederestaurant")
def pagederestaurant():
    with db.connect() as conn: 
        with conn.cursor() as cur: 
            sql = """
                SELECT r.id_restaurant,
                    r.nom,
                    r.horaire_ouverture,
                    r.frais_livraison, 
                    a.numRue,
                    a.nomRue,
                    v.nom AS nom_ville
                FROM restaurant r
                JOIN adresse a ON r.id_adresse = a.id_adresse
                JOIN ville v ON a.id_ville = v.id_ville
                ORDER BY r.nom
            """

            cur.execute(sql)
            restaurants = cur.fetchall()
            
    return render_template("pagederestaurant.html", restaurants=restaurants)


@app.route("/restaurant/<int:id_restaurant>")
def restaurant_detail(id_restaurant):
    with db.connect() as conn:
        with conn.cursor() as cur:

            # Infos du restaurant
            cur.execute("""
                SELECT r.nom,
                       r.horaire_ouverture,
                       r.frais_livraison,
                       a.numRue,
                       a.nomRue,
                       v.nom AS ville
                FROM restaurant r
                JOIN adresse a ON r.id_adresse = a.id_adresse
                JOIN ville v ON a.id_ville = v.id_ville
                WHERE r.id_restaurant = %s
            """, (id_restaurant,))
            restaurant = cur.fetchone()

            # Plats du restaurant
            cur.execute("""
                SELECT p.id_plat, p.nom, p.prix, p.description
                FROM plat p
                JOIN affichage af ON p.id_plat = af.id_plat
                JOIN restaurant r ON r.id_carte = af.id_carte
                WHERE r.id_restaurant = %s
            """, (id_restaurant,))
            plats = cur.fetchall()

            # Avis
            cur.execute("""
                SELECT c.commentaire, c.note, cl.prenom
                FROM commentaire c
                JOIN client cl ON c.id_client = cl.id_client
                WHERE c.id_restaurant = %s
            """, (id_restaurant,))
            avis = cur.fetchall()

    return render_template(
        "restaurant.html",
        restaurant=restaurant,
        plats=plats,
        avis=avis,
        id_resto=id_restaurant
    )


@app.route('/ajout_panier/<id_resto>', methods=["POST"])
def ajout_panier(id_resto):
    with db.connect() as conn:
        
        with conn.cursor() as cur:
            id_resto_int = int(id_resto)
            

            cur.execute("SELECT frais_livraison FROM restaurant WHERE id_restaurant = %s", (id_resto_int,))
            resto = cur.fetchone()
            
            
            cur.execute("""
                SELECT p.id_plat, p.nom, p.prix, p.photo 
                FROM plat p
                JOIN affichage a ON p.id_plat = a.id_plat
                JOIN restaurant r ON a.id_carte = r.id_carte
                WHERE r.id_restaurant = %s
            """, (id_resto_int,))
            plats = cur.fetchall()
            
           
            if "panier" in session and "prix_total" in session and "frais" in session:
                panier_dict = session["panier"]
                prix_total = float(session["prix_total"])
                frais = float(session["frais"])
                
             
                if panier_dict and len(panier_dict) > 0:
                    for plat_panier in panier_dict.values():
                        if plat_panier["id_resto"] != id_resto_int:
                           
                            panier_dict = {}
                            prix_total = 0
                            frais = 0
                        break
            else:
                panier_dict = {}
                prix_total = 0
                frais = 0
            
         
            for plat in plats:
                quantite_str = request.form.get(f"quantite_plat_{plat.id_plat}")
                if quantite_str:
                    quantite = int(quantite_str)
                    if quantite > 0:
                        prix_quantite = float(plat.prix) * quantite
                        
                        if str(plat.id_plat) in panier_dict:
                            
                            panier_dict[str(plat.id_plat)]["prix_quantite"] = float(panier_dict[str(plat.id_plat)]["prix_quantite"]) + prix_quantite
                            panier_dict[str(plat.id_plat)]["quantite"] = int(panier_dict[str(plat.id_plat)]["quantite"]) + quantite
                        else:
                           
                            panier_dict[str(plat.id_plat)] = {
                                "id_plat": plat.id_plat,
                                "id_resto": id_resto_int,
                                "quantite": quantite,
                                "photo": plat.photo,  
                                "prix": float(plat.prix),
                                "nom": plat.nom,
                                "prix_quantite": prix_quantite
                            }
                        
                        prix_total += prix_quantite
              
            if panier_dict:
                session["id_resto_panier"] = id_resto_int
                frais = float(resto.frais_livraison)
            
           
            session["panier"] = panier_dict
            session["prix_panier"] = prix_total
            session["frais"] = frais
            
    return redirect(url_for("Le_panier"))



@app.route('/Le_panier')
def Le_panier():
    if "panier" not in session:
        session["panier"] = {}
        session["prix_panier"] = 0
        session["frais"]=0

    prix_panier = float(session["prix_panier"])
    frais=float(session["frais"])
    return render_template("panier.html", panier=session["panier"], prix_total=prix_panier,frais=frais)


          
@app.route("/confirmer_commande", methods=["POST"])
def confirmer_commande():
    
    if "panier" in session and session.get('id_client'):
        with db.connect() as conn: 
            with conn.cursor() as cur:
                cur.execute("SELECT max(Numcommande) FROM commande")
                num_commande = cur.fetchone()[0]+1
                
                cur.execute("""
                    INSERT INTO commande(numCommande,id_restaurant, id_client, matricule, date_commande) 
                    VALUES (%s,%s, %s, NULL, CURRENT_TIMESTAMP) 
                    RETURNING numCommande
                """, (num_commande,int(session["id_resto_panier"]), int(session["id_client"])))
                 
                
             
                for plat in session["panier"]:
                    id_plat = int(plat)
                    quantite = int(session["panier"][plat]["quantite"])
                    
                    cur.execute("""
                        INSERT INTO contient(numCommande, id_plat, quantite) 
                        VALUES (%s, %s, %s)
                    """, (num_commande, id_plat, quantite))
                
                
                montant_total = float(session["prix_panier"]) + float(session.get("frais", 0))
                point_parraine = (montant_total / 10) * 50
                
                cur.execute("""
                    UPDATE client 
                    SET point_fidelite = point_fidelite + %s 
                    WHERE id_client = %s
                """, (point_parraine, int(session["id_client"])))
                
              
                if "parrain" in session and session["parrain"]:
                    cur.execute("""
                        UPDATE client 
                        SET point_fidelite = point_fidelite + %s 
                        WHERE id_client = %s
                    """, (point_parraine, int(session["parrain"])))
                
        
                session.pop("panier", None)
                session.pop("prix_total", None)
                session.pop("id_resto_panier", None)
                session.pop("frais", None)
    
    
    return redirect(url_for("profilpersonnel"))


@app.route("/recherche")
def recherche():

    if "id_client" not in session:
        return redirect(url_for("connexion"))  

    id_client = session["id_client"]
    
    nom = request.args.get("nom")
    motcle = request.args.get("motcle")
    note_min = request.args.get("note_min")
    avis_min = request.args.get("avis_min")

   
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            
            query = """ SELECT r.id_restaurant,
            r.nom,
            r.horaire_ouverture,          -- ajouter cette colonne
            COALESCE(AVG(cm.note), 0) AS moyenne,
            COUNT(cm.note) AS nb_avis
            FROM restaurant r
            JOIN client c ON c.id_client = %s
            LEFT JOIN commentaire cm ON cm.id_restaurant = r.id_restaurant
            LEFT JOIN decrit d ON d.id_restaurant = r.id_restaurant
            WHERE (r.ferm_excep IS NULL OR r.ferm_excep != CURRENT_DATE)
            AND EXISTS(
            SELECT 1
            FROM couvre cv
            JOIN livreur l ON l.matricule = cv.matricule
            WHERE cv.id_ville = c.id_ville)
            """
            params = [id_client]
            
            if nom:
                query += " AND r.nom ILIKE %s"
                params.append(f"%{nom}%")
            if motcle:
                query += " AND d.nom ILIKE %s"
                params.append(f"%{motcle}%")
            
            query += " GROUP BY r.id_restaurant, r.nom"
            
            # Filtres sur agrégats (HAVING)
            having_clauses = []
            if note_min:
                having_clauses.append("AVG(cm.note) >= %s")
                params.append(float(note_min))
            if avis_min:
                having_clauses.append("COUNT(cm.note) >= %s")
                params.append(int(avis_min))
            
            if having_clauses:
                query += " HAVING " + " AND ".join(having_clauses)
            
            query += " ORDER BY moyenne DESC, nb_avis DESC"
            
            cur.execute(query, params)
            restos = cur.fetchall()
    
    return render_template("recherche.html", restaurants=restos)



@app.route("/profilpersonnel")
def profilpersonnel():

    id_client = session.get("id_client")
    if id_client is None:
         return redirect("/connexion")

    with db.connect() as conn:
        with conn.cursor() as cur:

            # Historique commandes avec statut
            cur.execute("""
                SELECT c.numCommande,
                       c.date_commande,
                       r.nom,
                       CASE 
                           WHEN c.matricule IS NULL THEN 'en_attente'
                           ELSE 'finalisee'
                       END AS statut,
                       SUM(ct.quantite * p.prix) AS total
                FROM commande c
                JOIN restaurant r ON c.id_restaurant = r.id_restaurant
                JOIN contient ct ON c.numCommande = ct.numCommande
                JOIN plat p ON ct.id_plat = p.id_plat
                WHERE c.id_client = %s
                GROUP BY c.numCommande, c.date_commande, r.nom, statut
                ORDER BY c.date_commande DESC
            """, (id_client,))
            commandes = cur.fetchall()

            # Points de fidélité
            cur.execute("SELECT point_fidelite FROM client WHERE id_client=%s", (id_client,))
            points = cur.fetchone()[0]

    return render_template("profilpersonnel.html", commandes=commandes, points=points)


@app.route("/annuler_commande", methods=["POST"])
def annuler_commande():
    numCommande = request.form.get("numCommande")
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM commande WHERE numCommande=%s AND matricule IS NULL", (numCommande,))
    return redirect("/profilpersonnel")

@app.route("/noter_commande", methods=["POST"])
def noter_commande():
    numCommande = request.form.get("numCommande")
    note = request.form.get("note")
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Récupérer id_restaurant
            cur.execute("SELECT id_restaurant FROM commande WHERE numCommande=%s", (numCommande,))
            id_restaurant = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO commentaire(id_client, id_restaurant, note)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_client,id_restaurant) DO UPDATE
                SET note = EXCLUDED.note
            """, (1, id_restaurant, note))  # id_client à remplacer après connexion
    return redirect("/profilpersonnel")

@app.route("/parrainer", methods=["POST"])
def parrainer():
    # Vérifier que l'utilisateur est connecté
    if "id_client" not in session:
        flash("Vous devez être connecté pour parrainer", "error")
        return redirect(url_for("connexion"))
    
    email = request.form.get("email")
    
    # Vérifier que l'email est fourni
    if not email:
        flash("Veuillez entrer un email", "error")
        return redirect(request.referrer or url_for("accueil"))
    
    id_parrain = session["id_client"]
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Vérifier que cet email n'existe pas déjà dans les clients
            cur.execute("SELECT id_client FROM client WHERE adresse_mail = %s", (email,))
            if cur.fetchone():
                flash("Erreur : cette personne est déjà inscrite sur le site !", "error")
                return redirect(request.referrer or url_for("accueil"))
            
            # Vérifier que je ne parraine pas mon propre email
            cur.execute("SELECT adresse_mail FROM client WHERE id_client = %s", (id_parrain,))
            result = cur.fetchone()
            if result and result[0] == email:
                flash("Erreur : vous ne pouvez pas parrainer votre propre email !", "error")
                return redirect(request.referrer or url_for("accueil"))
            
           
            cur.execute("""
                UPDATE client 
                SET point_fidelite = point_fidelite + 10 
                WHERE id_client = %s
            """, (id_parrain,))
            
            conn.commit()
    
    flash(f"Parrainage enregistré ! Vous avez gagné 10 points. Quand {email} s'inscrira, il sera automatiquement votre filleul 🎉")
    return redirect(request.referrer or url_for("accueil"))




@app.route("/profilprofessionnel")
def profilprofessionnel():
    matricule = session.get("matricule")
    if matricule is None:
        return redirect("/connexionprive")
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Commandes en attente dans les villes qu'il couvre
            cur.execute("""

                SELECT c.numCommande, c.date_commande, r.nom AS restaurant, v.nom AS ville
                FROM commande c
                JOIN restaurant r ON c.id_restaurant = r.id_restaurant
                JOIN adresse a ON r.id_adresse = a.id_adresse
                JOIN ville v ON a.id_ville = v.id_ville
                LEFT JOIN livreur l ON c.matricule = l.matricule
                WHERE c.matricule IS NULL  -- commande non prise
                AND v.id_ville IN (
                SELECT id_ville FROM couvre WHERE matricule=%s
                )
                ORDER BY c.date_commande;
                """, (matricule,))
            commandes = cur.fetchall()
            
            # Statut du livreur
            cur.execute("SELECT status FROM livreur WHERE matricule=%s", (matricule,))
            status = cur.fetchone()[0]
            
            # Villes disponibles pour couverture
            cur.execute("SELECT id_ville, nom FROM ville")
            villes = cur.fetchall()
            
            # Villes actuellement couvertes
            cur.execute("SELECT id_ville FROM couvre WHERE matricule=%s", (matricule,))
            villes_couvertes = [v[0] for v in cur.fetchall()]
    
    return render_template(
        "profilprofessionnel.html",
        commandes=commandes,
        status=status,
        villes=villes,
        villes_couvertes=villes_couvertes
    )

@app.route("/prendre_commande", methods=["POST"])
def prendre_commande():
    matricule = session.get("matricule")
    if matricule is None:
        flash("Vous devez être connecté", "error")
        return redirect("/connexionprive")
    
    numCommande = request.form.get("numCommande")
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Vérifier que la commande est en attente (matricule NULL)
            cur.execute("""
                SELECT matricule
                FROM commande
                WHERE numCommande=%s
            """, (numCommande,))
            result = cur.fetchone()
            
            if result and result[0] is None:
                # Assigner le livreur et mettre la date de livraison
                cur.execute("""
                    UPDATE commande
                    SET matricule=%s, date_livraison=NOW()
                    WHERE numCommande=%s
                """, (matricule, numCommande))
                conn.commit()
                flash(f"Commande {numCommande} prise en charge !", "success")
            else:
                flash("Cette commande n'est plus disponible.", "error")
    
    return redirect("/profilprofessionnel")



@app.route("/changer_statut", methods=["POST"])
def changer_statut():
    matricule = session.get("matricule")
    if matricule is None:
        flash("Vous devez être connecté", "error")
        return redirect("/connexionprive")
    
    nouveau_statut = request.form.get("statut")
    
    if nouveau_statut not in ['hors_service', 'en_attente', 'en_course']:
        flash("Statut invalide", "error")
        return redirect("/profilprofessionnel")
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Changer le statut
            cur.execute("""
                UPDATE livreur 
                SET status=%s 
                WHERE matricule=%s
            """, (nouveau_statut, matricule))
            conn.commit()
            flash(f"Statut changé en '{nouveau_statut}' avec succès", "success")
    
    return redirect("/profilprofessionnel")

@app.route("/mettre_couverture", methods=["POST"])
def mettre_couverture():
    matricule = session.get("matricule")
    if matricule is None:
        flash("Vous devez être connecté", "error")
        return redirect("/connexionprive")
    
    villes_choisies = request.form.getlist("villes")
    
    with db.connect() as conn:
        with conn.cursor() as cur:
            # Supprimer toutes les villes actuelles
            cur.execute("DELETE FROM couvre WHERE matricule=%s", (matricule,))
            
            # Ajouter les nouvelles villes
            for id_ville in villes_choisies:
                cur.execute("""
                    INSERT INTO couvre (matricule, id_ville) 
                    VALUES (%s, %s)
                """, (matricule, int(id_ville)))
            
            conn.commit()
            flash("Villes mises à jour avec succès !", "success")
    
    return redirect("/profilprofessionnel")


@app.route("/commentaire_verifie")
def commentaire_verifie():
    with db.connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM commentaire_verifie ORDER BY id_client, id_restaurant")
            commentaires = cur.fetchall()
    
    return render_template("commentaire_verifie.html", commentaires=commentaires)


@app.route("/deconnexion")
def deconnexion():
    session.clear()  # Supprime toutes les variables de session
    return redirect(url_for("accueil"))

if __name__=='__main__':
    app.run()

    
