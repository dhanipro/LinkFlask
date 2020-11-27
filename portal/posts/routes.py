from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app
from portal import db
from flask_login import current_user
from portal.posts.forms import HubungiForm, SubscribersForm, CommentForm
from portal.models import User, Role, Post, Comments, Kategori, Tag, Page, Hubungi, Subscribers
from .utils import utils_context
import datetime

posts = Blueprint('posts', __name__)


@posts.app_errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error/404.html', **utils_context()), 404

@posts.app_errorhandler(403)
def page_deny(e):
    # note that we set the 404 status explicitly
    return render_template('error/403.html', **utils_context()), 403

@posts.before_app_first_request
def before_first_request_func():
    db.create_all()
    Role.insert_roles()

@posts.context_processor
def waktu():
    return utils_context()

@posts.route("/")
@posts.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    headline = Post.query.filter_by(headline = True).order_by(Post.date_posted.desc()).first()
    posts = Post.query.filter_by(publish=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('post/home.html', posts=posts, headline=headline)

@posts.route("/artikel/<berita>/<string:post_id>", methods=['GET', 'POST'])
def post(berita=None, post_id=None):
    form_comment = CommentForm(prefix='form_comment')
    form_reply = CommentForm(prefix='form_reply')
    post = Post.query.filter_by(slug=post_id, publish=True).first_or_404()
    similar = Post.query.join(Post.tags).filter(Tag.id==post.tags[0].id, Post.id != post.id).order_by(Post.date_posted.desc()).limit(3).all()
    if current_user.is_anonymous:
        post.dibaca += 1
        db.session.commit()
    if form_comment.validate_on_submit():
        comment = Comments(name=form_comment.nama.data, email=form_comment.email.data, 
        website=form_comment.website.data, comment=form_comment.comment.data, publish=True,
        post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Komentar berhasil ditambahkan', 'is-success')
        return redirect(url_for('posts.post', berita=post.category.slug, post_id=post.slug))
    if form_reply.validate_on_submit():
        reply_id = request.form.get('commentId')
        reply = Comments(name=form_reply.nama.data, email=form_reply.email.data, 
        website=form_reply.website.data, comment=form_reply.comment.data, publish=True,
        reply_id=reply_id, post_id=post.id
        )
        db.session.add(reply)
        db.session.commit()
        flash('Balasan komentar berhasil ditambahkan', 'is-success')
        return redirect(url_for('posts.post', berita=post.category.slug, post_id=post.slug))
    return render_template('post/detail.html', post=post, meta=post.title, similar=similar, form_comment=form_comment, form_reply=form_reply)

@posts.route("/category/<string:slug_kategori>")
def kategori(slug_kategori):
    kategori = Kategori.query.all()
    single_kategori = Kategori.query.filter_by(slug=slug_kategori).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(kategori_id=single_kategori.id).order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('post/category.html', kategori=kategori, posts=posts, single_kategori=single_kategori, label='kategori')

@posts.route("/search")
def search():
    search = request.args.get('q', None)
    kata = search.split()
    # agar dapat menggunakan template category
    single_kategori = dict(name=search)
    # end agar dapat menggunakan template category
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.title.like('%'+kata[0]+'%'), Post.publish==True).order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('post/category.html', posts=posts, label='pencarian', single_kategori=single_kategori)

@posts.route("/topik/<string:slug_tag>")
def topik(slug_tag):
    single_kategori = Tag.query.filter_by(slug=slug_tag).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(Post.tags).filter(Tag.slug==slug_tag)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('post/category.html', posts=posts, single_kategori=single_kategori, label='topik')

#pages halaman
@posts.route("/halaman/<string:slug>")
def halaman(slug):
    halaman = Page.query.filter_by(slug=slug).first_or_404()
    return render_template('post/halaman.html', halaman=halaman)

#sitemap xml
@posts.route("/sitemap.xml")
def sitemap_xml():
    artikel = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('post/sitemap.xml', artikel=artikel, base_url='https://blog.dhanipro.com')

@posts.route("/subscribe", methods=['GET', 'POST'])
def subscribe():
    form = SubscribersForm()
    if form.validate_on_submit():
        sub = Subscribers(email=form.email.data)
        db.session.add(sub)
        db.session.commit()
        flash('Data Anda berhasil disimpan, kami akan mengirim email ke Anda jika ada pembaruan konten', 'is-success is-light')
        return redirect(request.url)
    return redirect(url_for('posts.home'))
