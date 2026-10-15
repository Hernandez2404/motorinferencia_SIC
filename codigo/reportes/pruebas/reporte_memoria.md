# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `memoria.json`: Fuga de memoria que termina en caída por OOM
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- Uso de memoria RAM por encima del 90 % (`memoria_alta`)
- Uso intensivo de memoria swap (`swap_activa`)
- La memoria de la aplicación crece sin liberarse (`memoria_crece_sin_liberarse`)
- Los logs muestran eventos 'Out of memory' (OOM killer) (`oom_en_logs`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** sin incidente crítico identificado; atender según la prioridad de los diagnósticos.

**Diagnósticos:**

- Fuga de memoria en la aplicación (prioridad 7, R07)
- Caída del servicio por falta de memoria (OOM) (prioridad 7, R08)

**Recomendaciones (en orden de prioridad):**

1. Perfilar la memoria de la aplicación (heap dump), corregir la fuga y, mientras tanto, programar reinicios controlados del servicio. *(por R17, a partir de: Fuga de memoria en la aplicación)*
2. Reiniciar el servicio, aumentar la RAM o reducir el número de workers, y configurar límites de memoria por proceso. *(por R18, a partir de: Caída del servicio por falta de memoria (OOM))*

## 3. Explicación: ¿cómo se llegó a cada conclusión?

- **Fuga de memoria en la aplicación** (`diag_fuga_memoria`): concluido por R07 *Fuga de memoria* en el ciclo 2. La presión de memoria acompañada de un crecimiento continuo con carga estable es el patrón típico de una fuga.
  - **El servidor está bajo presión de memoria (RAM saturada y uso de swap)** (`presion_memoria`): concluido por R01 *Presión de memoria* en el ciclo 1. Con la RAM saturada el sistema recurre a la swap, lo que indica que la memoria física no alcanza.
    - Uso de memoria RAM por encima del 90 % (`memoria_alta`): síntoma reportado
    - Uso intensivo de memoria swap (`swap_activa`): síntoma reportado
  - La memoria de la aplicación crece sin liberarse (`memoria_crece_sin_liberarse`): síntoma reportado

- **Caída del servicio por falta de memoria (OOM)** (`diag_caida_oom`): concluido por R08 *Caída por falta de memoria (OOM)* en el ciclo 4. Bajo presión de memoria, el OOM killer del kernel termina procesos; los logs lo confirman.
  - **El servidor está bajo presión de memoria (RAM saturada y uso de swap)** (`presion_memoria`): concluido por R01 *Presión de memoria* en el ciclo 1. Con la RAM saturada el sistema recurre a la swap, lo que indica que la memoria física no alcanza.
    - Uso de memoria RAM por encima del 90 % (`memoria_alta`): síntoma reportado
    - Uso intensivo de memoria swap (`swap_activa`): síntoma reportado
  - Los logs muestran eventos 'Out of memory' (OOM killer) (`oom_en_logs`): síntoma reportado

## 4. Hipótesis por confirmar (¿por qué no?)

- No hay reglas a las que les falte un único síntoma.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|
| 1 | R01 | R01 Presión de memoria | única aplicable | `presion_memoria` |
| 2 | R07, R08 | R07 Fuga de memoria | azar (empate en todos los criterios anteriores) | `diag_fuga_memoria` |
| 3 | R08, R17 | R17 Recomendación: fuga de memoria | recencia (R08=1, R17=2) | `rec_fuga_memoria` |
| 4 | R08 | R08 Caída por falta de memoria (OOM) | única aplicable | `diag_caida_oom` |
| 5 | R18 | R18 Recomendación: falta de memoria | única aplicable | `rec_memoria` |

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `memoria_alta` | sintoma | 0 | Uso de memoria RAM por encima del 90 % |
| `swap_activa` | sintoma | 0 | Uso intensivo de memoria swap |
| `memoria_crece_sin_liberarse` | sintoma | 0 | La memoria de la aplicación crece sin liberarse |
| `oom_en_logs` | sintoma | 0 | Los logs muestran eventos 'Out of memory' (OOM killer) |
| `presion_memoria` | intermedio | 1 | El servidor está bajo presión de memoria (RAM saturada y uso de swap) |
| `diag_fuga_memoria` | diagnostico | 2 | Fuga de memoria en la aplicación |
| `rec_fuga_memoria` | recomendacion | 3 | Perfilar la memoria de la aplicación (heap dump), corregir la fuga y, mientras tanto, programar reinicios controlados del servicio. |
| `diag_caida_oom` | diagnostico | 4 | Caída del servicio por falta de memoria (OOM) |
| `rec_memoria` | recomendacion | 5 | Reiniciar el servicio, aumentar la RAM o reducir el número de workers, y configurar límites de memoria por proceso. |
