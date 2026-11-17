import os
from dotenv import load_dotenv

# Carrega o .env forçadamente antes de iniciar a aplicação
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, EmailLog

# CORREÇÃO AQUI: Chama create_app() sem argumentos para respeitar o seu __init__.py
app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, EmailLog=EmailLog)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)