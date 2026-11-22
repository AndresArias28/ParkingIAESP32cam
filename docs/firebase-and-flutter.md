# Conteo en Firebase y visualización Flutter

## Estado del código

El servidor aplica una transición de escena vacía a vehículo una sola vez por cámara. Para habilitar otro paso exige dos fotos vacías consecutivas. Usa el umbral y cooldown configurados en Firebase; si faltan, usa 0.85 y 2500 ms. Una transacción sincroniza `estado` y `parking`. El código Flutter actual escucha `parking`; la versión anterior escucha `estado`.

La base existente tiene `config` y `estado` en la raíz. En la captura proporcionada, la capacidad era de 100 carros y 200 motos, con 10 carros ocupados y 0 motos ocupadas. El servidor toma esos valores como punto de partida; no reinicia el conteo a 0 ni usa la capacidad de ejemplo 5/5 mientras esos campos existan. El usuario confirmó que la cámara ya envía predicciones y que el conteo actualiza Firebase; el modelo todavía debe comprobarse con los juguetes y la iluminación definitivos antes de confiar en los cupos.

## Conectar Firebase

1. En la consola de Firebase del proyecto ya usado por Flutter, abrir **Configuración del proyecto → Cuentas de servicio → Generar nueva clave privada**. Guardar el JSON en `D:\parqueaderoIA\backend\serviceAccountKey.json`. Ese nombre está excluido de Git. No subirlo a Arduino Cloud ni compartirlo en el chat.
2. Confirmar que la URL de Realtime Database sea la misma que usa la app. El backend carga `D:\parqueaderoIA\.env` al arrancar; ese archivo local está excluido de Git. Allí se guardan `GOOGLE_APPLICATION_CREDENTIALS`, `FIREBASE_DATABASE_URL`, `PARKING_FIREBASE_ENABLED`, `PARKING_HOST`, `PARKING_PORT` y `PARKING_CAMERA_TOKEN`. Los valores no privados ya están preparados en el archivo local. Completar `PARKING_CAMERA_TOKEN` allí con un valor privado nuevo y poner ese mismo valor en `CAMERA_TOKEN` de la cámara; después volver a cargar el sketch. El valor compartido en el chat debe reemplazarse; no copiarlo al repositorio ni volver a publicarlo. Para evitar que las variables de una sesión anterior tengan prioridad sobre `.env`, abrir una ventana nueva de PowerShell después de editarlo.

Desde `D:\parqueaderoIA`, comprobar la lectura de Firebase y luego iniciar el servidor:

```powershell
.\.venv\Scripts\python.exe -m backend.check_firebase
.\.venv\Scripts\python.exe -m backend.app.server
```

La primera orden solo lee `parking/state` y `estado`: no crea nodos ni modifica cupos. La URL debe coincidir con la configurada en `movil_app/lib/parking_station.dart`; la cuenta de servicio debe pertenecer al mismo proyecto Firebase. Las variables que se definan manualmente en PowerShell tienen prioridad sobre `.env`. Si aparece `Falta FIREBASE_DATABASE_URL`, revisar el archivo local y ejecutar desde la raíz del proyecto.

Al arrancar debe aparecer `Conteo Firebase: activado`. Cada foto procesada mostrará `Conteo entrance-01: sí (accepted)` o una razón como `empty`, `low_confidence`, `already_seen`, `cooldown` o `capacity_limit`. Si aparece `Conteo Firebase: desactivado`, las peticiones pueden clasificar correctamente, pero no escribirán en Realtime Database. En ese caso, detener el servidor y reiniciarlo con todas las variables anteriores en la misma terminal.

3. Conectar el computador y la ESP32-CAM de entrada al mismo router con Internet, usando una red de 2,4 GHz compatible con la cámara. El firmware de entrada usa `WIFI_STA`; seguir `docs/esp32-every-2-seconds.md` para cargarlo. Obtener con `ipconfig` la IPv4 del computador en esa red y escribirla como `BACKEND_IP` solo en el `secrets.h` privado de Arduino Cloud. El puerto `BACKEND_PORT` debe coincidir con `PARKING_PORT` (5000 por defecto). `PARKING_HOST=0.0.0.0` permite recibir conexiones, pero no es la dirección que debe usar la ESP32. Escribir el mismo valor privado en `CAMERA_TOKEN` y `PARKING_CAMERA_TOKEN`; no compartirlo ni guardarlo en Git.
4. Antes de probar el conteo, abrir `http://IP_DEL_COMPUTADOR:5000/health` desde la red local (ajustando el puerto si se configuró otro), comprobar `http://IP_DE_LA_ESP32/capture` y observar predicciones `entrance-01` con HTTP 200 en el servidor. Si no llegan, revisar IP, puerto, firewall y aislamiento de clientes del router. El computador debe seguir conectado al router para que Python pueda actualizar Firebase.
5. Ejecutar Flutter con su configuración Firebase existente. Solo después de confirmar la llegada de imágenes, probar el conteo y verificar por separado la escritura en Firebase y la lectura en Flutter. El nodo `parking` aparecerá después de la primera foto procesada con el conteo activado; `estado` se mantendrá sincronizado para la versión anterior de la app.

## Probar con la maqueta

1. Mostrar Vacío durante dos capturas y verificar que el contador no cambie.
2. Mostrar un carro de juguete durante al menos dos capturas: debe sumar **una sola vez** aunque permanezca frente a la cámara.
3. Retirar el carro durante dos capturas vacías. Volver a mostrarlo: debe sumar una vez más, salvo que el cooldown o la capacidad lo impidan.
4. Repetir con moto. Con `exit-01`, las mismas transiciones restan, nunca por debajo de cero.

Las respuestas del endpoint incluyen `counted` y `reason`. `already_seen` indica que el vehículo sigue presente; `capacity_limit` indica lleno o cero; `cooldown` indica que pasó demasiado pronto. Las predicciones `empty` y las de confianza baja no crean eventos.

El permiso de lectura de Firebase para la app debe estar configurado en las reglas de Realtime Database. Este trabajo no cambia las reglas. El servidor usa credenciales administrativas locales y debe permanecer en una red de confianza.
