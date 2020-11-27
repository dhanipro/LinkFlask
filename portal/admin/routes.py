import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort, Markup, send_from_directory, jsonify, Blueprint, current_app
from portal import db, bcrypt, mail
from portal.models import User, Post, Comments, Kategori, Tag, Page, Hubungi, Subscribers, Role
from .forms import PostForm, KategoriForm, TagForm, HalamanForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from slugify import slugify
from .utils import save_picture, save_picture_profile
from portal.posts.utils import utils_context

admin = Blueprint('admin', __name__, url_prefix='/admin123')

@admin.context_processor
def admin_konteks():
    user_post = User.query.all()
    return dict(user_post=user_post, **utils_context())

@admin.route("/")
@login_required
def admin_index():
    if not current_user.active:
        abort(403)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('admin/home.html', posts=posts)

# kategori
@admin.route("/kategori")
@login_required
def kategori():
    if not current_user.active:
        abort(403)
    kategori = Kategori.query.all()
    return render_template('admin/kategori.html', kategori=kategori)

@admin.route('/add_kategori', methods=['GET','POST'])
@login_required
def add_kategori():
    if not current_user.active:
        abort(403)
    form = KategoriForm()
    if form.validate_on_submit():
        if request.form.get('gutters'):
            kategori = Kategori(name=form.nama.data, slug=slugify(form.nama.data), user_id=current_user.id, gutters=True)
        else:
            kategori = Kategori(name=form.nama.data, slug=slugify(form.nama.data), user_id=current_user.id)
        db.session.add(kategori)
        db.session.commit()
        flash('Kategori Berhasil ditambah!', 'is-success')
        return redirect(url_for('admin.kategori'))
    return render_template('admin/tambah_kategori.html', form=form)

@admin.route('/update_kategori/<int:kategori_id>/update', methods=['GET','POST'])
@login_required
def update_kategori(kategori_id):
    if not current_user.active:
        abort(403)
    kategori = Kategori.query.get_or_404(kategori_id)
    form = KategoriForm()
    if form.validate_on_submit():
        kategori.name = form.nama.data
        db.session.commit()
        flash("Kategori berhasil diupdated!", 'is-success')
        return redirect(url_for('admin.kategori'))
    form.nama.data = kategori.name
    return render_template('admin/tambah_kategori.html', form=form)

@admin.route("/kategori/<int:kategori_id>/delete")
@login_required
def delete_kategori(kategori_id):
    if not current_user.active:
        abort(403)
    kategori = Kategori.query.get_or_404(kategori_id)
    if current_user.email != current_app.config['ADMIN_BLOG']:
        abort(403)
    db.session.delete(kategori)
    db.session.commit()
    flash('Kategori berhasil dihapus', 'is-success')
    return redirect(url_for('admin.kategori'))
# end kategori

# tag
@admin.route("/tag")
@login_required
def tag():
    if not current_user.active:
        abort(403)
    tags = Tag.query.all()
    return render_template('admin/tag.html', tags=tags)


@admin.route('/add_tag', methods=['GET','POST'])
@login_required
def add_tag():
    if not current_user.active:
        abort(403)
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.nama.data, slug=slugify(form.nama.data))
        db.session.add(tag)
        db.session.commit()
        flash('Topik Berhasil ditambah!', 'is-success')
        return redirect(url_for('admin.tag'))
    return render_template('admin/add_tag.html', form=form)

@admin.route('/update_tag/<int:id>/update', methods=['GET','POST'])
@login_required
def update_tag(id):
    if not current_user.active:
        abort(403)
    tag = Tag.query.get_or_404(id)
    form = TagForm()
    if form.validate_on_submit():
        tag.name = form.nama.data
        db.session.commit()
        flash("Topik berhasil diupdated!", 'is-success')
        return redirect(url_for('admin.tag'))
    form.nama.data = tag.name
    return render_template('admin/add_tag.html', form=form)

@admin.route("/tag/<int:tag_id>/delete")
@login_required
def delete_tag(tag_id):
    if not current_user.active:
        abort(403)
    tag = Tag.query.get_or_404(tag_id)
    if current_user.email != current_app.config['ADMIN_BLOG']:
        abort(403)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag berhasil dihapus', 'is-success')
    return redirect(url_for('admin.tag'))

# end tag

