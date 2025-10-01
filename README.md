# 🗑️ XML Cleaner - Suppression automatique des balises "Coeff Fixe"

Application web Streamlit pour nettoyer automatiquement les fichiers XML en supprimant les blocs `<Rates>` contenant "Coeff Fixe".

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Description

Cette application permet de traiter rapidement des fichiers XML volumineux en supprimant automatiquement les balises spécifiques qui correspondent aux critères suivants :

- **Type de balise** : `<Rates>`
- **Attributs** : `rateType="pay"` ET `rateStatus="agreed"`
- **Contenu** : Contient `<Class>Coeff Fixe</Class>`

### 🎯 Cas d'usage

Idéal pour nettoyer des fichiers de paie, exports RH ou tout fichier XML contenant des données redondantes de type "Coefficient Fixe" qu'il faut supprimer en masse.

## ✨ Fonctionnalités

- ✅ **Upload simple** de fichiers XML via drag & drop
- ✅ **Détection automatique** des balises correspondant aux critères
- ✅ **Compteurs en temps réel** : nombre de balises trouvées et à supprimer
- ✅ **Aperçu avant suppression** des éléments ciblés
- ✅ **Suppression en un clic** de toutes les balises concernées
- ✅ **Téléchargement immédiat** du fichier nettoyé
- ✅ **Interface intuitive** et responsive

## 🚀 Démarrage rapide

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation locale

1. **Clonez le dépôt**
```bash
git clone https://github.com/votre-username/xml-cleaner.git
cd xml-cleaner
```

2. **Installez les dépendances**
```bash
pip install -r requirements.txt
```

3. **Lancez l'application**
```bash
streamlit run app.py
```

4. **Ouvrez votre navigateur**
L'application s'ouvre automatiquement à l'adresse : `http://localhost:8501`

## 🌐 Utilisation en ligne

L'application est déployée sur Streamlit Cloud :

👉 **[Accéder à l'application](https://votre-app.streamlit.app)** *(remplacez par votre URL)*

## 📖 Guide d'utilisation

### Étape 1 : Upload du fichier
![Upload](https://via.placeholder.com/600x200/4CAF50/FFFFFF?text=1.+Uploadez+votre+fichier+XML)

Glissez-déposez ou sélectionnez votre fichier XML.

### Étape 2 : Vérification
L'application affiche :
- Le nombre total de balises `<Rates>` trouvées
- Le nombre de balises "Coeff Fixe" qui seront supprimées
- Un aperçu des éléments concernés

### Étape 3 : Suppression
Cliquez sur le bouton **"SUPPRIMER LES BALISES"** pour nettoyer le fichier.

### Étape 4 : Téléchargement
Téléchargez votre fichier nettoyé avec le suffixe `_cleaned.xml`.

## 🔧 Exemple de balise supprimée

Voici un exemple de bloc XML qui sera supprimé :

```xml
<Rates rateType="pay" rateStatus="agreed">
  <Amount rateAmountPeriod="hourly" currency="EUR">22.446</Amount>
  <Class>Coeff Fixe</Class>
  <Multiplier percentIndicator="true">100.00</Multiplier>
  <StartDate>2025-09-22</StartDate>
  <RatesId idOwner="RIS">
    <IdValue>100010</IdValue>
  </RatesId>
  <BillingMultiplier percentIndicator="false">0</BillingMultiplier>
</Rates>
```

## 📁 Structure du projet

```
xml-cleaner/
│
├── app.py                 # Application Streamlit principale
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
└── .gitignore            # Fichiers à ignorer par Git
```

## 🛠️ Technologies utilisées

- **[Streamlit](https://streamlit.io/)** - Framework web Python
- **[ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)** - Parser XML Python natif

## 📝 Configuration

### Fichier `requirements.txt`
```txt
streamlit==1.31.0
```

### Variables d'environnement (optionnel)
Aucune variable d'environnement n'est requise pour le fonctionnement de base.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 🐛 Signaler un bug

Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/votre-username/xml-cleaner/issues) avec :
- Une description claire du problème
- Les étapes pour reproduire le bug
- Le comportement attendu vs le comportement observé
- Des captures d'écran si pertinent

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Auteur

**Votre Nom**
- GitHub: [@votre-username](https://github.com/votre-username)

## 🙏 Remerciements

- Merci à l'équipe Streamlit pour leur framework incroyable
- Communauté Python pour ElementTree

---

⭐ Si ce projet vous a aidé, n'hésitez pas à mettre une étoile !
