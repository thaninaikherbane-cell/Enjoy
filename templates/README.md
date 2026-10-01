# Enjoy!

Plateforme web de livraison de repas à domicile, réalisée en binôme dans le cadre du projet de Bases de données de L2 Informatique à l'Université Gustave Eiffel (2025/2026).

Enjoy! met en relation **des clients**, **des restaurants partenaires** et **des livreurs**.

## Fonctionnalités

### Côté client
- Inscription et connexion (mots de passe chiffrés avec bcrypt)
- Recherche de restaurants par nom, mot-clé (spécialité), note minimale ou nombre d'avis
- Panier et validation de commande
- Historique des commandes dans le profil : annulation d'une commande en attente, notation après livraison
- Parrainage d'un ami par email et points de fidélité

### Côté livreur
- Inscription et connexion avec numéro professionnel
- Choix du statut : `hors_service`, `en_attente`, `en_course`
- Choix des villes couvertes
- Consultation et prise en charge des commandes en attente

### Pour tous
- Liste des restaurants disponibles et leurs informations
- Page publique des commentaires vérifiés (avis liés à une commande réelle)

## Technologies

- **Back-end :** Python, Flask
- **Base de données :** PostgreSQL, psycopg2
- **Sécurité :** bcrypt (hashage des mots de passe), sessions Flask
- **Front-end :** HTML, CSS

## Points techniques

- **Modélisation normalisée :** tables séparées pour les codes postaux, villes et adresses ; une carte peut être partagée par plusieurs restaurants d'une même chaîne.
- **Contraintes en base :** `CHECK` sur les prix, les notes et les statuts ; `UNIQUE` sur l'email, le numéro professionnel et le numéro de carte.
- **Recherche de restaurants :** une seule requête combine jointures, moyenne des notes (`LEFT JOIN` + `COALESCE`), filtres dynamiques (`ILIKE`, `HAVING`) et une sous-requête `EXISTS` pour n'afficher que les restaurants ouverts et desservis par au moins un livreur dans la ville du client.
- **Commandes :** une commande sans livreur affecté (`matricule IS NULL`) est en attente ; la prise en charge ne peut se faire qu'une fois.
- **Vues SQL :** relevé hebdomadaire, spécialités des restaurants, commentaires vérifiés.

## Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/thaninaikherbane-cell/Enjoy.git
   cd Enjoy
   ```

2. Installer les dépendances :
   ```bash
   pip install flask psycopg2-binary bcrypt
   ```

3. Créer la base PostgreSQL `enjoy_db` et y importer le schéma et les données.

4. Lancer l'application :
   ```bash
   python main.py
   ```

### Identifiants de test
- **Client :** `jean.dupont@mail.com` / `mdp1`
- **Livreur :** `0601010101` / `mdp101`

## Répartition du travail

**Thanina Ikherbane**
- Conception du schéma entité-association et du modèle relationnel
- Création des vues SQL
- Pages profil client et livreur, recherche, commentaires vérifiés
- Gestion des commandes et des livraisons
- Parrainage et points de fidélité
- Design CSS

**Mellina Mammeri**
- Optimisation du modèle de données
- Pages connexion, inscription, restaurants et panier
- Authentification avec bcrypt
- Tests et débogage

## Pistes d'amélioration

- Mieux structurer le code (découpage en modules / Blueprints Flask)
- Ajouter des tests automatisés
- Paiement en ligne et suivi des livraisons en temps réel
- Notation des livreurs
- Interface adaptée au mobile
- Gestion RGPD complète (export des données, droit à l'oubli)