# post
@admin.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if not current_user.active:
        abort(403)
    form = PostForm()
    form.kategori.choices = [(str(kategori.id), kategori.name)for kategori in Kategori.query.all()]
    form.kategori.choices.insert(0,('', '== Pilih Kategori =='))
    topik = Tag.query.all()
    random_hex = secrets.token_hex(3)
    if form.validate_on_submit():
        url_link = slugify(form.title.data + ' ' + random_hex)
        if form.thumbnail.data:
            picture_file = save_picture(form.thumbnail.data)
            post = Post(title=form.title.data, content=form.content.data, image_thumb=picture_file, slug=url_link, headline=form.is_headline.data, author=current_user, kategori_id=form.kategori.data)
        else:
            post = Post(title=form.title.data, content=form.content.data, slug=url_link, headline=form.is_headline.data, author=current_user, kategori_id=form.kategori.data)
        selected_tags = request.form.get('multiple_company')
        if selected_tags:
            my_tag = selected_tags.split(',')
            for checkbox in my_tag:
                check = Tag.query.get(checkbox)
                post.tags.append(check)
            db.session.add(post) 
        db.session.commit()
        flash('Artikel Anda berhasil dibuat!', 'is-success')
        return redirect(url_for('admin.admin_index'))
    return render_template('admin/create_post.html', title='Post Baru',
                           form=form, legend='New Post', topik=topik)

@admin.route('/uploads/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


@admin.route('/upload', methods=['POST'])
def upload():
    random_hex = secrets.token_hex(8)
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    nama_gambar = f.filename.split('.')[0]
    nama_tersimpan = nama_gambar + '-' + random_hex + '.' + extension
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], nama_tersimpan))
    url = url_for('admin.uploaded_files', filename=nama_tersimpan)
    return upload_success(url=url)

