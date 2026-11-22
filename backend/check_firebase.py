"""Comprueba la conexión de lectura a Firebase RTDB sin modificar datos."""

from .app.firebase_repository import FirebaseRepository
from .app.local_config import load_local_env


def main():
    load_local_env()
    try:
        reference = FirebaseRepository().reference
        state = reference.child("parking/state").get()
        legacy_state = reference.child("estado").get()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"No se pudo configurar Firebase: {exc}") from exc
    except Exception as exc:
        raise SystemExit(
            f"No se pudo leer Firebase ({type(exc).__name__}). "
            "Revisa la credencial, la URL, Internet y los permisos del proyecto."
        ) from exc

    print("Conexión de lectura correcta.")
    print(f"parking/state: {'existe' if state is not None else 'no existe'}")
    print(f"estado: {'existe' if legacy_state is not None else 'no existe'}")


if __name__ == "__main__":
    main()
