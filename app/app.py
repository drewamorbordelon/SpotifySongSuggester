import json
import sqlite3
import os
import pandas as pd

from flask import Flask, render_template, request, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from os import getenv



# def create_app():
#     app = Flask(__name__)

#     Bootstrap(app)
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     DB = SQLAlchemy(app)
#     DB.init_app(app)
#     app.config['SECRET_KEY'] = '<SECRET_KEY>'
#     csrf = CSRFProtect(app)

#     @app.route('/', methods=['GET'])
#     def dropdown():

#         return render_template('base.html')

    
#     @app.route('/predict', methods=['GET', 'POST'])
#     def home():
#         template = render_template('predict.html', title="Branching out on your music quest")
#         songs = render_10(request.values['Searched_Song'])

DB_FILE = 'data/db.sqlite3'


def create_app():
    """Create and configure an instance of Flask application"""
    app = Flask(__name__)

    Bootstrap(app)
    CORS(app)
    
    def create_connection(db_file, verbose=False):
        """
        Create a database connection to SQLite database

        Parameter
        ---------
        df_file: str
                    database file path
        verbose: bool
                    prints details of the connection to database

        Returns
        -------
        conn: sqlite3.connection
                    returns sqlite3 connection object
        """
        # Check if db_file path is valid
        if not os.path.isfile(db_file):
            raise IOError(f'Invalid database filepath: {db_file}')

        conn = None
        try:
            conn = sqlite3.connect(db_file)
            if verbose:
                print(f'Using SQLite version: {sqlite3.version}')
                print(f'Creating connection to {db_file} ....')
            return conn
        except sqlite3.Error as e:
            print(e)

    def select_query(conn, query, verbose=False):
        """
        Queries and returns results from the database as a Pandas DataFrame

        Parameter
        ---------
        conn: sqlite3.connection
                    returns sqlite3 connection object
        query: str
                    SQL SELECT query
        verbose: bool
                    prints details of the connection to the database
        
        Returns
        -------
        results: DataFrame
                    returns results as Pandas DataFrame
        """     
        if not query.startswith('SELECT'):
            raise ValueError('Query should begin with `SELECT`')
        
        df = pd.read_sql(query, conn)

        if verbose:
            print(df.head())
        return df

    @app.route('/')
    def index():
        return "Spotify Song Recommender API is working"

    @app.routes('/api', method=['POST'])
    def api():

        data_in = request.get_json(force=True)

        try:
            # Create database connection
            conn = create_connection(DB_FILE, verbose=True)

            try:
                # Get track id of searched song
                track_id = data_in["Searched_Song"]
            except Exception as e:
                return f"Index Error for: {data_in}"
            
            # Find similar songs
            query = "SELECT * FROM recommendations WHERE Searched_Song == '{}'".format(
                track_id)

            similar_songs = select_query(conn, query)
            similar_songs_dict = similar_songs.to_dict(orient='records')[0]

            return jsonify(similar_songs_dict)

        except Exception as e:
            print(e)
            return f"Can't find the track id of Searched_Song {data_in}"

    return app