@admin.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    if not current_user.active:
        abort(403)
    post = Post.query.get_or_404(post_id)
    topik = Tag.query.all()
    if post.author != current_user:
        abort(403)
    form = PostForm(kategori=post.kategori_id)
    form.kategori.choices = [(str(kategori.id), kategori.name)for kategori in Kategori.query.all()]
    if form.validate_on_submit():
        if form.thumbnail.data:
            picture_file = save_picture(form.thumbnail.data)
            post.image_thumb = picture_file
        post.title = form.title.data
        post.content = form.content.data
        post.headline = form.is_headline.data
        post.kategori_id = form.kategori.data
        #hapus tags dulu
        hapus_tag = post.tags
        for hapus in hapus_tag:
            checkbox = Tag.query.get(hapus.id)
            post.tags.remove(checkbox)
        #baru ditambah tags
        if form.multiple_company.data:
            selected_tags = request.form.get('multiple_company')
            my_tag = selected_tags.split(',')
            for checkbox in my_tag:
                check = Tag.query.get(checkbox)
                post.tags.append(check)
        
        db.session.commit()
        flash("Postingan berhasil diupdate", 'is-success')
        return redirect(url_for('admin.admin_index'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.multiple_company.data = post.tags
        form.is_headline.data = post.headline
    return render_template('admin/create_post.html', title='Update Post',
                           form=form, legend='Update Post', topik=topik, post=post)

@admin.route("/post/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    if not current_user.active:
        abort(403)
    post = Post.query.get_or_404(post_id)
    if current_user.email != current_app.config['ADMIN_BLOG'] or current_user.id != post.author.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post berhasil dihapus', 'is-success')
    return redirect(url_for('admin.admin_index'))

@admin.route("/send-to-subscribers/<int:post_id>")
@login_required
def send_to_subscribers(post_id):
    if current_user.role.name != 'admin' and current_user.role.name != 'moderator':
        abort(403)
    post = Post.query.get_or_404(post_id)
    subscribers = Subscribers.query.all()
    msg = Message(post.title,
                  sender='noreply@demo.com',
                  recipients=[subscriber.email for subscriber in subscribers])
    msg.html = render_template('admin/mail.html', post=post, link=url_for('posts.post', berita=post.category.slug, post_id=post.slug)) 
    mail.send(msg)
    flash('Postingan berhasil dikirim ke-email pelanggan', 'is-success')
    return redirect(url_for('admin.admin_index'))
# end post

@admin.route("/account/<int:id>/update", methods=['GET', 'POST'])
@login_required
def account(id):
    if current_user.email != current_app.config['ADMIN_BLOG']:
        abort(403)
    user = User.query.get_or_404(id)
    form = UpdateAccountForm(role=user.roles_id)
    form.role.choices = [(str(role.id), role.name)for role in Role.query.all()]
    form.role.choices.insert(0,('', '== Pilih Role =='))
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture_profile(form.picture.data)
            user.image_file = picture_file
        user.username = form.username.data
        user.roles_id = form.role.data
        user.biografi = form.biografi.data
        user.active = form.active.data
        db.session.commit()
        flash('Akun Anda berhasil diupdate!', 'is-success')
        return redirect(url_for('admin.users'))
    form.username.data = user.username
    form.email.data = user.email
    form.active.data = user.active
    form.biografi.data = user.biografi 
    return render_template('admin/account.html', user=user, title='Account', form=form)

# Pages
@admin.route("/page/new", methods=['GET', 'POST'])
@login_required
def new_page():
    if not current_user.active:
        abort(403)
    form = HalamanForm()
    if form.validate_on_submit():
        halaman = Page(title=form.title.data, content=form.content.data, slug=slugify(form.title.data), user_id=current_user.id)
        db.session.add(halaman)
        db.session.commit()
        flash('Halaman berhasil dibuat!', 'is-success')
        return redirect(url_for('admin.pages'))
    return render_template('admin/create_page.html', title='Halaman Baru',
                           form=form, legend='Halaman Baru')

@admin.route("/page")
@login_required
def pages():
    if not current_user.active:
        abort(403)
    page = request.args.get('page', 1, type=int)
    pages = Page.query.order_by(Page.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('admin/pages.html', pages=pages)


@admin.route("/page/<int:id>/update", methods=['GET', 'POST'])
@login_required
def update_page(id):
    if not current_user.active:
        abort(403)
    halaman = Page.query.get_or_404(id)
    form = HalamanForm()
    if form.validate_on_submit():
        halaman.title = form.title.data
        halaman.content = form.content.data
        halaman.publish = form.is_active.data
        db.session.commit()
        flash('Halaman berhasil diupdate!', 'is-success')
        return redirect(url_for('admin.pages'))
    elif request.method == 'GET':
        form.title.data = halaman.title
        form.content.data = halaman.content
        form.is_active.data = halaman.publish
    return render_template('admin/create_page.html', title='Update Page',
                           form=form, legend='Update Page')

@admin.route("/page/<int:page_id>/delete")
@login_required
def delete_page(page_id):
    if not current_user.active:
        abort(403)
    page = Page.query.get_or_404(page_id)
    if current_user.email != current_app.config['ADMIN_BLOG'] or current_user.id != page.author_pages.id:
        abort(403)
    db.session.delete(page)
    db.session.commit()
    flash('Page berhasil dihapus', 'is-success')
    return redirect(url_for('admin.pages'))

# end pages

# role

@admin.route("/users")
@login_required
def users():
    if current_user.role.name != 'admin':
        abort(403)
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# end role

# comment
@admin.route("/comments")
@login_required
def comments():
    if current_user.role.name != 'admin' and current_user.role.name != 'moderator':
        abort(403)
    page = request.args.get('page', 1, type=int)
    comments = Comments.query.order_by(Comments.publish==False, Comments.date_comment.desc()).paginate(page=page, per_page=10)
    return render_template('admin/comments.html', comments=comments)

@admin.route("/comments/<int:id>/unpublish")
@login_required
def publish_unpublish_comment(id):
    if current_user.role.name != 'admin' and current_user.role.name != 'moderator':
        abort(403)
    comment = Comments.query.get_or_404(id)
    if comment.publish:
        comment.publish = False
    else:
        comment.publish = True
    db.session.commit()
    flash('Komentar berhasil diupdate', 'is-success')
    return redirect(url_for('admin.comments'))

@admin.route("/comments/<int:id>/delete")
@login_required
def delete_comment(id):
    if current_user.role.name != 'admin' and current_user.role.name != 'moderator':
        abort(403)
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Komentar berhasil dihapus', 'is-success')
    return redirect(url_for('admin.comments'))
# end comment

# subscribers list
@admin.route("/subscribers")
@login_required
def list_subscribers():
    if current_user.role.name != 'admin' and current_user.role.name != 'moderator':
        abort(403)
    subscribers = Subscribers.query.order_by(Subscribers.date_posted.desc()).all()
    return render_template('admin/subscribers.html', subscribers=subscribers)
# end subscribers list