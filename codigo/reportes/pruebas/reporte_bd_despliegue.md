# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `bd_despliegue.json`: Base de datos saturada después de un despliegue
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- Tiempos de respuesta superiores a lo normal (`respuesta_lenta`)
- Los usuarios reciben errores HTTP 5xx (`errores_5xx`)
- Muchas consultas lentas en la base de datos (`consultas_lentas_bd`)
- Pool de conexiones a la base de datos agotado (`conexiones_bd_agotadas`)
- Se desplegó una nueva versión recientemente (`despliegue_reciente`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** sin incidente crítico identificado; atender según la prioridad de los diagnósticos.

**Diagnósticos:**

- Regresión introducida por el último despliegue (prioridad 5, R13)
- Saturación de la base de datos (consultas lentas y pool de conexiones agotado) (prioridad 5, R11)

**Recomendaciones (en orden de prioridad):**

1. Hacer rollback a la versión anterior y revisar los cambios incluidos en el último despliegue. *(por R23, a partir de: Regresión introducida por el último despliegue)*
2. Revisar índices y planes de ejecución (EXPLAIN) de las consultas lentas, ampliar el pool de conexiones y agregar caché de consultas. *(por R21, a partir de: Saturación de la base de datos (consultas lentas y pool de conexiones agotado))*

## 3. Explicación: ¿cómo se llegó a cada conclusión?

- **Regresión introducida por el último despliegue** (`diag_regresion_despliegue`): concluido por R13 *Regresión por despliegue* en el ciclo 2. La degradación aparece justo después de un despliegue, por lo que el cambio es la causa más probable.
  - **El servicio está degradado: responde lento y con errores** (`servicio_degradado`): concluido por R02 *Servicio degradado* en el ciclo 1. Lentitud combinada con errores 5xx significa que el servicio sigue arriba pero no atiende bien las peticiones.
    - Tiempos de respuesta superiores a lo normal (`respuesta_lenta`): síntoma reportado
    - Los usuarios reciben errores HTTP 5xx (`errores_5xx`): síntoma reportado
  - Se desplegó una nueva versión recientemente (`despliegue_reciente`): síntoma reportado

- **Saturación de la base de datos (consultas lentas y pool de conexiones agotado)** (`diag_saturacion_bd`): concluido por R11 *Saturación de la base de datos* en el ciclo 5. Las consultas lentas retienen conexiones y terminan agotando el pool: la base de datos está saturada.
  - **La base de datos es el cuello de botella del tiempo de respuesta** (`cuello_botella_bd`): concluido por R05 *Cuello de botella en BD* en el ciclo 4. Si hay consultas lentas y la respuesta del sitio es lenta, el tiempo se está perdiendo en la base de datos.
    - Muchas consultas lentas en la base de datos (`consultas_lentas_bd`): síntoma reportado
    - Tiempos de respuesta superiores a lo normal (`respuesta_lenta`): síntoma reportado
  - Pool de conexiones a la base de datos agotado (`conexiones_bd_agotadas`): síntoma reportado

## 4. Hipótesis por confirmar (¿por qué no?)

- No hay reglas a las que les falte un único síntoma.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|
| 1 | R02, R05 | R02 Servicio degradado | azar (empate en todos los criterios anteriores) | `servicio_degradado` |
| 2 | R05, R13 | R13 Regresión por despliegue | recencia (R05=0, R13=1) | `diag_regresion_despliegue` |
| 3 | R05, R23 | R23 Recomendación: rollback | recencia (R05=0, R23=2) | `rec_rollback` |
| 4 | R05 | R05 Cuello de botella en BD | única aplicable | `cuello_botella_bd` |
| 5 | R11 | R11 Saturación de la base de datos | única aplicable | `diag_saturacion_bd` |
| 6 | R21 | R21 Recomendación: optimizar base de datos | única aplicable | `rec_optimizar_bd` |

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `respuesta_lenta` | sintoma | 0 | Tiempos de respuesta superiores a lo normal |
| `errores_5xx` | sintoma | 0 | Los usuarios reciben errores HTTP 5xx |
| `consultas_lentas_bd` | sintoma | 0 | Muchas consultas lentas en la base de datos |
| `conexiones_bd_agotadas` | sintoma | 0 | Pool de conexiones a la base de datos agotado |
| `despliegue_reciente` | sintoma | 0 | Se desplegó una nueva versión recientemente |
| `servicio_degradado` | intermedio | 1 | El servicio está degradado: responde lento y con errores |
| `diag_regresion_despliegue` | diagnostico | 2 | Regresión introducida por el último despliegue |
| `rec_rollback` | recomendacion | 3 | Hacer rollback a la versión anterior y revisar los cambios incluidos en el último despliegue. |
| `cuello_botella_bd` | intermedio | 4 | La base de datos es el cuello de botella del tiempo de respuesta |
| `diag_saturacion_bd` | diagnostico | 5 | Saturación de la base de datos (consultas lentas y pool de conexiones agotado) |
| `rec_optimizar_bd` | recomendacion | 6 | Revisar índices y planes de ejecución (EXPLAIN) de las consultas lentas, ampliar el pool de conexiones y agregar caché de consultas. |
