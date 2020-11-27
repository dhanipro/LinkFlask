from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from portal.models import User, tag_loader, select2
from flask_select2.model.fields import AjaxSelectField, AjaxSelectMultipleField

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', render_kw={'disabled':True})
    role = SelectField('Role', validators=[DataRequired()], choices = [])
    biografi = TextAreaField('Biografi')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    active = BooleanField('Active')
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data:
            raise ValidationError('Email tidak dapat diganti')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    kategori = SelectField('Kategori', validators=[DataRequired()], choices = [])
    content = CKEditorField('Content', validators=[DataRequired()])
    thumbnail = FileField('Gambar Thumbnail', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    is_headline = BooleanField('Headline', default=False)
    multiple_company = AjaxSelectMultipleField(
        loader=tag_loader,
        label='Masukkan Tags',
        allow_blank=False
    )
    submit = SubmitField('Post')

class HalamanForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    is_active = BooleanField('Tayangkan', default=True)
    submit = SubmitField('Post')

class KategoriForm(FlaskForm):
    nama = StringField('Nama kategori', validators=[DataRequired()])
    is_gutters = BooleanField('Jadikan Gutters', default=False)
    submit = SubmitField('Submit')

    def validate_nama(form, field):
        if len(field.data) < 3:
            raise ValidationError('Nama harus lebih dari 3 huruf')

class TagForm(FlaskForm):
    nama = StringField('Nama Tag', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RoleForm(FlaskForm):
    nama = StringField('Nama Role', validators=[DataRequired()])
    submit = SubmitField('Submit')