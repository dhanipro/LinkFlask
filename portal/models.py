from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from portal import db, login_manager, select2
from flask_login import UserMixin
from flask_select2.contrib.sqla.ajax import QueryAjaxModelLoader
from hashlib import md5

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    biografi = db.Column(db.String(255))
    roles_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    active = db.Column(db.Boolean(), nullable=False, default=False)
    register_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    pages = db.relationship('Page', backref='author_pages', lazy=True)
    kategori = db.relationship('Kategori', backref='categories', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_BLOG']:
                self.active = True
                self.role = Role.query.filter_by(name='admin').first()
            else:
                self.role = Role.query.filter_by(name='writer').first()


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "User('{self.username}', '{self.email}', '{self.image_file}')"

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    @staticmethod
    def insert_roles():
        roles = ['admin', 'moderator', 'writer']
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            db.session.add(role)
        db.session.commit()

# Create M2M table
post_tags = db.Table('post_tags', db.Model.metadata,
                           db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                           db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                           )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    on_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_thumb = db.Column(db.String(255), nullable=False, default='default.jpg')
    slug = db.Column(db.String(255), nullable=False)
    publish = db.Column(db.Boolean(), nullable=False, default=True)
    headline = db.Column(db.Boolean(), nullable=False)
    dibaca = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    tags = db.relationship('Tag', secondary=post_tags, lazy='dynamic', backref='tagger')
    comments = db.relationship('Comments', backref='post_comment', lazy='dynamic')

    def __repr__(self):
        return "Post('{self.title}', '{self.date_posted}')"

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    on_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    slug = db.Column(db.String(255), nullable=False)
    publish = db.Column(db.Boolean(), nullable=False, server_default='1')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Post('{self.title}', '{self.date_posted}')"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    slug = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"{self.name}"

tag_loader = QueryAjaxModelLoader(
    name='tag',
    session=db.session,
    model=Tag,
    fields=['name'],
    order_by=[Tag.name.asc()],
    page_size=20,
    placeholder="Pilih tags"
)

select2.add_loader(loader=tag_loader)


class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts = db.relationship('Post', backref='category', lazy=True)

    def __repr__(self):
        return "Post('{self.nama_kategori}', '{self.date_posted}')"

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    comment = db.Column(db.Text, nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    date_comment = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    publish = db.Column(db.Boolean())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    children = db.relationship('Comments', backref=db.backref('reply', remote_side=[id]))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return "Comments('{self.comment}', '{self.date_comment}')"

class Hubungi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pesan = db.Column(db.TEXT, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "Hubungi('{self.nama}', '{self.date_posted}')"

class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "Hubungi('{self.email}', '{self.date_posted}')"