import os
import sys

from flask import Flask, render_template, request, flash, redirect

from flaskr.db import get_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/database')
    def database():
        db = get_db()
        texts = db.execute('SELECT * FROM text').fetchall()
        return render_template('database.html', texts=texts)

    @app.route('/search')
    def search():
        query = request.args['q']
        query = '%' + query + '%'
        db = get_db()
        texts = db.execute('SELECT * FROM text WHERE art LIKE ? OR subtype LIKE ? or title LIKE ?', 
            (query, query, query)).fetchall()
        return render_template('database.html', texts=texts)

    @app.route('/text/<int:id>')
    def get_text(id):
        db = get_db()
        text = db.execute('SELECT * FROM text WHERE id = ?', (id,)).fetchall()
        return render_template('text.html', text=text[0])

    @app.route('/modify')
    def modify():
        return render_template('modify.html')

    @app.route('/create', methods=['GET', 'POST'])
    def create():
        if request.method == 'POST':
            art = request.form['art']
            subtype = request.form['subtype']
            title = request.form['title']
            link = request.form['link']
            
            error = None
            print(art, file=sys.stderr)
            if art == '':
                error = 'Art is required'
            if title == '':
                error = 'Title is required'
            
            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO text (art, subtype, title, link)'
                    ' VALUES (?, ?, ?, ?)',
                    (art, subtype, title, link)
                )
                db.commit()

        return render_template('modify.html')

    @app.route('/text/<int:id>/delete', methods=['POST'])
    def delete_text(id):
        if request.method == 'POST':
            db = get_db()
            db.execute('DELETE FROM text WHERE id = ?', (id,))
            db.commit()
        return redirect('/database')
    
    @app.route('/text/<int:id>/update', methods=['POST'])
    def update_text(id):
        if request.method == 'POST':
            art = request.form['art']
            subtype = request.form['subtype']
            title = request.form['title']
            link = request.form['link']
            db = get_db()
            db.execute('UPDATE text SET title = ?, art = ?, subtype = ?, link = ? WHERE id = ?', 
                (title, art, subtype, link, id))
            db.commit()
        return redirect('/database')

    @app.route('/about')
    def about():
        return render_template('about.html')

    from . import db
    db.init_app(app)

    return app
