from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model



from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-very-very-secret-key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'docai'
app.config['UPLOADS'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load the model for grayscale images
model_path = 'models/my_model_breast_cancer.h5'
model = load_model(model_path)

mysql = MySQL(app)




@app.route('/', endpoint='home')
def home():
    return render_template('home.html')
@app.route('/about', endpoint='about')
def about():
    return render_template('about.html')

@app.route('/contactus', endpoint='contactus')
def about():
    return render_template('contactus.html')

@app.route('/prediction')
def prediction():
    # Check if user is logged in
    if 'loggedin' in session:
        # If logged in, proceed to render the prediction page
        return render_template('prediction.html')
    else:
        # If not logged in, redirect to login page
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('login'))





# -------------------------Patient registration form ----------------------------
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired(), Length(min=1, max=50)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=255)])
    submit = SubmitField('Register')

    def validate_email(self, email):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email.data,))
        account = cursor.fetchone()
        if account:
            raise ValidationError('An account with this email already exists.')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

@app.route('/contactus', methods=['GET', 'POST'])
def contact_us():
    form = ContactForm()  # Instantiate your form class
    if form.validate_on_submit():
        # Here you would typically gather the data and send an email or store it in the database
        # flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('home'))  # Redirect to home or a 'thank you' page after form submission
    return render_template('contactus.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = generate_password_hash(form.password.data)  

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO accounts (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)', (firstname, lastname, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('You have successfully registered! You can now login.', 'success') 
        return redirect(url_for('login'))
    return render_template('register.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email =%s',(email,))

        account = cursor.fetchone()

        if account and check_password_hash(account['password'], password):
            firstname= account['firstname']
            lastname = account['lastname']
            fullname = firstname +" " +lastname
            session['fullname'] = fullname
            session['email'] = account['email']
                
            session['loggedin'] = True
            session['id'] = account['id']
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))  
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
              
    return render_template('login.html', form=form)

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        # Logic to display user profile
        return render_template('prediction.html')
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('fullname',None)

    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))





@app.route('/skinuploads/<filename>')
def skin_uploaded_file(filename):
    return send_from_directory(app.config['UPLOADS'], filename)




@app.route('/my_uploads')
def my_uploads():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 

    cursor.execute('SELECT * FROM predictions WHERE user_id = %s ORDER BY uploaded_at DESC', (user_id,))
    predictions = cursor.fetchall()
    
    for prediction in predictions:
        prediction['image_path'] = prediction['image_path'].replace('\\', '/')
    
    cursor.close()
    return render_template('my_uploads.html', predictions=predictions)


# ----------------------------------------------------------------------------------------------
#
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(image_path, model):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (224, 224))
    img = img.reshape(-1, 224, 224, 1)
    img = img / 255.0
    prediction = model.predict(img)
    return np.argmax(prediction)

@app.route('/scan', methods=['POST'])
def scan_image():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to access this feature'}), 403

    if 'skinImage' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400

    file = request.files['skinImage']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # This is the right way to save the filename in the database.
        filepath = os.path.join(app.config['UPLOADS'], filename)
        file.save(filepath)
        db_filepath = filename  # Save only the filename for database insertion

        prediction_index = predict_image(filepath, model)
        class_labels = ['Benign', 'Malignant', 'Normal']
        prediction_label = class_labels[prediction_index]

        try:
            # Insert prediction result into the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO predictions (user_id, image_path, prediction_result, uploaded_at) VALUES (%s, %s, %s, NOW())', 
               (session['id'], db_filepath, prediction_label))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert prediction into database: {e}")
            return jsonify({'success': False, 'message': 'Failed to store prediction in database'}), 500

        return jsonify({'success': True, 'message': 'Success', 'prediction': prediction_label})
    else:
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400


# @app.route('/scan', methods=['POST'])
# def scan_image():
#     if 'skinImage' not in request.files:
#         flash('No file part')
#         return redirect(request.url)
    
#     file = request.files['skinImage']
#     if file.filename == '':
#         flash('No selected file')
#         return redirect(request.url)
    
#     if file and allowed_file(file.filename):        
#         filepath = os.path.join(app.config['UPLOADS'], secure_filename(file.filename))
#         file.save(filepath)

#         prediction_index = predict_image(filepath, model)
#         # Update your class_labels as necessary
#         class_labels = ['Benign', 'Malignant', 'Normal']
#         prediction_label = class_labels[prediction_index]

#         return jsonify({'success': True, 'message': 'Success', 'prediction': prediction_label})

#     else:
#         flash('Invalid file type')
#         return redirect(request.url)

# Your code to run the app remains the same
if __name__ == '__main__':
    app.run(debug=True)