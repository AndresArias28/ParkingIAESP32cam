# Principios y decisiones

## Alcance del MVP

Construir una maqueta funcional de conteo y visualización de cupos de carros y motos. No incluye identificación de placas, cobros, reservas ni reconocimiento individual de vehículos.

## Decisiones

1. Las ESP32-CAM capturan; el backend Python ejecuta la IA.
2. El dataset debe incluir imágenes de las dos cámaras reales, con la misma configuración que se usará en inferencia.
3. Mantener tres clases: Carro, Moto y Vacío.
4. Estabilizar primero la cámara de entrada; integrar salida después del flujo de inferencia.
5. Flutter visualiza Firebase; no ejecuta IA ni consulta directamente las cámaras.
6. Mantener inferencia, reglas y almacenamiento independientes.
7. Usar inicialmente 5 cupos por tipo, confianza 0.85 y cooldown de 2500 ms por cámara.
8. Conservar la aplicación recuperada en movil_app/ durante la reconstrucción.

## Calidad y datos

Reservar aproximadamente 20 % de imágenes para evaluación independiente. Separar por sesión o secuencia de captura para evitar que imágenes casi idénticas aparezcan a ambos lados. Una buena precisión sobre entrenamiento no demuestra rendimiento real.

El cooldown es una protección inicial, no una garantía de un conteo por vehículo. Su adecuación debe comprobarse en la maqueta, incluyendo vehículos detenidos y pasos próximos.

Nunca versionar secretos. No modificar la base de datos real al validar ejemplos locales.
