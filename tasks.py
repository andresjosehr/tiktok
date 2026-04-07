"""
Aliases locales del proyecto - usar con: inv <comando>

  inv server    Servidor web Django
  inv sim       Workers en modo simulador
  inv live      Workers + TikTok Live
  inv db        Levantar MySQL (Docker)
  inv init      Migrar + poblar datos iniciales
  inv -l        Listar todos los comandos
"""

import os
from invoke import task

os.environ['PYTHONIOENCODING'] = 'utf-8'


@task
def server(c):
    """Iniciar servidor web Django (accesible en LAN)"""
    c.run("python -X utf8 manage.py runserver 0.0.0.0:8000", pty=False)


@task
def sim(c):
    """Iniciar workers en modo simulador (sin TikTok, usar /simulator/)"""
    c.run("python -X utf8 manage.py start_event_system --simulator --verbose", pty=False)


@task
def live(c):
    """Iniciar sistema completo: workers + captura TikTok Live"""
    c.run("python -X utf8 manage.py start_event_system --verbose", pty=False)


@task
def db(c):
    """Levantar MySQL en Docker"""
    c.run("docker-compose up -d db")


@task
def init(c):
    """Migrar base de datos y poblar datos iniciales"""
    c.run("python manage.py migrate")
    c.run("python manage.py populate_initial_data")
