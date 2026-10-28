# Captura del dataset — Fase 2B

Requiere Python 3 en el computador; no necesita instalar bibliotecas. El firmware se sigue cargando desde Arduino Cloud. La herramienta de captura se ejecuta localmente porque guarda archivos en este computador.

## Preparación

1. Alimentar la ESP32-CAM y pulsar brevemente RST si no aparece la red.
2. Esperar unos 20 segundos y conectar **este computador** a ParkingIA-Entrada; mantener conexión aunque no tenga Internet.
3. Comprobar http://192.168.4.1/capture en su navegador. Mantener cerrado el monitor serie de Cloud.
4. Abrir una terminal en D:\parqueaderoIA.

## Primera prueba

```powershell
py ml/training/capture_dataset.py --clase carro --cantidad 3
```

Antes de cada fotografía, colocar un carro y pulsar Enter. Variar posición o ángulo. Los JPEG se guardan en ml/dataset/carro/ con cámara, sesión y número consecutivo. Nunca se sobrescriben archivos existentes.

Repetir con `--clase moto` y `--clase vacio`. Vacío significa que no hay un vehículo válido: puede incluir sombras y reflejos del escenario real.

Para un lote automático, opcional:

```powershell
py ml/training/capture_dataset.py --clase carro --cantidad 10 --automatico --intervalo 3
```

Cambiar la escena entre fotos. Ctrl+C detiene la captura. La URL se puede cambiar con --url y la cámara con --camera exit-01 cuando exista la segunda cámara.

La herramienta comprueba tipo de respuesta, tamaño y marcadores JPEG; no valida enfoque ni decodifica la imagen. Abrir y revisar visualmente las fotos guardadas. Si falla una descarga, se detiene sin guardarla y conserva las anteriores.

## Criterio de salida

Guardar y abrir correctamente tres fotos de cada clase obtenidas de la cámara real. La comprobación local con un servidor simulado no sustituye esta prueba.

Después, fase 2C: reunir aproximadamente 200–300 imágenes útiles por clase, incluyendo ambas cámaras cuando estén disponibles. Conservar la sesión en los nombres para separar sesiones de entrenamiento y evaluación, evitando fotos casi iguales entre ambos grupos. Antes de reunir el dataset completo, fijar encuadre, enfoque, resolución y calidad.
