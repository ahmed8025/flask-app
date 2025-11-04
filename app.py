from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_bcrypt import Bcrypt
from wtforms import StringField, TextAreaField, validators
from werkzeug.exceptions import NotFound, InternalServerError
import re
import os

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

# Custom validators for input sanitization
def validate_no_sql_injection(form, field):
    """Prevent SQL injection attempts in text fields"""
    sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'union', 'exec', 'script']
    value = field.data.lower() if field.data else ''
    for keyword in sql_keywords:
        if keyword in value:
            raise validators.ValidationError(f'Invalid input detected. Please avoid using "{keyword}" in your input.')

def validate_no_xss(form, field):
    """Prevent XSS attempts in text fields"""
    xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'onclick=']
    value = field.data.lower() if field.data else ''
    for pattern in xss_patterns:
        if pattern in value:
            raise validators.ValidationError('Invalid input detected. Please avoid using script-related content.')

def validate_phone_number(form, field):
    """Validate phone number format"""
    if field.data:
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern, field.data.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')):
            raise validators.ValidationError('Please enter a valid phone number.')

# Secure Form Classes
class StudentForm(FlaskForm):
    student_id = StringField('Student ID', [
        validators.DataRequired(message='Student ID is required'),
        validators.Length(min=1, max=80, message='Student ID must be between 1 and 80 characters'),
        validate_no_sql_injection,
        validate_no_xss
    ])
    roll_number = StringField('Roll Number', [
        validators.DataRequired(message='Roll number is required'),
        validators.Length(min=1, max=80, message='Roll number must be between 1 and 80 characters'),
        validate_no_sql_injection,
        validate_no_xss
    ])
    student_name = StringField('Student Name', [
        validators.DataRequired(message='Student name is required'),
        validators.Length(min=1, max=80, message='Student name must be between 1 and 80 characters'),
        validators.Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces'),
        validate_no_sql_injection,
        validate_no_xss
    ])
    phone_number = StringField('Phone Number', [
        validators.DataRequired(message='Phone number is required'),
        validators.Length(min=10, max=15, message='Phone number must be between 10 and 15 characters'),
        validate_phone_number,
        validate_no_sql_injection,
        validate_no_xss
    ])

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(80), nullable=False, unique=True)
    roll_number = db.Column(db.String(80), nullable=False, unique=True)
    student_name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)  # For password storage

    def __repr__(self):
        return f"<Student {self.student_id}>"
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

# Create database tables
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def hello_world():
    form = StudentForm()
    if form.validate_on_submit():
        try:
            # Check for duplicate student_id or roll_number
            existing_student = Student.query.filter(
                (Student.student_id == form.student_id.data) | 
                (Student.roll_number == form.roll_number.data)
            ).first()
            
            if existing_student:
                flash('Student ID or Roll Number already exists!', 'error')
            else:
                student = Student(
                    student_id=form.student_id.data.strip(),
                    roll_number=form.roll_number.data.strip(),
                    student_name=form.student_name.data.strip(),
                    phone_number=form.phone_number.data.strip(),
                )
                db.session.add(student)
                db.session.commit()
                flash('Student added successfully!', 'success')
                return redirect(url_for("hello_world"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the student.', 'error')
            app.logger.error(f"Error adding student: {str(e)}")

    students = Student.query.all()
    return render_template("index.html", students=students, form=form)


@app.route("/delete/<int:student_pk>", methods=["POST"])
def delete_student(student_pk: int):
    try:
        student = Student.query.get_or_404(student_pk)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the student.', 'error')
        app.logger.error(f"Error deleting student: {str(e)}")
    return redirect(url_for("hello_world"))


@app.route("/edit/<int:student_pk>", methods=["GET", "POST"])
def edit_student(student_pk: int):
    student = Student.query.get_or_404(student_pk)
    form = StudentForm(obj=student)
    
    if form.validate_on_submit():
        try:
            # Check for duplicate student_id or roll_number (excluding current student)
            existing_student = Student.query.filter(
                (Student.student_id == form.student_id.data) | 
                (Student.roll_number == form.roll_number.data)
            ).filter(Student.id != student_pk).first()
            
            if existing_student:
                flash('Student ID or Roll Number already exists!', 'error')
            else:
                student.student_id = form.student_id.data.strip()
                student.roll_number = form.roll_number.data.strip()
                student.student_name = form.student_name.data.strip()
                student.phone_number = form.phone_number.data.strip()
                db.session.commit()
                flash('Student updated successfully!', 'success')
                return redirect(url_for("hello_world"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the student.', 'error')
            app.logger.error(f"Error updating student: {str(e)}")

    return render_template("edit.html", student=student, form=form)


@app.route("/home")
def home():
    return "Welcome to home page"

# Custom Error Handlers for Security
@app.errorhandler(404)
def not_found_error(error):
    """Custom 404 error page to prevent information disclosure"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error page to prevent information disclosure"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Handle CSRF token errors"""
    flash('Security token expired. Please try again.', 'error')
    return redirect(url_for('hello_world'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)