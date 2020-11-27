import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_select2 import Select2
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from flask_wtf import CSRFProtect  # if you want to enable CSRF protect, uncomment this line
from .utils import indonesia_time
from .config import Config

basedir = os.path.abspath(os.path.dirname(__file__))

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/database'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:1ac3d18d@localhost:5432/database'
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
bcrypt = Bcrypt()
select2 = Select2()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'is-info'
login_manager.login_message = "Silahkan login untuk akses halaman ini."

mail = Mail()
ckeditor = CKEditor()
csrf = CSRFProtect()  # if you want to enable CSRF protect, uncomment this line

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    bcrypt.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)  # if you want to enable CSRF protect, uncomment this line
    select2.init_app(app)
    login_manager.init_app(app)


    # Register blueprints
    from portal.auth.routes import auth
    app.register_blueprint(auth)

    from portal.admin.routes import admin
    app.register_blueprint(admin)

    from portal.posts.routes import posts
    app.register_blueprint(posts)

    from portal.api.routes import api
    app.register_blueprint(api)

    # register custom filters
    app.jinja_env.filters['indonesia_time'] = indonesia_time

    return app