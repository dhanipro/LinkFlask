from flask import Blueprint, request, jsonify
from portal.models import Post, Kategori, Tag
from .schema import PostSchema, PostDetailSchema, KategoriSchema, TagSchema

api = Blueprint('api', __name__, url_prefix='/api')

@api.route("/home")
def api_home():
    page = request.args.get('page', 1, type=int)
    auth = request.args.get("key")
    if auth == 'randomstring':
        posts = Post.query.filter_by(publish=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
        post_schema = PostSchema(many=True)
        result = post_schema.dump(posts.items)
        return jsonify(result)
    else:
        return jsonify({'message': 'Invalid'})

@api.route("/detail/<int:id>")
def api_detail_post(id):
    page = request.args.get('page', 1, type=int)
    auth = request.args.get("key")
    if auth == 'randomstring':
        post = Post.query.get(id)
        post_schema = PostDetailSchema()
        result = post_schema.dump(post)
        return jsonify(result)
    else:
        return jsonify({'message': 'Invalid'})

@api.route("/kategori")
def api_kategori():
    page = request.args.get('page', 1, type=int)
    auth = request.args.get("key")
    if auth == 'randomstring':
        kategori = Kategori.query.all()
        kategori_schema = KategoriSchema(many=True)
        result = kategori_schema.dump(kategori)
        return jsonify(result)
    else:
        return jsonify({'message': 'Invalid'})

@api.route("/tag")
def api_tag():
    page = request.args.get('page', 1, type=int)
    auth = request.args.get("key")
    if auth == 'randomstring':
        tags = Tag.query.all()
        tag_schema = TagSchema(many=True)
        result = tag_schema.dump(tags)
        return jsonify(result)
    else:
        return jsonify({'message': 'Invalid'})