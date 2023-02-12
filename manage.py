import os

import alembic.config
import click
import pytest
import uvicorn

from app.config import settings


@click.group()
def cli():
    pass


@cli.command()
def test():
    pytest.main([os.getcwd()])


@cli.command()
def upgrade():
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembic_args)


@cli.command()
@click.argument('name')
def revision(name):
    alembic_args = [
        '--raiseerr',
        'revision', '--autogenerate', name,
    ]
    alembic.config.main(argv=alembic_args)


@cli.command()
def runserver():
    log_level = "debug" if settings.DEBUG else "info"
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, log_level=log_level, reload=settings.DEBUG)


if __name__ == '__main__':
    cli()
