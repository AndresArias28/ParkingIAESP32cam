"""Prueba una foto de la ESP32-CAM contra el servidor local de inferencia."""

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera-url", default="http://192.168.4.1/capture")
    parser.add_argument("--server-url", default="http://127.0.0.1:5000/api/v1/predict")
    parser.add_argument("--camera", choices=("entrance-01", "exit-01"), default="entrance-01")
    args = parser.parse_args()
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(args.camera_url, timeout=15) as response:
            if response.headers.get_content_type() != "image/jpeg":
                raise ValueError("/capture no devolvió image/jpeg")
            image = response.read(5 * 1024 * 1024 + 1)
        if len(image) > 5 * 1024 * 1024 or not image:
            raise ValueError("La foto está vacía o supera 5 MB")
        separator = "&" if "?" in args.server_url else "?"
        url = f"{args.server_url}{separator}camera={args.camera}"
        request = Request(url, data=image, headers={"Content-Type": "image/jpeg"}, method="POST")
        with opener.open(request, timeout=30) as response:
            print(json.dumps(json.load(response), ensure_ascii=False, indent=2))
    except (HTTPError, URLError, OSError, ValueError) as exc:
        raise SystemExit(f"No se pudo clasificar la foto: {exc}") from exc


if __name__ == "__main__":
    main()
