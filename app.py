import os
from flask import Flask, render_template, request, redirect, url_for,session
import uuid
import certifi
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "supersecretkey123"


client = MongoClient(
    "mongodb+srv://yashaswiniiiav2004_db_user:yashaswini2004@cluster0.hr7uqcm.mongodb.net/?appName=Cluster0",
    tls=True,                 # enable SSL
    tlsCAFile=certifi.where() # use Python's trusted certificate file
)

db = client['digital_card_db']       # replace with your DB name
collection = db['cards'] 
users_collection = db['users'] # replace with your collection name

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        card_id = str(uuid.uuid4())

        data = {
            "fullname": request.form.get('fullname'),
            "title": request.form.get('title'),
            "company": request.form.get('company'),
            "tagline": request.form.get('tagline'),
            "mobile": request.form.get('mobile'),
            "email": request.form.get('email'),
            "bio": request.form.get('bio'),
            "linkedin": request.form.get('linkedin') or None,
            "github": request.form.get('github')or None,
            "instagram": request.form.get('instagram')or None
            
        }

        data["_id"] = card_id
        collection.insert_one(data)

        return redirect(url_for('view_card', card_id=card_id))

    return render_template('index.html')


@app.route('/card/<card_id>')
def view_card(card_id):
    card = collection.find_one({"_id": card_id})

    if card:
        card['_id'] = str(card['_id'])   # 🔥 THIS LINE IMPORTANT
        return render_template('card.html', card=card)
    else:
        return "Card not found"
@app.route('/edit/<card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    card = collection.find_one({"_id": card_id})

    if request.method == 'POST':
        updated_data = {
            "fullname": request.form.get('fullname'),
            "title": request.form.get('title'),
            "company": request.form.get('company'),
            "tagline": request.form.get('tagline'),
            "mobile": request.form.get('mobile'),
            "email": request.form.get('email'),
            "bio": request.form.get('bio'),
            "linkedin": request.form.get('linkedin') or None,
            "github": request.form.get('github')or None,
            "instagram": request.form.get('instagram')or None
        }

        collection.update_one({"_id": card_id}, {"$set": updated_data})

        return redirect(url_for('view_card', card_id=card_id))

    return render_template('edit.html', card=card) 
@app.route('/delete/<card_id>')
def delete_card(card_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    collection.delete_one({"_id": card_id})
    return "Card Deleted Successfully" 
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })

        return redirect(url_for('login'))

    return render_template('register.html') 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
