from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, ValidationError
from wtforms.fields.html5 import EmailField
from portal.models import Subscribers

class SubscribersForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Alamat Anda Email"})
    submit = SubmitField('Berlangganan')

    def validate_email(self, email):
        subscriber = Subscribers.query.filter_by(email=email.data).first()
        if subscriber:
            raise ValidationError('Email sudah pernah didaftarkan, cek email Anda')

class CommentForm(FlaskForm):
    nama = StringField('Nama',
                           validators=[DataRequired(), Length(min=3)], render_kw={'placeholder': 'Nama'})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    website = StringField('Website', render_kw={'placeholder': 'http://www.example.com'})
    comment = TextAreaField('Komentar', validators=[DataRequired()], render_kw={'placeholder': 'Tinggalkan komentar'})
    submit = SubmitField('Submit')

class ReplyForm(FlaskForm):
    nama = StringField('Nama',
                           validators=[DataRequired(), Length(min=3)], render_kw={'placeholder': 'Nama'})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    website = StringField('Website', render_kw={'placeholder': 'http://www.example.com'})
    comment = TextAreaField('Komentar', validators=[DataRequired()], render_kw={'placeholder': 'Tinggalkan komentar'})
    submit = SubmitField('Submit')

class HubungiForm(FlaskForm):
    nama = StringField('Nama',
                           validators=[DataRequired(), Length(min=3)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    pesan = TextAreaField('Pesan', validators=[DataRequired()])
    submit = SubmitField('Submit')