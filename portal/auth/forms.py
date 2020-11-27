from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from portal.models import User, tag_loader, select2
from flask_select2.model.fields import AjaxSelectField, AjaxSelectMultipleField


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'Nama'})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={'placeholder': 'ConfirmPassword'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah ada yang mendaftar. Silahkan pilih yang lain')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email belum pernah didaftarkan. Anda dapat registrasi dengan email tersebut.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password baru'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(message='Tidak boleh kosong'), EqualTo('password', message='Harus sama dengan field diatas')], render_kw={'placeholder': 'Ulangi password baru'})
    submit = SubmitField('Reset Password')