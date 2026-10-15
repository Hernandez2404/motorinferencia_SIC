# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `caida_disco.json`: Sitio caído con el disco lleno por logs
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- El sitio no carga (timeout o conexión rechazada) (`sitio_no_disponible`)
- El proceso del servidor web / aplicación está detenido (`proceso_web_detenido`)
- Partición de disco llena o casi llena (`disco_lleno`)
- Los archivos de log ocupan mucho espacio o crecen rápido (`logs_crecen_rapido`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio (respaldado por R15)

**Diagnósticos:**

- Disco lleno por logs sin rotación (prioridad 7, R12)

**Recomendaciones (en orden de prioridad):**

1. Notificar al equipo de guardia, publicar una página de mantenimiento y abrir el registro formal del incidente. *(por R25, a partir de: Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio)*
2. Liberar espacio comprimiendo o eliminando logs antiguos y configurar la rotación automática (logrotate). *(por R22, a partir de: Disco lleno por logs sin rotación)*

## 3. Explicación: ¿cómo se llegó a cada conclusión?

- **Disco lleno por logs sin rotación** (`diag_logs_sin_rotacion`): concluido por R12 *Logs sin rotación* en el ciclo 5. El disco se llenó y los logs son los que más crecen: falta una política de rotación.
  - **El servidor no puede escribir en disco por falta de espacio** (`escritura_bloqueada`): concluido por R06 *Escritura bloqueada* en el ciclo 4. Sin espacio libre, la aplicación y el sistema no pueden escribir archivos, sesiones ni logs.
    - Partición de disco llena o casi llena (`disco_lleno`): síntoma reportado
  - Los archivos de log ocupan mucho espacio o crecen rápido (`logs_crecen_rapido`): síntoma reportado

- **Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio** (`incidente_critico`): concluido por R15 *Incidente crítico por caída* en el ciclo 2. Un servicio fuera de línea afecta a todos los usuarios: se clasifica como incidente crítico.
  - **El servicio web está caído** (`servicio_caido`): concluido por R03 *Servicio caído* en el ciclo 1. Si el sitio no carga y el proceso web está detenido, el servicio está fuera de línea.
    - El sitio no carga (timeout o conexión rechazada) (`sitio_no_disponible`): síntoma reportado
    - El proceso del servidor web / aplicación está detenido (`proceso_web_detenido`): síntoma reportado

## 4. Hipótesis por confirmar (¿por qué no?)

- No hay reglas a las que les falte un único síntoma.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|
| 1 | R03, R06 | R03 Servicio caído | prioridad (R03=10, R06=7) | `servicio_caido` |
| 2 | R06, R15 | R15 Incidente crítico por caída | prioridad (R06=7, R15=10) | `incidente_critico` |
| 3 | R06, R25 | R25 Recomendación: plan de contingencia | prioridad (R06=7, R25=10) | `rec_plan_contingencia` |
| 4 | R06 | R06 Escritura bloqueada | única aplicable | `escritura_bloqueada` |
| 5 | R12 | R12 Logs sin rotación | única aplicable | `diag_logs_sin_rotacion` |
| 6 | R22 | R22 Recomendación: rotar logs | única aplicable | `rec_rotar_logs` |

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `sitio_no_disponible` | sintoma | 0 | El sitio no carga (timeout o conexión rechazada) |
| `proceso_web_detenido` | sintoma | 0 | El proceso del servidor web / aplicación está detenido |
| `disco_lleno` | sintoma | 0 | Partición de disco llena o casi llena |
| `logs_crecen_rapido` | sintoma | 0 | Los archivos de log ocupan mucho espacio o crecen rápido |
| `servicio_caido` | intermedio | 1 | El servicio web está caído |
| `incidente_critico` | severidad | 2 | Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio |
| `rec_plan_contingencia` | recomendacion | 3 | Notificar al equipo de guardia, publicar una página de mantenimiento y abrir el registro formal del incidente. |
| `escritura_bloqueada` | intermedio | 4 | El servidor no puede escribir en disco por falta de espacio |
| `diag_logs_sin_rotacion` | diagnostico | 5 | Disco lleno por logs sin rotación |
| `rec_rotar_logs` | recomendacion | 6 | Liberar espacio comprimiendo o eliminando logs antiguos y configurar la rotación automática (logrotate). |
