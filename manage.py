import os
import sys

import alembic.config
import click
import pytest
import uvicorn

from app.config import settings
from app import get_application
from app.database import get_local_session
from app.models.user import User


@click.group()
def cli():
    pass


@cli.command(short_help="Run application tests")
def test():
    os.environ['APP_CONFIG'] = 'testing'
    pytest.main([os.getcwd()])


@cli.command(short_help="Upgrade database using alembic")
def upgrade():
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembic_args)


@cli.command(short_help="Add new alembic revision")
@click.argument('name')
def revision(name):
    # TODO: FIX BROKEN ARGUMENT
    alembic_args = [
        '--raiseerr',
        'revision', '--autogenerate', name,
    ]
    alembic.config.main(argv=alembic_args)


@cli.command(short_help="Run a uvicorn server")
def runserver():
    os.environ['APP_CONFIG'] = 'development'
    log_level = "debug" if settings.DEBUG else "info"
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, log_level=log_level, reload=settings.DEBUG)


@cli.command(short_help="Create superuser for testing purposes")
def superuser():
    session = get_local_session()
    user = User(username='admin', email='admin@admin.com', name='admin')
    user.is_superuser = True
    user.is_active = True
    user.set_password('admin1234')
    session.add(user)
    session.commit()


@cli.command(short_help="Run a shell in the app context.")
def shell() -> None:
    import code

    current_app = get_application()
    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        f"App: {settings.TITLE}\n"
        f"Instance: {os.getcwd()}"
    )
    db = get_local_session()
    ctx: dict = {'app': current_app, 'db': db}
    code.interact(banner=banner, local=ctx)


if __name__ == '__main__':
    cli()
