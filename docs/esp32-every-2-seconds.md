# Prueba de clasificación automática cada 2 segundos

## Qué hace

`firmware/entrada/parking_entrada.ino` conecta la cámara de entrada al Wi-Fi del router en modo `WIFI_STA`, conserva `GET /capture` y envía un JPEG cada 2 segundos a `POST /api/v1/predict?camera=entrance-01`. El servidor Python clasifica como `car`, `motorcycle` o `empty`. Si se activa Firebase siguiendo `docs/firebase-and-flutter.md`, también procesa el conteo y Flutter lo visualiza.

El intervalo comienza al iniciar cada intento. Si una conexión tarda más de 2 segundos, los intentos serán más lentos; no se acumulan envíos pendientes. Sin conexión al router, la cámara omite los envíos y vuelve a intentar conectarse. Este sketch no crea la red directa `ParkingIA-Entrada`; el firmware anterior de captura del dataset sigue disponible por separado.

## Preparar el computador

1. Conectar el computador a la red de casa con Internet. La ESP32-CAM y el computador deben estar en la misma red local; usar una red de 2,4 GHz compatible con la cámara. Mantener el computador conectado a ella durante toda la prueba.
2. En PowerShell, ejecutar `ipconfig` y anotar la **Dirección IPv4** del adaptador conectado al router. Esa es la dirección que irá en `BACKEND_IP`; comprobarla de nuevo si el router la cambia. `0.0.0.0` es la dirección de escucha del servidor, no la dirección de destino de la cámara.
3. Desde `D:\parqueaderoIA`, iniciar el servidor:

```powershell
$env:PARKING_HOST = '0.0.0.0'
.\.venv\Scripts\python.exe -m backend.app.server
```

4. Abrir `http://IP_DEL_COMPUTADOR:5000/health` en el computador, sustituyendo `IP_DEL_COMPUTADOR` por la IPv4 obtenida. Debe responder con `status: ok` y `model: loaded`. Si Windows pregunta por acceso de red para Python, permitirlo en la red privada de casa. Para comprobar acceso desde otro dispositivo de la red, abrir la misma dirección allí. Esta ruta verifica que el modelo cargó, pero no la conexión a Firebase ni la calidad de las predicciones.

El servidor usa el puerto 5000 por defecto. Si se define `PARKING_PORT` con otro valor, usar ese mismo valor como `BACKEND_PORT` en la configuración local de la ESP32 y en las URL de prueba.

## Preparar Arduino Cloud

1. Crear un sketch nuevo con una sola pestaña `.ino` y pegar el contenido de `firmware/entrada/parking_entrada.ino`.
2. Crear una pestaña de encabezado llamada exactamente `secrets.h` y copiar `firmware/entrada/secrets.example.h`. Completar allí `ROUTER_SSID` y `ROUTER_PASSWORD` para la red de casa, `BACKEND_IP` con la IPv4 del computador y `BACKEND_PORT` con el puerto del servidor. Si se activa Firebase, definir también `CAMERA_TOKEN` con el mismo valor privado que `PARKING_CAMERA_TOKEN` en el servidor. No compartir ni versionar `secrets.h` ni capturas de esa pestaña.
3. Si se reutiliza un `secrets.h` anterior, quitar las declaraciones del punto de acceso (`AP_SSID` y `AP_PASSWORD`) y asegurarse de que existan `ROUTER_SSID`, `ROUTER_PASSWORD`, `BACKEND_IP`, `BACKEND_PORT` y `CAMERA_TOKEN`, sin duplicarlas. El archivo de ejemplo contiene valores vacíos para los datos privados; se completan solo en la copia local.
4. Seleccionar AI Thinker ESP32-CAM y cargar el sketch. Si es necesario, pulsar RST brevemente tras alimentar la placa. Buscar la IP de la ESP32 en la lista de clientes del router o en la salida serie si el monitor funciona de forma estable; cerrarlo antes de la prueba continua si interfiere con la cámara.
5. Desde el computador aún conectado al router, abrir `http://IP_DE_LA_ESP32/capture` y comprobar que devuelve un JPEG. La IP de la ESP32 es distinta de `BACKEND_IP`. Observar en la terminal del servidor predicciones de `entrance-01` aproximadamente cada 2 segundos; el firmware muestra la respuesta del servidor cuando recibe HTTP 200.

Si no hay predicciones, revisar la IP del computador, el puerto, el estado de conexión de la ESP32, el firewall de Windows y si el router aísla a sus clientes Wi-Fi. Un HTTP 200 con clase inesperada exige evaluar el modelo con fotografías nuevas.

## Alcance de la maqueta

Dejar un solo carro o una sola moto de juguete en el área visible y retirarlo para observar `empty`. El backend ya contiene transición Vacío → Vehículo, umbral, cooldown por cámara y límites de cupos; el conteo requiere Firebase y el token de cámara configurados. El cooldown reduce duplicados, pero no identifica vehículos individuales. La segunda cámara de salida y la prueba integral siguen pendientes.
