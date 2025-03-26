from flask import Flask, render_template, request, redirect, url_for, flash
import pickle
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import session




popular_df=pickle.load(open('popular.pkl','rb'))
pt=pickle.load(open('pt.pkl','rb'))
books=pickle.load(open('books.pkl','rb'))
similarity_score=pickle.load(open('similarity_score.pkl','rb'))


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # XAMPP default MySQL password
# app.config['MYSQL_DB'] = 'book recommended'
app.config['MYSQL_DB'] = 'book recommended'  # Use underscores for valid naming


mysql = MySQL(app)
google_drive_base_url = "https://drive.google.com/file/d/"


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            user = cursor.fetchone()
            cursor.close()
        except Exception as e:
            flash('Database error occurred. Please try again later.', 'danger')
            return render_template('login.html')

        if user and user[5] == password:  # Assuming password is stored in the 5th column
            session['loggedin'] = True
            session['id'] = user[0]       # Assuming user ID is in the 0th column
            session['email'] = user[4]    # Assuming email is in the 4th colum
            flash('Login successful!', 'success')
            return redirect(url_for('second'))
        elif user:
            flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('Email not found. Please sign up.', 'warning')
            return redirect(url_for('signup'))

    return render_template('login.html')

@app.route('/second')
def second():
    return render_template('second.html' ,book_name=list(popular_df['Book-Title'].values), author=list(popular_df['Book-Author'].values),image=list(popular_df['Image-URL-M'].values), votes=list(popular_df['Book-Rating'].values), rating  =list(popular_df['avg_ratings'].values))

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dev')
def dev():
    return render_template('dev.html')

@app.route('/forgetpass')
def forgetpass():
    return render_template('forgetpass.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Print the form data received from the user
        print(request.form)  # This will print all form fields and their values

        # Now proceed with form validation and insertion into the database
        if 'username' in request.form and 'email' in request.form and 'password' in request.form:
            username = request.form['username']
            email = request.form['email']
            # password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            password = request.form['password']


            # Insert into MySQL
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO user (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            cursor.close()

            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))  # Redirect to login page
        else:
            flash('Missing form data. Please try again.', 'danger')

    return render_template('signup.html')  # Show signup form for GET requests

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

def get_file_id(book_id):
    # Implement your logic to retrieve the file ID for a given book ID
    return "1ufRI06Gj1n4JI84MmALNv5UM6LDhP8Zr"

@app.route("/showbook")
def index():
    # ... your logic to retrieve book data ...
    books = [
        {"book_id": 1, "image": "...", "book_name": "..."},
        {"book_id": 2, "image": "...", "book_name": "..."},
    ]
    return render_template("index.html", books=books)

@app.route('/recommend_books',methods=['post'])
def recommend_book():
    user_input=request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    
    # Find the most similar items, sorted by similarity score, excluding the first (which is the book itself)
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        item.append(temp_df['Book-Title'].values[0])
        item.append(temp_df['Book-Author'].values[0])
        item.append(temp_df['Image-URL-M'].values[0])
        data.append(item)
        
    print(data)
    
    return render_template('recommend.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)
