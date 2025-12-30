"""
Basic unit tests for Flask application
"""
import unittest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Student

class FlaskAppTestCase(unittest.TestCase):
    """Test cases for Flask application"""

    def setUp(self):
        """Set up test client and database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_app_imports(self):
        """Test that app module imports successfully"""
        self.assertIsNotNone(app)
        self.assertTrue(hasattr(app, 'config'))

    def test_home_route(self):
        """Test home route returns 200"""
        response = self.app.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_index_route(self):
        """Test index route returns 200"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_database_connection(self):
        """Test database connection and model creation"""
        with app.app_context():
            student = Student(
                student_id='TEST001',
                roll_number='R001',
                student_name='Test Student',
                phone_number='1234567890'
            )
            db.session.add(student)
            db.session.commit()
            
            retrieved = Student.query.filter_by(student_id='TEST001').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.student_name, 'Test Student')

if __name__ == '__main__':
    unittest.main()

