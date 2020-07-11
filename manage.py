# manage.py
from flask.cli import FlaskGroup
from project import app
from dotenv import load_dotenv

cli = FlaskGroup(app)

if __name__ == '__main__':
    load_dotenv()
    cli()
