# -*- coding: utf-8 -*-
import os
import uuid
import markdown
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flask import send_from_directory
from flask_demo.auth import login_required
from flask_demo.db import get_db

bp = Blueprint('blog', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMAGE_FOLDER = bp.root_path + '/../images/'

try:
    os.makedirs(IMAGE_FOLDER)
except OSError:
    pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    summary = {post['id']: post['body'][:100] if len(post['body']) > 100 else post['body'] for post in posts}
    pages = [{
        'name': '上一页',
        'page': '1',
        'link': '/1'
    },
        {
        'name': '2',
        'link': '/2'
    },
        {
            'name': '下一页',
            'link': '/3'
    },
    ]
    return render_template('blog/index.html', posts=posts, summary=summary, pages=pages)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
            return redirect(request.url)
        filename_uuid = ''
        # if 'image' not in request.files:
        #     flash('No file part')
        #     return redirect(request.url)
        # image = request.files['image']
        # image_uuid = uuid.uuid4()
        # if image.filename == '':
        #     flash('No selected file')
        #     return redirect(request.url)
        # if not image or not allowed_file(image.filename):
        #     flash('No selected file')
        #     return redirect(request.url)
        # filename_uuid = ''.join([str(image_uuid), '.', image.filename.rsplit('.', 1)[1]])
        # image.save(os.path.join(IMAGE_FOLDER, filename_uuid))
        db = get_db()
        db.execute(
            'INSERT INTO post (title, body, author_id, filename_uuid)'
            ' VALUES (?, ?, ?, ?)',
            (title, body, g.user['id'], filename_uuid)
        )
        data_id = db.execute('SELECT LAST_INSERT_ROWID();').lastrowid
        db.commit()
        return show(data_id)

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, filename_uuid, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            filename_uuid = ''
            # if 'image' not in request.files:
            #     flash('No file part')
            #     return redirect(request.url)
            # image = request.files['image']
            # image_uuid = uuid.uuid4()
            # if image.filename == '':
            #     flash('No selected file')
            #     return redirect(request.url)
            # if not image or not allowed_file(image.filename):
            #     flash('No selected file')
            #     return redirect(request.url)
            # filename_uuid = ''.join([str(image_uuid), '.', image.filename.rsplit('.', 1)[1]])
            # image.save(os.path.join(IMAGE_FOLDER, filename_uuid))
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, filename_uuid = ?'
                ' WHERE id = ?',
                (title, body, filename_uuid, id)
            )
            db.commit()
            return redirect(url_for('blog.show', id=id))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/show', methods=('GET',))
def show(id):
    post = get_post(id, check_author=False)
    if not post:
        return redirect(url_for('blog.index'))
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    markdown_body = markdown.markdown(post['body'], extensions=exts) if post['body'] else ''
    template = render_template('/blog/show.html', post=post, markdown_body=markdown_body)
    return template.replace('markdown_body', markdown_body)


@bp.route('/image/<filename>')
def uploaded_file(filename):
    return send_from_directory(IMAGE_FOLDER, filename)
