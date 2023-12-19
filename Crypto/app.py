from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime
import datetime
import requests
import json

app = Flask(__name__) #this has 2 underscores on each side
app.config['MYSQL_HOST'] = 'mysql.2122.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2122'
app.config['MYSQL_PASSWORD'] = 'm545CS42122'
app.config['MYSQL_DB'] = '2122project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] ='ka;iwjfiziejehwf'
mysql = MySQL(app)

@app.route('/')
def welcome():
    returnUser = returning()
    #getting the trend from api
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    data = json.loads(response.text)
    trend = []
    unixTime = []
    timeList = []
    historyPrice = []
    i = 0
    #getting the names of the top 5 trending cryptocurrency
    while i < 5:
        trend.append(data['coins'][i]['item']['name'])
        i = i + 1
    #getting the history of bitcoin for the past 5 days
    url2 = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=5'
    response = requests.get(url2)
    data = json.loads(response.text)
    #getting the datetime and historical price of bitcoin and appending onto two arrays
    for price in data['prices']:
        unixTime.append(price[0])
        historyPrice.append(int(price[1]))

    #the json file had the datetime in unixTime. Divided by 1000 because it was in
    #milliseconds. I can only use fromtimestamp if unixTime is in seconds
    #https://stackoverflow.com/questions/46565580/convert-unix-timestamp-in-python-to-datetime-and-make-2-hours-behind
    for i in unixTime:
        timeList.append(str(datetime.datetime.fromtimestamp(i/1000).strftime('%m-%d-%y %H:%M:%S')))
    return render_template('welcome.html', returnUser = returnUser, trend = trend, timeList= timeList, historyPrice = historyPrice,unixTime = unixTime)

