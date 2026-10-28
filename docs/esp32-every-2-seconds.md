# Prueba de clasificación automática cada 2 segundos

## Qué hace

`firmware/entrada/parking_entrada.ino` crea la red Wi-Fi de la cámara, conserva `GET /capture` para inspección y envía un JPEG cada 2 segundos a `POST /api/v1/predict?camera=entrance-01`. El servidor Python clasifica como `car`, `motorcycle` o `empty` y muestra el resultado en su terminal. La ESP32 no ejecuta el modelo y esta prueba no modifica Firebase ni la aplicación Flutter.

El intervalo comienza al iniciar cada intento. Si una conexión tarda más de 2 segundos, los intentos serán más lentos; no se acumulan envíos pendientes. La cámara no debe enviar dos capturas simultáneas.

## Preparar el computador

1. Conectar el computador a la red Wi-Fi `ParkingIA-Entrada` (o al SSID que se configure). Aceptar que no tiene Internet. Mantener cerrado el monitor serie de Arduino Cloud.
2. Abrir PowerShell y ejecutar `ipconfig`. Buscar el adaptador Wi-Fi conectado a esa red y anotar su **Dirección IPv4**. Suele ser `192.168.4.2`, pero debe verificarse; `192.168.4.1` es la cámara.
3. En `D:\parqueaderoIA`, iniciar el servidor para permitir conexiones desde la cámara:

```powershell
$env:PARKING_HOST = '0.0.0.0'
.\.venv\Scripts\python.exe -m backend.app.server
```

4. Si Windows pregunta por acceso de red para Python, permitirlo en la red privada de la maqueta. `http://127.0.0.1:5000/health` debe responder `{"model":"loaded","status":"ok"}` en el computador.

## Preparar Arduino Cloud

1. Crear un sketch nuevo con una sola pestaña `.ino` y pegar el contenido de `firmware/entrada/parking_entrada.ino`.
2. Crear una pestaña de encabezado llamada exactamente `secrets.h` y copiar el contenido de `firmware/entrada/secrets.example.h`.
3. En `secrets.h`, elegir una contraseña local de al menos 8 caracteres para `AP_PASSWORD`; escribir en `BACKEND_IP` la IPv4 del computador obtenida con `ipconfig`. Conservar este sketch privado y no compartir capturas de la pestaña de secretos.
4. Seleccionar AI Thinker ESP32-CAM y cargar el sketch. Como en las pruebas anteriores, mantener cerrado el monitor serie. Si la red no aparece tras conectar la alimentación, pulsar RST brevemente.
5. Conectar de nuevo el computador a la red de la cámara y arrancar el servidor si aún no está ejecutándose. La terminal del servidor debe mostrar `Predicción entrance-01: car`, `motorcycle` o `empty` aproximadamente cada 2 segundos.

Para comprobar la foto manual, abrir `http://192.168.4.1/capture`. Si no hay predicciones, revisar: IPv4 del computador, que el servidor esté escuchando en `0.0.0.0`, el firewall de Windows y que el computador siga conectado a la red de la cámara. Un resultado HTTP 200 con clase inesperada requiere revisar el modelo con fotografías nuevas.

## Alcance de la maqueta

Dejar un solo carro o una sola moto de juguete en el área visible, luego retirar el objeto para observar `empty`. El envío continuo clasifica **cada imagen**, pero no representa por sí solo un evento de entrada o salida. Para contar un vehículo una sola vez harán falta transición Vacío → Vehículo, reglas de umbral y cooldown, límites, cámara de salida y persistencia, que se implementarán en fases posteriores.
