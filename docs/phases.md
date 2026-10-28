# Seguimiento de fases

## Fase 1 — Base y documentación

- [x] Inicializar repositorio Git local con nombre lógico parking-ia (carpeta existente: parqueaderoIA).
- [x] Preparar estructura de carpetas y conservar movil_app/.
- [x] Crear README.md y AGENTS.md.
- [x] Documentar arquitectura, principios y requisitos.
- [x] Configurar exclusiones de secretos, datos y archivos generados.
- [x] Definir capacidad inicial: 5 carros y 5 motos.
- [x] Definir cámaras entrance-01 y exit-01.

No se ha creado un repositorio remoto ni publicado el proyecto. Los marcadores .gitkeep reservan carpetas para las fases siguientes.

## Fase 2A — Captura funcional con reinicio manual

- [x] Confirmar placa AI Thinker ESP32-CAM con base ESP32-CAM-MB.
- [x] Cargar firmware desde Arduino Cloud y crear red Wi-Fi ParkingIA-Entrada.
- [x] Inicializar sensor y capturar JPEG (confirmado por el usuario).
- [x] Exponer /capture y descargar imágenes desde navegador.
- [ ] Evaluar VGA 640×480, calidad 12 y un framebuffer.
- [ ] Revisar enfoque, encuadre y estabilidad; fijar parámetros de dataset e inferencia.

Criterio de salida: obtener imágenes válidas consistentemente desde la cámara de entrada. Este paso requiere hardware y red local.

El usuario confirmó tres ciclos exitosos: conectar USB → pulsar RST → conectar a ParkingIA-Entrada → abrir http://192.168.4.1/capture. Abrir el monitor serie detiene el parpadeo del programa de diagnóstico; causa pendiente de confirmar. Mantenerlo cerrado. Falta resolver el arranque sin RST y confirmar visualmente encuadre y parámetros antes del dataset completo. El firmware cargado desde Cloud aún no está recuperado como archivo local del repositorio.

## Fase 2B — Herramienta preparada; prueba real pendiente

- [x] Crear ml/training/capture_dataset.py sin dependencias externas.
- [x] Permitir clase, cámara, URL y cantidad; captura manual o automática.
- [x] Guardar por clase con sesión y secuencia sin sobrescribir archivos.
- [x] Confirmar captura desde el computador conectado a la cámara: se encontraron 46 imágenes en carro, 20 en moto y 10 en vacio (27 de octubre de 2026). Las 76 se abren como JPEG de 640×480; el usuario confirmó que las capturó.
- [ ] Corregir contenido y etiquetas de las fotografías antes de usar el dataset.

Instrucciones: docs/dataset-capture.md. En la inspección visual de muestra, una foto de carro no contiene un carro visible y tres fotos de moto muestran una figura humana de juguete, no una moto. Las fotos vacías muestreadas parecen repetitivas y muestran una sombra pronunciada. Las fotos existentes se conservaron sin mover ni borrar; requieren revisión completa por el usuario.

## Fase 2C — Dataset en construcción

- [x] Crear carpetas por clase y comenzar capturas desde entrance-01.
- [ ] Montar y fijar la cámara sobre el escenario real de la maqueta.
- [ ] Revisar todas las etiquetas y descartar tomas borrosas o sin el objeto correspondiente.
- [ ] Capturar motos reales de juguete para la clase moto y escenas vacías variadas para vacio.
- [ ] Equilibrar clases y reunir aproximadamente 200–300 fotos útiles por clase con variaciones reales.
- [ ] Añadir capturas desde exit-01 cuando la segunda cámara esté disponible.
- [ ] Reservar sesiones completas de evaluación independientes de entrenamiento.

El usuario informó que ya entrenó un primer modelo con Teachable Machine. Este puede servir para comprobar la integración técnica, pero faltan etiquetas confiables, variedad y la perspectiva de salida antes de considerarlo validado para conteo real.

## Fase 3 — Primer modelo de prueba

- [x] Entrenamiento inicial realizado por el usuario en Teachable Machine.
- [x] `keras_model.h5` y `labels.txt` exportados presentes en `ml/model/` (27 de octubre de 2026).
- [ ] Evaluar imágenes nuevas y documentar resultados por clase.

## Fase 4 — Backend Python de inferencia

- [x] Implementar `ImageClassifier` con preprocesamiento y etiquetas validadas.
- [x] Implementar Flask con `/health` y `POST /api/v1/predict`, carga multipart o JPEG directo.
- [x] Añadir validación de cámara, imagen y límite de tamaño.
- [x] Añadir cliente Python para consultar `/capture` y enviar una foto al servidor local.
- [x] Añadir pruebas HTTP sin modelo real.
- [x] Cargar el modelo exportado (entrada 224×224, orden Moto/Carro/Vacío) y comprobar `/health` y `POST /api/v1/predict` mediante peticiones HTTP reales al servidor en `127.0.0.1:5000`; ambos respondieron 200.
- [x] Ejecutar cinco pruebas del contrato HTTP y predecir una foto existente de cada clase.
- [ ] Evaluar predicciones sobre fotos nuevas, ajenas al entrenamiento, y revisar confusiones por clase.

Guía de ejecución: `docs/backend.md`. El modelo y las fotos están excluidos de Git. La clasificación técnica funciona, pero la confianza alta observada en fotos existentes no valida la precisión: una de las fotos de `carro` sin carro visible recibió `car` con 0.9999. No usar este modelo para modificar cupos hasta corregir etiquetas y evaluarlo con fotos nuevas.

## Fase 5 — Envío automático de la ESP32-CAM

- [x] Preparar `firmware/entrada/parking_entrada.ino` para capturar y enviar JPEG cada 2 segundos al backend.
- [x] Configurar el servidor para escuchar en la red de la cámara cuando `PARKING_HOST=0.0.0.0`.
- [x] Conservar `/capture` y registrar la clasificación en la terminal del servidor.
- [ ] Compilar y cargar el sketch desde Arduino Cloud; probar flujo real cámara → servidor.
- [ ] Resolver arranque de la cámara sin RST manual.

Guía: `docs/esp32-every-2-seconds.md`. El firmware todavía no se ha compilado ni probado en la placa desde este repositorio.

## Fases posteriores

2B: herramienta de captura; 2C: dataset de ambas cámaras; 3: entrenamiento y evaluación; 4: backend de inferencia; 5: envío ESP32 → backend; 6: Firebase y conteo; 7: cámara de salida; 8: adaptar Flutter; 9: pruebas integrales.

Consultar el documento original para el detalle. Su sección «Próximo paso inmediato» describe la fase 2A; primero se preparó la fase 1 siguiendo la solicitud actual.
