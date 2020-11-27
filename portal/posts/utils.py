from .forms import SubscribersForm
from portal.models import Kategori, Tag, Post, Page
import datetime

def utils_context():
    form = SubscribersForm()
    blog_name = 'LinkFlask'
    kategori = Kategori.query.all()
    topik = Tag.query.all()
    populer = Post.query.filter_by(publish = True).order_by(Post.dibaca.desc()).limit(5).all()
    pages = Page.query.filter_by(publish=True).all()
    return dict(now=datetime.date.today().year, kategori=kategori, topik=topik, populer=populer, pages=pages, blog_name=blog_name, form=form)