# manage.py

from flask.cli import FlaskGroup
from project import create_app, db
from project.api.models import User
from dotenv import load_dotenv

# This is only to seed the database
from faker import Faker

fake = Faker()
Faker.seed(42)

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command('seed_db')
def seed_db():
    for _ in range(10):
        email = fake.ascii_free_email()
        username = email.split('@')[0]
        user = User(username=username, email=email)
        db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    load_dotenv()
    cli()
