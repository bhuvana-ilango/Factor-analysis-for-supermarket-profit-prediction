import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for
import pickle
import firebase_admin
from firebase_admin import credentials, initialize_app, auth
import pyrebase

# cred = credentials.Certificate("firebase.json")
# firebase_admin.initialize_app(cred)

config = {
  "apiKey": "AIzaSyDxFetJC4NHEX1i0boTDiXEjpvD8gkgDb4",
  "authDomain": "supermarket-sales-e6eee.firebaseapp.com",
  "projectId": "supermarket-sales-e6eee",
  "storageBucket": "supermarket-sales-e6eee.appspot.com",
  "messagingSenderId": "230477327371",
  "appId": "1:230477327371:web:254a1e7429482698176b0e",
  "measurementId": "G-TMLTMEE8SH",
  "databaseURL": "https://supermarket-sales-e6eee-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    return render_template('predict.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/predict/results', methods=['POST'])
def results():
      features = [float(x) for x in request.form.values()]
      final_features = [np.array(features)]
      prediction = model.predict(final_features)

      output = round(prediction[0], 1)

      return render_template('results.html', prediction_text = output)

@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    return render_template("dashboard.html")

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        print(email, password)
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('dashboard'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        print(email, password)
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('dashboard'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('signup'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('signup'))

if __name__ == "__main__":
  app.run()