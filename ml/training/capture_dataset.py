"""Captura manual o por lotes desde /capture; solo requiere Python estándar."""

import argparse
from datetime import datetime
from pathlib import Path
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener


DATASET = Path(__file__).resolve().parents[1] / "dataset"
MAX_BYTES = 5 * 1024 * 1024


def fetch_jpeg(url):
    # Acceso local directo: no enviar capturas mediante proxies del sistema.
    opener = build_opener(ProxyHandler({}))
    request = Request(url, headers={"Cache-Control": "no-cache"})
    with opener.open(request, timeout=15) as response:
        if response.headers.get_content_type() != "image/jpeg":
            raise ValueError("La cámara no devolvió image/jpeg.")
        data = response.read(MAX_BYTES + 1)
        expected = response.headers.get("Content-Length")
    if len(data) > MAX_BYTES:
        raise ValueError("La respuesta supera 5 MB.")
    if expected is not None and len(data) != int(expected):
        raise ValueError("La descarga está incompleta.")
    if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        raise ValueError("La respuesta no tiene los marcadores de un JPEG completo.")
    return data


def save_capture(data, folder, camera, session):
    folder.mkdir(parents=True, exist_ok=True)
    number = 1
    while True:
        path = folder / f"{camera}_{session}_{number:04d}.jpg"
        try:
            with path.open("xb") as output:
                try:
                    output.write(data)
                except BaseException:
                    path.unlink(missing_ok=True)
                    raise
            return path
        except FileExistsError:
            number += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://192.168.4.1/capture")
    parser.add_argument("--clase", choices=("carro", "moto", "vacio"))
    parser.add_argument("--camera", choices=("entrance-01", "exit-01"), default="entrance-01")
    parser.add_argument("--cantidad", type=int, default=1)
    parser.add_argument("--intervalo", type=float, default=3,
                        help="Segundos entre fotos en modo automático")
    parser.add_argument("--automatico", action="store_true",
                        help="No esperar Enter antes de cada foto")
    args = parser.parse_args()
    if args.cantidad < 1 or not 0 <= args.intervalo < float("inf"):
        parser.error("Cantidad debe ser positiva e intervalo finito no negativo.")

    clase = args.clase
    while clase not in ("carro", "moto", "vacio"):
        clase = input("Clase (carro / moto / vacio): ").strip().lower()

    folder = DATASET / clase
    session = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    print(f"Clase: {clase} | Cámara: {args.camera}")
    print(f"Destino: {folder}")
    print("Conecta este computador a ParkingIA-Entrada. Ctrl+C para terminar.")
    try:
        for index in range(args.cantidad):
            if not args.automatico:
                input(f"Prepara la escena {index + 1}/{args.cantidad} y pulsa Enter...")
            elif index:
                time.sleep(args.intervalo)
            data = fetch_jpeg(args.url)
            path = save_capture(data, folder, args.camera, session)
            print(f"Guardada: {path.name} ({len(data)} bytes)")
    except KeyboardInterrupt:
        print("\nCaptura detenida; se conservan las fotos guardadas.")
        return 130
    except (URLError, OSError, ValueError) as error:
        print(f"No se pudo completar la captura: {error}", file=sys.stderr)
        print("Comprueba el Wi-Fi y abre /capture en el navegador. "
              "Las fotos anteriores se conservan.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
