# Servidor Python — Fase 4

El servidor clasifica una imagen como `car`, `motorcycle` o `empty` y devuelve la confianza. No modifica contadores ni Firebase; esas funciones corresponden a la fase 6.

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

```powershell
.\.venv\Scripts\python.exe -m backend.app.server
```

Esperar `Servidor listo en http://127.0.0.1:5000`. Mantener abierta esa terminal. Si falta el modelo o las etiquetas, el servidor indicará el problema y se detendrá. `GET http://127.0.0.1:5000/health` devuelve estado y modelo cargado.

## 4. Enviar una foto local

En otra terminal, desde la misma carpeta:

```powershell
$foto = (Get-ChildItem ml\dataset\carro -Filter *.jpg | Select-Object -First 1).FullName
curl.exe -X POST -F "image=@$foto" "http://127.0.0.1:5000/api/v1/predict?camera=entrance-01"
```

Respuesta esperada: `{"camera":"entrance-01","prediction":"car","confidence":0.9432}`. La clase y confianza reales dependen del modelo y la foto. También acepta un cuerpo JPEG directo con `Content-Type: image/jpeg`, pensado para la integración futura con la ESP32.

Usar primero imágenes nuevas, que no se hayan usado en entrenamiento. Una predicción correcta sobre las mismas fotos de entrenamiento no valida la precisión. Si el modelo aprendió etiquetas incorrectas, se debe volver a entrenar con datos corregidos.

## 5. Probar una foto actual de la ESP32-CAM

Con el servidor ejecutándose, este computador conectado a `ParkingIA-Entrada` y el monitor serie cerrado:

```powershell
.\.venv\Scripts\python.exe -m backend.camera_client
```

El cliente consulta `http://192.168.4.1/capture` y envía esa foto al servidor local. El resultado aparece en la terminal. No se requiere cambiar todavía el firmware de la ESP32. Esta prueba clasifica una sola foto y no actualiza cupos. Para repetirla, ejecutar otra vez el comando.

## Alcance actual

El servidor escucha solo en este computador (`127.0.0.1`). Para que la ESP32 lo alcance habrá que poner ambos en una red accesible y configurar la dirección de escucha en fase 5. La ruta `/health` confirma carga del modelo, no calidad de clasificación. La fase 6 implementará reglas, cooldown y Firebase de forma separada.
