# Servidor Python — Fase 4

El servidor clasifica una imagen como `car`, `motorcycle` o `empty` y devuelve la confianza. Con Firebase habilitado, aplica el conteo y escribe en Realtime Database. La configuración está en `docs/firebase-and-flutter.md`.

## 1. Copiar el modelo

En Teachable Machine: Exportar modelo → **TensorFlow** → **Keras** → **Descargar**. Descomprimir el archivo y copiar `keras_model.h5` y `labels.txt` a `D:\parqueaderoIA\ml\model\`. No renombrar los archivos. `labels.txt` debe contener exactamente Carro, Moto y Vacío (el orden puede variar). El modelo y el dataset están excluidos de Git.

## 2. Instalar Python y bibliotecas

En PowerShell, desde `D:\parqueaderoIA`:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Python 3.12 está disponible en este computador. La primera instalación de TensorFlow puede tardar y requiere conexión a Internet. En Windows se utiliza la CPU.

## 3. Iniciar

El servidor carga el archivo local `D:\parqueaderoIA\.env` si existe. Para la conexión persistente con Firebase, completar primero `PARKING_CAMERA_TOKEN` como explica `docs/firebase-and-flutter.md`. Desde una terminal nueva en la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m backend.app.server
```

Esperar `Servidor listo en 0.0.0.0:5000` y `Conteo Firebase: activado` con la configuración local. Mantener abierta esa terminal. Si falta el modelo o las etiquetas, el servidor indicará el problema y se detendrá. `GET http://127.0.0.1:5000/health` devuelve estado y modelo cargado.

## 4. Enviar una foto local

En otra terminal, desde la misma carpeta:

```powershell
$foto = (Get-ChildItem ml\dataset\carro -Filter *.jpg | Select-Object -First 1).FullName
curl.exe -X POST -F "image=@$foto" "http://127.0.0.1:5000/api/v1/predict"
```

Respuesta esperada: `{"prediction":"car","confidence":0.9432}`. La clase y confianza reales dependen del modelo y la foto. Esta prueba sin cámara identificada solo clasifica y no altera cupos. También acepta un cuerpo JPEG directo con `Content-Type: image/jpeg`, como el que envía la ESP32.

Usar primero imágenes nuevas, que no se hayan usado en entrenamiento. Una predicción correcta sobre las mismas fotos de entrenamiento no valida la precisión. Si el modelo aprendió etiquetas incorrectas, se debe volver a entrenar con datos corregidos.

## 5. Probar una foto actual de la ESP32-CAM

Para probar el firmware anterior de captura del dataset, con el computador conectado a `ParkingIA-Entrada`, el servidor ejecutándose y el monitor serie cerrado:

```powershell
.\.venv\Scripts\python.exe -m backend.camera_client
```

El cliente consulta `http://192.168.4.1/capture` y envía esa foto al servidor local. El resultado aparece en la terminal. Esta prueba clasifica una sola foto. Con Firebase habilitado, puede actualizar cupos si el cliente envía el token de cámara. Para repetirla, ejecutar otra vez el comando. Para el firmware nuevo conectado al router, seguir `docs/esp32-every-2-seconds.md` y mantener el computador en la red de casa; este cliente también acepta `--camera-url http://IP_DE_LA_ESP32/capture`.

## Alcance actual

Por defecto el servidor escucha solo en este computador (`127.0.0.1`). Para que la ESP32 lo alcance, poner ambos en una red accesible y usar `PARKING_HOST=0.0.0.0`. La ruta `/health` confirma carga del modelo, no calidad de clasificación ni conexión a Firebase. Para comprobar Firebase, ejecutar `python -m backend.check_firebase` según `docs/firebase-and-flutter.md`.
