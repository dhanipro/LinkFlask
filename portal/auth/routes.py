import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from portal import db, bcrypt, mail
from portal.models import User
from .forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user
from .utils import send_reset_email

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Akun berhasil dibuat! Silahkan Login', 'is-success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.admin_index'))
        else:
            flash('Login Gagal. Cek email dan password Anda', 'is-danger')
    return render_template('auth/login.html', title='Login', form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('posts.home'))

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Kami telah mengirimkan email intruksi untuk mengganti password. Silahkan cek email Anda', 'is-info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password Anda telah diupdate! silahkan login', 'is-success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)