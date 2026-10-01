
-- =============================================
-- NETTOYAGE (DROP TABLES)
-- =============================================
DROP TABLE IF EXISTS commentaire CASCADE;
DROP TABLE IF EXISTS contient CASCADE;
DROP TABLE IF EXISTS commande CASCADE;
DROP TABLE IF EXISTS carte_bancaire CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS couvre CASCADE;
DROP TABLE IF EXISTS livreur CASCADE;
DROP TABLE IF EXISTS decrit CASCADE;
DROP TABLE IF EXISTS mot_clef CASCADE;
DROP TABLE IF EXISTS restaurant CASCADE;
DROP TABLE IF EXISTS adresse CASCADE;
DROP TABLE IF EXISTS ville CASCADE;
DROP TABLE IF EXISTS codePostal CASCADE;
DROP TABLE IF EXISTS affichage CASCADE;
DROP TABLE IF EXISTS carte CASCADE;
DROP TABLE IF EXISTS plat CASCADE;


CREATE TABLE plat(
    id_plat int PRIMARY KEY ,
    nom varchar(50) NOT NULL,
    prix NUMERIC(6,2) NOT NULL CHECK (prix>0),
    description text,
    photo bytea
);

CREATE TABLE carte(
    id_carte int PRIMARY KEY
);

CREATE TABLE affichage(
    id_carte int references carte(id_carte) ON DELETE CASCADE ON UPDATE CASCADE,
    id_plat int references plat(id_plat) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(id_carte,id_plat)
);

CREATE TABLE codePostal(
    CP char(5) PRIMARY KEY
);

