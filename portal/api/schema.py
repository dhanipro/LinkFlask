from portal import ma
from portal.models import Post, Kategori, Tag, Comments


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post

class KategoriSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Kategori

class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag

class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comments

class PostDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
    comments = ma.Nested(CommentSchema, many=True)