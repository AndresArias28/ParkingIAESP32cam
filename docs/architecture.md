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

En fase 5 se añadirá el identificador de cámara: `?camera=entrance-01` o `?camera=exit-01`. El formato de carga y los errores se concretarán al implementar el endpoint. Ninguno de estos endpoints está implementado todavía.

## Identificadores y reglas

| Etiqueta | Identificador |
| --- | --- |
| Carro | car |
| Moto | motorcycle |
| Vacío | empty |
| Entrada | entrance-01, tipo entrance |
| Salida | exit-01, tipo exit |

Entrada aceptada suma uno; salida aceptada resta uno, por tipo. Vacío y confianza inferior a 0.85 no modifican ocupación. Debe cumplirse siempre `0 <= occupied <= capacity` y `available = capacity - occupied`.

El cooldown inicial será de 2500 ms por cámara, medido entre eventos aceptados. Las decisiones rechazadas no deben reiniciarlo. El conteo concurrente de ambas cámaras requerirá una transacción o mecanismo equivalente para evitar actualizaciones perdidas. Estado y evento aceptado deben conservar coherencia ante reintentos; la estrategia de idempotencia se definirá en la integración.

## Datos previstos en Firebase

`config/parking.example.json` contiene el esquema inicial: config, state, cameras y events. Las cámaras comienzan con online=false: el ejemplo no implica conexión real. La detección de conexión requerirá un mecanismo de último contacto y caducidad que se definirá en la integración.

Ejemplo de evento aceptado:

```json
{"camera": "entrance-01", "type": "car", "action": "in", "confidence": 0.96, "timestamp": 0}
```

El timestamp 0 es ilustrativo; en producción representará tiempo del servidor en milisegundos Unix. La acción de salida será out.

## Aplicación recuperada

Actualmente movil_app/lib/parking_station.dart consulta `estado` con campos dispCarro, dispMoto, ocupadosCarro y ocupadosMoto. El esquema nuevo usa state/occupied y state/available. Esta diferencia se resolverá en fase 8; la app actual no es todavía compatible con el contrato propuesto. No se modifica la base Firebase existente durante la fase 1.
