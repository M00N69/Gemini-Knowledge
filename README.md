#  Streamlit with google drive knowledge

Code dans secretkey may the force be with you

# Application VisiPilot : Questions sur IFSv8, PAM, et BRCGS V9

Bienvenue dans l'application VisiPilot, conçue pour vous aider à poser des questions sur les normes IFSv8, PAM, et BRCGS V9. Cette application utilise une intelligence artificielle pour analyser des documents spécifiques et fournir des réponses précises à vos questions.

## Fonctionnalités Principales

### Page 1 : Questions sur la norme BRCGS V9

- **But** : Permet aux utilisateurs de poser des questions sur la norme BRCGS V9.
- **Fonctionnement** :
  1. **Chargement du Document** : L'application télécharge un document contenant des informations sur la norme BRCGS V9 depuis un fichier hébergé sur GitHub.
  2. **Saisie de la Question** : Les utilisateurs peuvent saisir leur question dans un champ de texte.
  3. **Génération de la Réponse** : Une fois la question soumise, l'intelligence artificielle analyse le document et génère une réponse adaptée.
- **URL du Document** : [BRCGS V9 Guide d'interprétation](https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/BRC9_GUIde%20_interpretation.txt).

### Page 2 : Questions sur IFSv8 et PAM

- **But** : Permet aux utilisateurs de poser des questions sur les normes IFSv8 et PAM.
- **Fonctionnement** :
  1. **Chargement des Documents** : L'application télécharge plusieurs documents pertinents depuis Google Drive.
  2. **Saisie de la Question** : Les utilisateurs peuvent poser une question en lien avec ces normes.
  3. **Génération de la Réponse** : L'intelligence artificielle traite la question et renvoie une réponse basée sur le contenu des documents chargés.
- **Documents Chargés** : L'application charge plusieurs fichiers depuis Google Drive avec les IDs suivants :
  - `1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8`
  - `1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW`
  - `1pLieGU6lIO0RAzPFGy0oR2I6nxAA8tjc`

### Page 3 : Questions sur IFSv8 et MCDA

- **But** : Fournir des réponses aux questions liées à IFSv8 et MCDA (Méthode de Conception et Développement de l'Analyse).
- **Fonctionnement** :
  1. **Chargement des Documents** : Comme pour la page sur IFSv8 et PAM, cette page charge des documents spécifiques depuis Google Drive.
  2. **Saisie de la Question** : Un champ de texte est disponible pour poser des questions sur IFSv8 et MCDA.
  3. **Génération de la Réponse** : L'intelligence artificielle répond aux questions en analysant le contenu des documents.
- **Documents Chargés** : Les mêmes documents que ceux utilisés pour IFSv8 et PAM sont également utilisés ici.

## Comment Utiliser l'Application ?

1. **Ouvrir l'Application** :
   - Accédez à l'application via un lien web fourni ou en exécutant le code sur un serveur local.

2. **Naviguer Entre les Pages** :
   - Utilisez le menu latéral de l'application pour accéder aux différentes pages : BRCGS V9, IFSv8 & PAM, et IFSv8 & MCDA.

3. **Poser vos Questions** :
   - Sur chaque page, un champ de texte est disponible pour poser vos questions. Cliquez sur "Envoyer" pour recevoir une réponse générée par l'intelligence artificielle.

## Configuration Technique

- **API Key** : L'application nécessite une clé API pour Google Generative AI, à stocker dans les secrets de Streamlit (`st.secrets["api_key"]`).
- **Caching** : Les documents téléchargés sont mis en cache pour améliorer les performances et éviter les téléchargements répétitifs.

## Remarques Importantes

- **Sécurité** : Des paramètres de sécurité sont en place pour éviter la génération de contenu inapproprié ou dangereux.
- **Documents** : Les documents utilisés sont accessibles publiquement et sont essentiels pour fournir des réponses précises aux questions.

## Support et Aide

- **Aide** : Si vous avez besoin d'aide pour utiliser l'application, veuillez consulter la page d'aide ou contacter l'administrateur de l'application.
- **Rapport de Bugs** : Si vous rencontrez un problème, veuillez le signaler à l'administrateur.

Nous espérons que cette application vous sera utile pour obtenir des réponses précises et fiables sur les normes IFSv8, PAM, et BRCGS V9 !