@app.route('/signup', methods = ['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signupSuccess', methods = ['POST'])
def signupSuccess():
    username = request.form.get("username")
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    cursor = mysql.connection.cursor()
    passwordSame = True
    usernameUsed = False
    emailUsed = False
    usernameList = []
    emailList = []
    #checking if the user inputted something for all the form inputs
    if((password1 == password2) and len(username) > 0 and len(email) > 0 and len(password1) > 0):
        query = 'Select * FROM calvintran_login WHERE Username = %s'
        queryVars = (username,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        data = cursor.fetchall()
        #using try and except to check if there is a user with that usernameList
        #if there's an indexError that means there isn't one
        try:
            usernameList = data[0].values()
            usernameUsed = True
            return render_template('signupFail.html', passwordSame = passwordSame, usernameUsed = usernameUsed)
        except IndexError:
            query = 'Select * FROM calvintran_login WHERE Email = %s'
            queryVars = (email,)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            data = cursor.fetchall()
        #checking if there is a user with that email
        #if there's an indexError that means there isn't one
            try:
                emailList = data[0].values()
                emailUsed = True
                return render_template('signupFail.html', passwordSame = passwordSame, usernameUsed = usernameUsed, emailUsed = emailUsed)
            except IndexError:
                securedPassword = generate_password_hash(password1)
                queryVars2 = (username, email, securedPassword)
                query2 = 'INSERT INTO calvintran_login(Username, Email, Password) VALUES (%s, %s, %s)'
                cursor.execute(query2, queryVars2)
                mysql.connection.commit()
                return redirect(url_for('login'))
    else:
        passwordSame = False
        return render_template('signupFail.html', passwordSame = passwordSame)

@app.route('/login', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/loginSuccess', methods = ['POST'])
def loginSuccess():
    userTrue = True
    passwordTrue = True
    username = request.form.get("username")
    password = request.form.get("password")
    cursor = mysql.connection.cursor()
    queryVars = (username,)
    query = 'SELECT * FROM calvintran_login WHERE Username = %s'
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data = cursor.fetchall()
    #use try and except to check for if there is the user's input
    #username and password
    try:
        person = list(data[0].values())
        securedPassword = person[2]
        if check_password_hash(securedPassword, password):
            session['calvintran_username'] = username
            return redirect(url_for('welcome'))
        else:
            passwordTrue = False
            return render_template('loginFail.html', userTrue = userTrue, passwordTrue = passwordTrue)
    except:
        userTrue = False
        return render_template('loginFail.html', userTrue = userTrue, passwordTrue = passwordTrue)

@app.route('/logout')
def logout():
    session.pop('calvintran_username', None)
    return redirect(url_for('welcome'))

@app.route('/browse')
def browse():
    returnUser = returning()
    return render_template('browse.html', returnUser = returnUser)

@app.route('/browseSuccess', methods = ['POST'])
def browseSuccess():
    returnUser = returning()
    cryptoCurrency = request.form.get("crypto")
    #the api needs a lowercase name for the url to work
    cryptoCurrency = cryptoCurrency.lower()
    base = 'https://api.coingecko.com/api/v3/simple/price'
    url = base + "?ids=" + cryptoCurrency + "&vs_currencies=USD"
    #using try and except to see if the cryptocurrency exists, if it doesn't
    #a keyError will occur
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        cryptoPrice = data[cryptoCurrency]['usd']
        unixTime = []
        timeList = []
        historyPrice = []
        url2 = 'https://api.coingecko.com/api/v3/coins/'+ cryptoCurrency + '/market_chart?vs_currency=usd&days=5'
        response2 = requests.get(url2)
        data2 = json.loads(response2.text)
        for price in data2['prices']:
            unixTime.append(price[0])
            historyPrice.append(int(price[1]))
        for i in unixTime:
            timeList.append((datetime.datetime.fromtimestamp(i/1000).strftime('%m-%d-%y %H:%M:%S')))
        cryptoCurrency = cryptoCurrency.capitalize()
        return render_template('browseSuccess.html', cryptoPrice = cryptoPrice, returnUser = returnUser, timeList = timeList, historyPrice = historyPrice, cryptoCurrency = cryptoCurrency)
    except KeyError:
        return redirect(url_for('browseFail'))

@app.route('/browseFail')
def browseFail():
    returnUser = returning()
    return render_template('browseFail.html', returnUser = returnUser)

@app.route('/following')
def following():
    cursor = mysql.connection.cursor()
    username = session.get('calvintran_username')
    queryVars = (username,)
    query = 'SELECT * FROM calvintran_following WHERE Username = %s'
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data = cursor.fetchall()
    i = 0
    cryptoList = []
    while i < len(data):
        cryptoList.append(list((data[i].values()))[1])
        i = i + 1
    returnUser = returning()
    return render_template('following.html', cryptoList = cryptoList, returnUser = returnUser)

@app.route('/deleting', methods = ['POST'])
def deleting():
    found = False
    cursor = mysql.connection.cursor()
    username = session.get('calvintran_username')
    deleting = request.form.get('deleteCrypto')
    deleting = deleting.capitalize()
    queryVars = (username, deleting)
    query = 'DELETE FROM calvintran_following WHERE Username = %s AND Following = %s'
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    queryVars = (username,)
    query = 'SELECT * FROM calvintran_following WHERE Username = %s'
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data = cursor.fetchall()
    i = 0
    cryptoList = []
    while i < len(data):
        cryptoList.append(list((data[i].values()))[1])
        i = i + 1
    returnUser = returning()
    return render_template('deleting.html', cryptoList = cryptoList, returnUser = returnUser, found = found, deleting = deleting)

@app.route('/followSuccess', methods  = ['POST'])
def followSuccess():
    alreadyFollowing = False
    username = session.get('calvintran_username')
    cryptoCurrency = request.form.get("cryptoCurrency")
    cursor = mysql.connection.cursor()
    username = session.get('calvintran_username')
    returnUser = returning()
    queryVars = (username,)
    query = 'SELECT following FROM calvintran_following WHERE Username = %s'
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    data = cursor.fetchall()
    try:
        cryptoList = list(data[0].values())
        for i in cryptoList:
            if i == cryptoCurrency:
                alreadyFollowing = True
            else:
                queryVars2 = (username, cryptoCurrency)
                query2 = 'INSERT INTO calvintran_following(Username, Following) VALUES (%s, %s)'
                cursor.execute(query2, queryVars2)
                mysql.connection.commit()
            queryVars = (username,)
            query = 'SELECT * FROM calvintran_following WHERE Username = %s'
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            data = cursor.fetchall()
            i = 0
            cryptoList = []
            while i < len(data):
                cryptoList.append(list((data[i].values()))[1])
                i = i + 1
    except IndexError:
        queryVars2 = (username, cryptoCurrency)
        query2 = 'INSERT INTO calvintran_following(Username, Following) VALUES (%s, %s)'
        cursor.execute(query2, queryVars2)
        mysql.connection.commit()
        queryVars = (username,)
        query = 'SELECT * FROM calvintran_following WHERE Username = %s'
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        data = cursor.fetchall()
        i = 0
        cryptoList = []
        while i < len(data):
            cryptoList.append(list((data[i].values()))[1])
            i = i + 1
    return render_template('followSuccess.html', cryptoCurrency = cryptoCurrency, cryptoList = cryptoList, alreadyFollowing = alreadyFollowing, returnUser = returnUser)

def returning():
    if (session.get('calvintran_username')):
        returning = True
    else:
        returning = False
    return returning
