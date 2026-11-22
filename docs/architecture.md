# Arquitectura prevista

## Componentes

| Componente | Responsabilidad |
| --- | --- |
| ESP32-CAM entrada/salida | Capturar JPEG e identificar la cámara emisora |
| ImageClassifier | Preprocesar la imagen según el modelo y devolver clase y confianza |
| ParkingService | Validar cámara, umbral, cooldown y límites; decidir el cambio |
| FirebaseRepository | Persistir estado y eventos de forma consistente |
| Firebase RTDB | Almacenar configuración, estado, cámaras y eventos |
| Flutter | Suscribirse al estado y mostrar cupos y eventos |

Flujo: cámara → backend → clasificador → servicio de conteo → repositorio → Firebase → Flutter.

## Contratos previstos

Durante la captura del dataset, cada ESP32 expondrá temporalmente `GET /capture`, con respuesta JPEG. Configuración inicial a evaluar: VGA 640×480, calidad JPEG 12 y un framebuffer; se fijará tras validar las imágenes.

En fase 4, `POST /api/v1/predict` clasificará una imagen local y devolverá, por ejemplo:

```json
{"prediction": "car", "confidence": 0.9432}
```

El endpoint acepta JPEG directo o archivo multipart `image`, y el identificador `?camera=entrance-01` o `?camera=exit-01`. Con `PARKING_FIREBASE_ENABLED=1`, credenciales de servidor y `PARKING_CAMERA_TOKEN` configurados, exige el encabezado `X-Camera-Token`, procesa el conteo y devuelve `counted`, `reason`, `occupied` y `available`.

## Identificadores y reglas

| Etiqueta | Identificador |
| --- | --- |
| Carro | car |
| Moto | motorcycle |
| Vacío | empty |
| Entrada | entrance-01, tipo entrance |
| Salida | exit-01, tipo exit |

Entrada aceptada suma uno; salida aceptada resta uno, por tipo. Vacío y confianza inferior a 0.85 no modifican ocupación. Debe cumplirse siempre `0 <= occupied <= capacity` y `available = capacity - occupied`.

El cooldown inicial es de 2500 ms por cámara, medido entre eventos aceptados. El detector se desarma tras detectar un vehículo y exige dos predicciones `empty` consecutivas, con confianza suficiente, antes de volver a contar. Un vehículo rechazado por cooldown o capacidad también desarma el detector hasta que la escena se vacíe. Las decisiones rechazadas no reinician el cooldown. La transacción de Firebase abarca la raíz para actualizar juntos `estado` y `parking` sin que dos cámaras pisen el contador de la otra. El estado del detector queda en `parking/cameras` para resistir reinicios del proceso Python. Una clasificación errónea de Vacío dos veces puede rearmarlo; se debe validar en la maqueta.

## Datos previstos en Firebase

`config/parking.example.json` contiene el esquema inicial bajo el nodo `parking`: config, state, cameras y events. La base existente usa además `config` y `estado` en la raíz. `FirebaseRepository` toma de allí capacidad, umbral, cooldown y ocupación; tras cada observación sincroniza `estado` y `parking` en una sola transacción. Conserva los demás nodos y campos. Las cámaras comienzan con online=false: el ejemplo no implica conexión real. Cada observación actualiza `lastSeenMs`; el cálculo de desconexión por caducidad queda pendiente.

Ejemplo de evento aceptado:

```json
{"camera": "entrance-01", "type": "car", "action": "in", "confidence": 0.96, "timestamp": 0}
```

El timestamp 0 es ilustrativo; en producción representará tiempo del servidor en milisegundos Unix. La acción de salida será out.

## Aplicación recuperada

El código Flutter actual escucha `parking` y muestra `state/occupied`, `state/available` y los últimos eventos. La versión anterior escucha `estado`; ambos nodos se mantienen sincronizados para que las dos versiones reciban cambios. La prueba de escritura con Firebase real requiere cámara, credenciales de servidor y conexión a Internet.
