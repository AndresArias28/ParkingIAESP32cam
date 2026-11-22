"""Carga la configuración local excluida de Git antes de iniciar el backend."""

from pathlib import Path

from dotenv import load_dotenv


ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


def load_local_env():
    # Las variables definidas en la terminal tienen prioridad sobre .env.
    load_dotenv(dotenv_path=ROOT_ENV, override=False)
