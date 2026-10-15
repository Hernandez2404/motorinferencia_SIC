# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `ddos.json`: Ataque de denegación de servicio que degrada el sitio
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- Uso de CPU sostenido por encima del 90 % (`cpu_alta`)
- Volumen de peticiones muy por encima de lo habitual (`trafico_alto`)
- Tráfico concentrado en pocas IP o con patrones anómalos (`trafico_origen_concentrado`)
- Tiempos de respuesta superiores a lo normal (`respuesta_lenta`)
- Los usuarios reciben errores HTTP 5xx (`errores_5xx`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio (respaldado por R16)

**Diagnósticos:**

- Posible ataque de denegación de servicio (DDoS) (prioridad 10, R10)

**Recomendaciones (en orden de prioridad):**

1. Notificar al equipo de guardia, publicar una página de mantenimiento y abrir el registro formal del incidente. *(por R25, a partir de: Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio)*
2. Activar rate limiting y WAF, bloquear las IP de origen del ataque y contactar al proveedor de protección anti-DDoS. *(por R20, a partir de: Posible ataque de denegación de servicio (DDoS))*

## 3. Explicación: ¿cómo se llegó a cada conclusión?

- **Posible ataque de denegación de servicio (DDoS)** (`diag_ddos`): concluido por R10 *Posible ataque DDoS* en el ciclo 3. Una sobrecarga producida por tráfico de pocas IP o con patrones repetitivos sugiere un ataque de denegación de servicio.
  - **La CPU está saturada por exceso de peticiones** (`sobrecarga_cpu`): concluido por R04 *Sobrecarga de CPU por tráfico* en el ciclo 2. CPU alta junto con tráfico alto indica que la carga proviene del volumen de peticiones.
    - Uso de CPU sostenido por encima del 90 % (`cpu_alta`): síntoma reportado
    - Volumen de peticiones muy por encima de lo habitual (`trafico_alto`): síntoma reportado
  - Tráfico concentrado en pocas IP o con patrones anómalos (`trafico_origen_concentrado`): síntoma reportado

- **Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio** (`incidente_critico`): concluido por R16 *Incidente crítico por ataque* en el ciclo 4. Un ataque que ya degrada el servicio requiere respuesta inmediata: se clasifica como incidente crítico.
  - **Posible ataque de denegación de servicio (DDoS)** (`diag_ddos`): ver su explicación arriba
  - **El servicio está degradado: responde lento y con errores** (`servicio_degradado`): concluido por R02 *Servicio degradado* en el ciclo 1. Lentitud combinada con errores 5xx significa que el servicio sigue arriba pero no atiende bien las peticiones.
    - Tiempos de respuesta superiores a lo normal (`respuesta_lenta`): síntoma reportado
    - Los usuarios reciben errores HTTP 5xx (`errores_5xx`): síntoma reportado

## 4. Hipótesis por confirmar (¿por qué no?)

- Para concluir **La base de datos es el cuello de botella del tiempo de respuesta** (R05) solo falta: ¿El registro de consultas lentas de la base de datos muestra muchas consultas lentas? (no fue informado). Conviene verificarlo.
- Para concluir **Pico de demanda legítimo que supera la capacidad instalada** (R09) solo falta: ¿Hay una campaña, lanzamiento o evento que explique un aumento legítimo de usuarios? (no fue informado). Conviene verificarlo.
- Para concluir **Regresión introducida por el último despliegue** (R13) solo falta: ¿Se desplegó una nueva versión de la aplicación en las últimas horas? (no fue informado). Conviene verificarlo.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|
| 1 | R02, R04 | R02 Servicio degradado | azar (empate en todos los criterios anteriores) | `servicio_degradado` |
| 2 | R04 | R04 Sobrecarga de CPU por tráfico | única aplicable | `sobrecarga_cpu` |
| 3 | R10 | R10 Posible ataque DDoS | única aplicable | `diag_ddos` |
| 4 | R16, R20 | R16 Incidente crítico por ataque | especificidad (R16=2, R20=1) | `incidente_critico` |
| 5 | R20, R25 | R25 Recomendación: plan de contingencia | recencia (R20=3, R25=4) | `rec_plan_contingencia` |
| 6 | R20 | R20 Recomendación: mitigar ataque | única aplicable | `rec_mitigar_ataque` |

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `cpu_alta` | sintoma | 0 | Uso de CPU sostenido por encima del 90 % |
| `trafico_alto` | sintoma | 0 | Volumen de peticiones muy por encima de lo habitual |
| `trafico_origen_concentrado` | sintoma | 0 | Tráfico concentrado en pocas IP o con patrones anómalos |
| `respuesta_lenta` | sintoma | 0 | Tiempos de respuesta superiores a lo normal |
| `errores_5xx` | sintoma | 0 | Los usuarios reciben errores HTTP 5xx |
| `servicio_degradado` | intermedio | 1 | El servicio está degradado: responde lento y con errores |
| `sobrecarga_cpu` | intermedio | 2 | La CPU está saturada por exceso de peticiones |
| `diag_ddos` | diagnostico | 3 | Posible ataque de denegación de servicio (DDoS) |
| `incidente_critico` | severidad | 4 | Incidente de severidad CRÍTICA: afecta la disponibilidad del servicio |
| `rec_plan_contingencia` | recomendacion | 5 | Notificar al equipo de guardia, publicar una página de mantenimiento y abrir el registro formal del incidente. |
| `rec_mitigar_ataque` | recomendacion | 6 | Activar rate limiting y WAF, bloquear las IP de origen del ataque y contactar al proveedor de protección anti-DDoS. |
