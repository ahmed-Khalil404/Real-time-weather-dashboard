# Tableau de bord météo en temps réel 🌍☁️

Le **Tableau de bord météo en temps réel** permet de surveiller l'environnement via des satellites. Ce système utilise le module **EchoStar-Term-7** pour collecter, transmettre et visualiser des données comme la température, la pression, l'humidité et l'altitude. Les données passent par une chaîne de traitement incluant **MQTT**, **Node-RED**, **InfluxDB** et **Grafana**.

---

## **Vue d'ensemble du projet**

Ce projet permet une surveillance environnementale dans des zones reculées où **l'accès direct à Internet** est impossible. Les données collectées sont transmises par satellite et traitées en temps réel pour fournir des informations précises .

---

## **Composants matériels**

### Spécifications EchoStar-Term-7

- **Microcontrôleur** : STM32U585CIT6
- **Module radio** : EchoStar EM2050
- **Module GNSS** : Quectel LC29H
- **Capteurs** :
  - **KX023-1025** : Accéléromètre
  - **BME280** : Capteur de température, pression, et humidité
  - **BME680/688** : Capteur de gaz
- **IO externes** : ADC, SPI, USART, I2C, etc.

---

## **Architecture du système**

### **Flux de données**

1. **Acquisition des données** :
   - Les données environnementales (température, pression, humidité, altitude) sont capturées avec le capteur **BME280**.

2. **Transmission** :
   - Les données sont emballées et envoyées vers le **satellite EchoStar** via le module radio **EchoStar EM2050**.

3. **Réception** :
   - Le satellite transfère les données à un **serveur au sol** à Sophia Antipolis via **MQTT**.

4. **Traitement** :
   - **Node-RED** s'abonne au flux MQTT et décode les données **Base64** en format lisible.

5. **Stockage et visualisation** :
   - Les données sont stockées dans **InfluxDB** pour une conservation à long terme.
   - **Grafana** affiche les visualisations en temps réel des données.

---

## **Composants logiciels**

### **Firmware (STM32U585CIT6)**

- Lit les données du **BME280**.
- Envoie les données via le module **EchoStar EM2050**.

### **Traitement côté serveur**

- Le **Broker MQTT** (ex : Mosquitto) reçoit les données d'EchoStar.
- **Node-RED** décode et formate les données pour **InfluxDB**.
- **InfluxDB** stocke les données des capteurs pour interrogation future.
- **Grafana** visualise les données en temps réel via des tableaux de bord interactifs.

---

## **Instructions de déploiement**

### **1. Configuration du matériel**
- Connecter le **BME280** via **I2C**.
- Configurer le module **EchoStar-Term-7** pour la communication par satellite.

### **2. Déploiement du firmware**
- Flasher le microcontrôleur STM32 avec le firmware fourni.
- Initialiser et configurer la communication satellite.

### **3. Configuration du serveur**
- Installer un **Broker MQTT** (ex : Mosquitto).
- Déployer **Node-RED** pour le traitement des données.
- Configurer **InfluxDB** pour le stockage des données.
- Connecter **Grafana** pour la visualisation des données en temps réel.

---

## 📊 **Surveillance des données en temps réel avec Grafana**

- **Surveiller** les conditions environnementales en temps réel (température, humidité, pression, altitude).
- **Suivre** l’historique des données pour analyser les tendances.
- **Personnaliser** les tableaux de bord selon vos besoins.

---

## 🛠 **Dépannage**

### **Problèmes de communication satellite**
- Vérifier la **connexion de l'antenne**.
- Vérifier la **disponibilité du réseau satellite**.
- Assurez-vous que l'appareil est **à l'extérieur** et non dans un espace fermé.

---

## **Améliorations futures**

- Ajouter d'autres capteurs (ex : **surveillance des gaz** ).
- Implémenter de la **détection d'anomalies** automatisée pour les alertes.
- Explorer le **calcul à la périphérie** pour prétraiter les données directement sur STM32.

---

## **Conclusion**

Le **Tableau de bord météo en temps réel** offre une solution complète de surveillance environnementale par satellite. Grâce à l'intégration de **MQTT**, **Node-RED**, **InfluxDB** et **Grafana**, vous pouvez surveiller et visualiser facilement les conditions météorologiques en temps réel depuis des lieux éloignés. 🌐
