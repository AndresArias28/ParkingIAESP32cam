# Parking IA

Parqueadero Inteligente Automatizado (P.I.A.): MVP de una maqueta que cuenta carros y motos mediante cámaras ESP32-CAM y muestra los cupos en Flutter.

## Flujo previsto

ESP32-CAM → JPEG por HTTP → backend Python/Flask → clasificador Carro/Moto/Vacío → reglas de conteo → Firebase Realtime Database → Flutter.

La inferencia se ejecutará en el backend. La app consultará Firebase mediante streams.

## Estado actual

Fase 1 completada: estructura, documentación, parámetros iniciales y control de versiones local. Backend, firmware y entrenamiento están pendientes; las carpetas reservadas no contienen todavía implementaciones ejecutables. La app recuperada está en `movil_app/` y conserva su integración anterior con Firebase.

## Organización

| Ruta | Contenido |
| --- | --- |
| `docs/constitution.md` | Principios y decisiones del proyecto |
| `docs/architecture.md` | Componentes, contratos y datos previstos |
| `docs/requirements.md` | Requisitos y criterios de aceptación |
| `docs/phases.md` | Avance y siguiente paso |
| `config/parking.example.json` | Parámetros iniciales sin credenciales |
| `backend/app/`, `backend/tests/` | Backend y pruebas futuras |
| `firmware/entrada/`, `firmware/salida/` | Firmware futuro de cada cámara |
| `ml/dataset/`, `ml/model/`, `ml/training/` | Capturas, modelo y entrenamiento |
| `movil_app/` | Aplicación Flutter recuperada |

Se conserva `movil_app/` en vez de trasladarla a `mobile/parking_app/` para preservar el proyecto existente.

## Parámetros iniciales de la maqueta

- Capacidad: 5 carros y 5 motos; ocupación inicial: 0 para ambos.
- Entrada: `entrance-01`; salida: `exit-01`.
- Confianza mínima: 0.85; cooldown: 2500 ms por cámara.
- Captura a evaluar en fase 2A: JPEG, VGA 640×480, calidad 12 y un framebuffer.

Son valores iniciales tomados del plan; deberán ajustarse a la maqueta y validarse con capturas reales. El archivo de ejemplo documenta la configuración y todavía no lo consume ningún componente.

## Siguiente paso

La cámara de entrada ya captura desde `/capture` según pruebas del usuario, con RST manual tras conectar USB. La herramienta de fase 2B guardó 76 fotos comprobadas como JPEG de 640×480. El primer modelo de Teachable Machine está en `ml/model/`; el backend de inferencia carga el modelo y responde a pruebas HTTP. Sigue `docs/backend.md` para ejecutarlo. Quedan pendientes la evaluación con fotos nuevas y la corrección de etiquetas y variedad del dataset antes de conectar el conteo.

El firmware de entrada para enviar fotografías cada 2 segundos está preparado en `firmware/entrada/parking_entrada.ino`. Sigue `docs/esp32-every-2-seconds.md` para cargarlo desde Arduino Cloud y conectarlo al backend. El conteo y Flutter aún no reciben estas predicciones.

## Configuración y seguridad

No guardar contraseñas Wi-Fi, cuentas de servicio, claves privadas ni tokens en Git. Usar variables de entorno o archivos locales excluidos. Los datasets y modelos también se excluyen por tamaño y posible contenido sensible. No se han publicado cambios ni desplegado servicios.

Documento fuente: `Parking IA — Reconstrucción, arquitectura y fases .md`.
