# Requisitos del MVP

## Funcionales

| ID | Requisito | Validación prevista |
| --- | --- | --- |
| RF-01 | Capturar JPEG válidos con ESP32-CAM | Descargar imágenes repetidamente desde /capture |
| RF-02 | Clasificar Carro, Moto o Vacío y devolver confianza | Evaluar imágenes nuevas de las tres clases |
| RF-03 | Identificar cámara de entrada o salida | Aceptar identificadores conocidos y rechazar desconocidos |
| RF-04 | Entrada suma y salida resta según tipo | Probar las cuatro combinaciones |
| RF-05 | Vacío o confianza inferior al umbral no cuentan | Comprobar estado sin cambios |
| RF-06 | Respetar capacidad y cero | Entrada lleno y salida vacío no alteran límites |
| RF-07 | Reducir duplicados mediante cooldown por cámara | Probar capturas repetidas y ambas cámaras independientes |
| RF-08 | Guardar estado y eventos aceptados | Verificar coherencia y concurrencia en Firebase |
| RF-09 | Mostrar ocupados, disponibles, cámaras y eventos en Flutter | Observar actualización mediante streams |
| RF-10 | Identificar cámara desconectada | Validar caducidad del último contacto |

## Parámetros iniciales

Capacidad car=5 y motorcycle=5; occupied=0; available=5 por tipo. Confianza mínima 0.85 (se acepta igualdad), cooldown 2500 ms por cámara. Son valores de arranque para validar en la maqueta, no mediciones del hardware.

## Requisitos de calidad

- No almacenar secretos en el repositorio.
- Separar inferencia, negocio y persistencia.
- Reservar evaluación independiente y evitar imágenes casi idénticas entre entrenamiento y prueba.
- No perder actualizaciones con las dos cámaras funcionando simultáneamente.
- Rechazar imágenes inválidas y cámaras desconocidas sin alterar el conteo.
- Definir reintentos e idempotencia antes de integrar conteo persistente.

## Salida de fase 1

Repositorio Git local inicializado; estructura conservada y completada; README y AGENTS escritos; arquitectura y requisitos documentados; exclusiones comprobadas; capacidades y cámaras definidas. No requiere firmware, modelo, backend ni conexión a Firebase funcionando.

## Pendientes de validar

Capacidad física de la maqueta; resolución y calidad definitivas; métrica y umbral de aceptación del modelo; mecanismo de conexión de cámaras; prevención de conteos de un vehículo detenido más allá del cooldown; reglas de acceso de Firebase.
