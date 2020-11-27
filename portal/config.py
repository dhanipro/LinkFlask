import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    ADMIN_BLOG = 'email@email.com'
    SECRET_KEY = os.getenv('SECRET_KEY', default='secretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', default='sqlite:///site.db')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    UPLOADED_PATH = os.path.join(basedir, 'static/upload')

    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 400
    CKEDITOR_EXTRA_PLUGINS = ['youtube']
    CKEDITOR_FILE_UPLOADER = 'admin.upload'
    CKEDITOR_ENABLE_CSRF = True  # if you want to enable CSRF protect, uncomment this line