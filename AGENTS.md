# Instrucciones de trabajo

- Leer README.md y docs/ antes de modificar el proyecto; el plan original se conserva como referencia.
- Trabajar por fases y registrar avances verificables en docs/phases.md. No presentar carpetas vacías como funciones implementadas.
- Mantener la app recuperada en movil_app/ salvo que una tarea requiera migrarla.
- Separar inferencia (ImageClassifier), reglas (ParkingService) y persistencia (FirebaseRepository).
- Usar car, motorcycle y empty como identificadores internos; Carro, Moto y Vacío en la interfaz.
- Mantener 0 <= occupied <= capacity y available = capacity - occupied para cada tipo.
- Identificar cámaras como entrance-01 y exit-01. El cooldown debe ser por cámara.
- No incluir contraseñas, tokens, claves privadas ni cuentas de servicio en código, documentación, ejemplos o commits.
- Mantener dataset y modelos fuera de Git; conservar únicamente marcadores y documentación.
- Preservar cambios existentes del usuario. No publicar, desplegar ni cambiar Firebase real como parte de tareas locales de documentación.
- Verificar los cambios con controles adecuados a su alcance; para documentación, revisar enlaces, estructura, JSON y exclusiones. Para lógica futura, probar límites, confianza y duplicados.
- Documentar limitaciones: un cooldown reduce duplicados pero no garantiza identificar vehículos individuales.