CREATE TABLE ville(
    id_ville serial PRIMARY KEY,
    nom varchar(50) NOT NULL ,
    CP char(5) references codePostal(CP) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE adresse(
    id_adresse int PRIMARY KEY,
    nomRue varchar(100),
    numRue varchar(10) NOT NULL,
    id_ville int references ville(id_ville) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE  TABLE restaurant(
    id_restaurant int PRIMARY KEY,
    nom varchar(100) NOT NULL,
    horaire_ouverture varchar(20) NOT NULL, 
    ferm_excep date,
    frais_livraison NUMERIC(5,2) NOT NULL CHECK (frais_livraison>=0),
    id_carte int references carte(id_carte) ON DELETE SET NULL ON UPDATE CASCADE,
    id_adresse int references adresse(id_adresse) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE mot_clef(
    nom varchar(25) PRIMARY KEY
);

CREATE TABLE decrit(
    id_restaurant int references restaurant(id_restaurant) ON DELETE CASCADE ON UPDATE CASCADE,
    nom varchar(25) references mot_clef(nom) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (id_restaurant,nom)
);

CREATE TABLE livreur(
    matricule serial PRIMARY KEY,
    nom varchar(50) NOT NULL,
    prenom varchar(50) NOT NULL,
    numPro varchar(20) NOT NULL UNIQUE,
    mdp varchar(225) NOT NULL,
    status varchar(30) NOT NULL DEFAULT 'hors_service' 
    CHECK (status IN ('hors_service', 'en_attente', 'en_course'))
);

CREATE TABLE couvre(
    matricule int references livreur(matricule) ON DELETE CASCADE ON UPDATE CASCADE,
    id_ville int references ville(id_ville) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (matricule,id_ville)
);

CREATE TABLE client(
    id_client serial PRIMARY KEY,
    nom varchar(50) NOT NULL,
    prenom varchar(50) NOT NULL,
    adresse_mail varchar(100) UNIQUE NOT NULL,
    numTel varchar(20) UNIQUE,
    mdp varchar(255) NOT NULL,
    point_fidelite int default 0 CHECK (point_fidelite >= 0),
    id_clientParraine int references client(id_client) ON DELETE SET NULL ON UPDATE CASCADE,
    id_ville int references ville(id_ville) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE carte_bancaire(
    id_carteB serial PRIMARY KEY,
    numCarte varchar(19) UNIQUE NOT NULL,
    typeCarte varchar(20) NOT NULL,
    date_expiration date NOT NULL,
    code_securite char(3) NOT NULL,
    id_client int references client (id_client) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (date_expiration > CURRENT_DATE) 
);

CREATE TABLE commande(
    numCommande int PRIMARY KEY,
    id_restaurant int REFERENCES restaurant(id_restaurant) ON DELETE CASCADE ON UPDATE CASCADE,
    id_client int REFERENCES client(id_client)  ON DELETE CASCADE ON UPDATE CASCADE,
    matricule int REFERENCES livreur(matricule) ON DELETE SET NULL ON UPDATE CASCADE,
    date_commande TIMESTAMP NOT NULL,  -- date/heure quand le client passe la commande
    date_livraison TIMESTAMP          -- date/heure quand le livreur prend en charge la commande
);

CREATE TABLE contient(
    numCommande int references commande(numCommande)  ON DELETE CASCADE ON UPDATE CASCADE,
    id_plat int references plat(id_plat) ON DELETE CASCADE ON UPDATE CASCADE,
    quantite int NOT NULL CHECK (quantite > 0) ,
    PRIMARY KEY (numCommande,id_plat)
);

CREATE TABLE commentaire(
    id_client int references client(id_client) ON DELETE CASCADE ON UPDATE CASCADE,
    id_restaurant int references restaurant(id_restaurant) ON DELETE CASCADE ON UPDATE CASCADE,
    commentaire text,
    note decimal(2,1) CHECK (note between 0 AND 5),
    PRIMARY KEY(id_client,id_restaurant)
);

-- Script d'insertion corrigé pour la base de données de livraison de repas

-- Insertion des données pour la table plat (IDs 1-10 supprimés, on garde 101-110)
INSERT INTO plat(id_plat, nom, prix, description) VALUES
(101, 'Pizza Margherita', 12.5, 'Pizza classique avec sauce tomate et mozzarella'),
(102, 'Burger Classique', 10.0, 'Burger avec steak, salade, tomate et fromage'),
(103, 'Sushi Saumon', 15.0, 'Sushi frais au saumon'),
(104, 'Salade César', 9.0, 'Salade avec poulet, croûtons et parmesan'),
(105, 'Tacos Poulet', 11.0, 'Tacos avec poulet, légumes et sauce'),
(106, 'Pâtes Carbonara', 13.0, 'Pâtes avec crème, lardons et parmesan'),
(107, 'Burger Végétarien', 11.0, 'Burger avec galette légumes et fromage'),
(108, 'Salade Niçoise', 10.5, 'Salade avec thon, œuf, olives et légumes'),
(109, 'Sushi Thon', 15.5, 'Sushi frais au thon'),
(110, 'Tacos Boeuf', 12.0, 'Tacos avec boeuf, légumes et sauce');

-- Insertion des données pour la table carte
INSERT INTO carte(id_carte) VALUES
(101), (102), (103);

-- Insertion des données pour la table affichage
INSERT INTO affichage(id_carte, id_plat) VALUES
(101, 101), (101, 102), (101, 106),
(102, 103), (102, 104), (102, 107), (102, 108),
(103, 105), (103, 109), (103, 110);

-- Insertion des données pour la table codePostal
INSERT INTO codePostal(CP) VALUES 
('75001'), ('75002'), ('69001'), ('13001'), ('31000');

-- Insertion des données pour la table ville
INSERT INTO ville(id_ville, nom, CP) VALUES
(101, 'Paris 1er', '75001'),
(102, 'Paris 2ème', '75002'),
(103, 'Lyon 1er', '69001'),
(104, 'Marseille 1er', '13001'),
(105, 'Toulouse', '31000');

-- Insertion des données pour la table adresse
INSERT INTO adresse(id_adresse, nomRue, numRue, id_ville) VALUES
(101, 'Rue de Rivoli', '123', 101),
(102, 'Boulevard Montmartre', '45bis', 102),
(103, 'Rue de la République', '7', 103),
(104, 'Canebière', '156', 104),
(105, 'Rue Saint-Rome', '22', 105);

-- Insertion des données pour la table restaurant
INSERT INTO restaurant(id_restaurant, nom, horaire_ouverture, ferm_excep, frais_livraison, id_carte, id_adresse) VALUES
(101, 'Le Gourmet', '10:00-22:00', NULL, 3.5, 101, 101),
(102, 'Burger House', '11:00-23:00', NULL, 2.0, 101, 102),
(103, 'Sushi World', '12:00-22:30', NULL, 4.0, 102, 103),
(104, 'Salade & Co', '09:00-20:00', NULL, 2.5, 102, 104),
(105, 'Tacos Express', '10:30-23:30', NULL, 3.0, 103, 105),
(106, 'Pasta & Co', '11:00-22:00', NULL, 3.5, 101, 102),
(107, 'Veggie Burger', '10:30-21:00', NULL, 2.5, 102, 103),
(108, 'Sushi Express', '12:00-22:30', NULL, 4.0, 102, 104);

-- Insertion des données pour la table mot_clef
INSERT INTO mot_clef(nom) VALUES
('Italien'), ('Pizza'), ('Burger'), ('Salade'), ('Tacos'), ('Pâtes'), ('Végétarien'), ('Sushi');

-- Insertion des données pour la table decrit
INSERT INTO decrit(id_restaurant, nom) VALUES
(101, 'Italien'), 
(101, 'Pizza'),
(102, 'Burger'), 
(103, 'Sushi'),
(104, 'Salade'),
(105, 'Tacos'), 
(106, 'Italien'),
(106, 'Pâtes'), 
(107, 'Végétarien'),
(107, 'Burger'),
(108, 'Sushi');

-- Insertion des données pour la table livreur
INSERT INTO livreur(matricule, nom, prenom, numPro, mdp, status) VALUES
(201, 'Martin', 'Paul', '0601010101', '$2b$12$rI2Wkgfs5lyc5hoE8PYnpeeA3xxH6B1UQhtSd7Bjla5orI7hcCTfC', 'en_attente'),
(202, 'Durand', 'Sophie', '0602020202', '$2b$12$TMzdoAJDlbu/Otr2uZS2neoyfsobIFjVmvAtgG.zZEwiHfPOfI4t6', 'en_course'),
(203, 'Bernard', 'Luc', '0603030303', '$2b$12$4qNTDaGzFbzDYUVZ3XapJucBP3M6MhZ2hoCT9H8608.HZe7ooJj6i', 'en_attente'),
(204, 'Petit', 'Lucie', '0604040404', '$2b$12$p1WY0EyOTwjPlbSCJd5nzO7twqdwJTnf2nf5AACCuP5SjK3SRljQ6', 'hors_service'),
(205, 'Roux', 'Hugo', '0605050505', '$2b$12$.j8SoE5X1sjoBPfAwQN/JO68rwv3dewcsWDRXILP2g9tVAjxfFUc.', 'en_course');

-- Insertion des données pour la table couvre
INSERT INTO couvre(matricule, id_ville) VALUES
(201, 101), (201, 102), 
(202, 103), 
(203, 104), (203, 105),
(204, 101), (204, 105), 
(205, 102), (205, 103);

-- Insertion des données pour la table client
INSERT INTO client(id_client, nom, prenom, adresse_mail, numTel, mdp, point_fidelite, id_clientParraine, id_ville) VALUES
(101, 'Dupont', 'Jean', 'jean.dupont@mail.com', '0606060606', '$2b$12$Vr1llvFC0h5xNb3sjtS6.eVHVApt9iKcobrNOgQA1k5Gfq8brArHi', 100, NULL, 101),
(102, 'Martin', 'Claire', 'claire.martin@mail.com', '0607070707', '$2b$12$9YvQMw7PpTlAQhmn53C1BekyiNQ6D9Ffupkg95AR4.JOaOXLNuc7S', 50, 101, 102),
(103, 'Leroy', 'Paul', 'paul.leroy@mail.com', '0608080808', '$2b$12$xMEqQjHJ.VGJYf2aqmSJReftVVw6oouWt7TtMgoY5omwDXV42YJJG', 70, NULL, 103),
(104, 'Bernard', 'Sophie', 'sophie.bernard@mail.com', '0609090909', '$2b$12$GdfDHfcSK/XjYu.avtGmrOliSzrVizlsflFVUfulkZA7o5bDkzZbC', 40, 101, 104),
(105, 'Legrand', 'Lucas', 'lucas.legrand@mail.com', '0610101010', '$2b$12$SvOKxfd/zU0jJnTwsy.cmeToOyK./ud4.bMLNOiiyqgOdLDZ.CuJ6', 30, 102, 105);

-- Insertion des données pour la table carte_bancaire
INSERT INTO carte_bancaire(id_carteB, numCarte, typeCarte, date_expiration, code_securite, id_client) VALUES
(101, '1234567890123456', 'Visa', '2026-12-31', '123', 101),
(102, '2345678901234567', 'MasterCard', '2026-08-31', '456', 102),
(103, '3456789012345678', 'Visa', '2026-05-31', '789', 104),
(104, '4567890123456789', 'MasterCard', '2025-12-31', '012', 105);

-- Insertion des données pour la table commande
INSERT INTO commande(numCommande, id_restaurant, id_client, matricule, date_commande, date_livraison) VALUES
(101, 101, 101, 201, '2025-11-10 12:30:00', '2025-11-10 12:50:00'),
(102, 102, 102, 202, '2025-11-10 13:00:00', '2025-11-10 13:20:00'),
(103, 103, 103, NULL, '2025-11-10 09:30:00', NULL),
(104, 106, 104, NULL, '2025-11-11 12:00:00', NULL),
(105, 107, 105, 205, '2025-11-11 12:30:00', '2025-11-11 12:50:00'),
(106, 108, 101, 201, '2025-11-11 13:00:00', '2025-11-11 13:20:00');

-- Insertion des données pour la table contient
INSERT INTO contient(numCommande, id_plat, quantite) VALUES
(101, 101, 2), (101, 102, 1),
(102, 102, 3),
(103, 103, 2), (103, 104, 1),
(104, 106, 2), (104, 101, 1),
(105, 107, 1), (105, 108, 2),
(106, 109, 3), (106, 110, 1);

-- Insertion des données pour la table commentaire
INSERT INTO commentaire(id_client, id_restaurant, commentaire, note) VALUES
(101, 101, 'Bonne cuisine mais le service était rapide', 3.5),
(102, 102, 'Repas correct mais manque de variété', 3.0),
(103, 103, 'Sushi frais avec portions grandes', 4.0),
(102, 101, 'Restaurant agréable', 3.8),
(103, 102, 'Livraison rapide mais burger trop sec', 3.2),
(104, 106, 'Délicieux et service rapide', 4.5),
(105, 107, 'Très bon', 4.0),
(101, 108, 'Sushi frais et bien présenté', 5.0);


--Creation la vue commentaire_verifie :
CREATE VIEW commentaire_verifie AS
SELECT DISTINCT ON (com.id_client, com.id_restaurant)
    com.id_client || ',' || com.id_restaurant AS id_commentaire,
    com.note,
    com.commentaire,
    com.id_client,
    com.id_restaurant,
    v.nom AS ville,
    co.numCommande,
    co.total_prix AS prix,
    co.date_livraison - co.date_commande AS duree_commande
FROM commentaire com
LEFT JOIN (
    SELECT co.numCommande, co.id_client, co.id_restaurant, co.date_commande, co.date_livraison,
           SUM(ct.quantite * p.prix) AS total_prix
    FROM commande co
    LEFT JOIN contient ct ON co.numCommande = ct.numCommande
    LEFT JOIN plat p ON ct.id_plat = p.id_plat
    GROUP BY co.numCommande, co.id_client, co.id_restaurant, co.date_commande, co.date_livraison
) co ON com.id_client = co.id_client AND com.id_restaurant = co.id_restaurant
JOIN client cl ON com.id_client = cl.id_client
JOIN ville v ON cl.id_ville = v.id_ville;


