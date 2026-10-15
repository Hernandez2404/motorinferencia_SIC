# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `pico_certificado.json`: Pico de demanda por campaña y certificado vencido
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- Uso de CPU sostenido por encima del 90 % (`cpu_alta`)
- Volumen de peticiones muy por encima de lo habitual (`trafico_alto`)
- Existe una campaña o evento que explica más usuarios (`evento_o_campana`)
- El navegador advierte de un certificado SSL/TLS inválido (`alerta_certificado`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** sin incidente crítico identificado; atender según la prioridad de los diagnósticos.

**Diagnósticos:**

- Pico de demanda legítimo que supera la capacidad instalada (prioridad 5, R09)
- Certificado SSL/TLS vencido o mal configurado (prioridad 3, R14)

**Recomendaciones (en orden de prioridad):**

1. Escalar horizontalmente (más instancias o autoescalado) y activar caché y CDN para el contenido estático. *(por R19, a partir de: Pico de demanda legítimo que supera la capacidad instalada)*
2. Renovar el certificado (por ejemplo con certbot / Let's Encrypt) y automatizar su renovación. *(por R24, a partir de: Certificado SSL/TLS vencido o mal configurado)*

## 3. Explicación: ¿cómo se llegó a cada conclusión?

- **Pico de demanda legítimo que supera la capacidad instalada** (`diag_pico_demanda`): concluido por R09 *Pico de demanda legítimo* en el ciclo 2. La sobrecarga coincide con un evento que atrae usuarios reales: la capacidad instalada no alcanza.
  - **La CPU está saturada por exceso de peticiones** (`sobrecarga_cpu`): concluido por R04 *Sobrecarga de CPU por tráfico* en el ciclo 1. CPU alta junto con tráfico alto indica que la carga proviene del volumen de peticiones.
    - Uso de CPU sostenido por encima del 90 % (`cpu_alta`): síntoma reportado
    - Volumen de peticiones muy por encima de lo habitual (`trafico_alto`): síntoma reportado
  - Existe una campaña o evento que explica más usuarios (`evento_o_campana`): síntoma reportado

- **Certificado SSL/TLS vencido o mal configurado** (`diag_certificado_invalido`): concluido por R14 *Certificado SSL/TLS inválido* en el ciclo 4. La advertencia del navegador indica que el certificado venció o no corresponde al dominio.
  - El navegador advierte de un certificado SSL/TLS inválido (`alerta_certificado`): síntoma reportado

## 4. Hipótesis por confirmar (¿por qué no?)

- Para concluir **Posible ataque de denegación de servicio (DDoS)** (R10) solo falta: ¿La mayor parte del tráfico proviene de pocas direcciones IP o presenta patrones repetitivos anómalos? (no fue informado). Conviene verificarlo.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|
| 1 | R04, R14 | R04 Sobrecarga de CPU por tráfico | prioridad (R04=5, R14=3) | `sobrecarga_cpu` |
| 2 | R09, R14 | R09 Pico de demanda legítimo | prioridad (R09=5, R14=3) | `diag_pico_demanda` |
| 3 | R14, R19 | R19 Recomendación: escalar capacidad | prioridad (R14=3, R19=5) | `rec_escalar` |
| 4 | R14 | R14 Certificado SSL/TLS inválido | única aplicable | `diag_certificado_invalido` |
| 5 | R24 | R24 Recomendación: renovar certificado | única aplicable | `rec_renovar_certificado` |

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `cpu_alta` | sintoma | 0 | Uso de CPU sostenido por encima del 90 % |
| `trafico_alto` | sintoma | 0 | Volumen de peticiones muy por encima de lo habitual |
| `evento_o_campana` | sintoma | 0 | Existe una campaña o evento que explica más usuarios |
| `alerta_certificado` | sintoma | 0 | El navegador advierte de un certificado SSL/TLS inválido |
| `sobrecarga_cpu` | intermedio | 1 | La CPU está saturada por exceso de peticiones |
| `diag_pico_demanda` | diagnostico | 2 | Pico de demanda legítimo que supera la capacidad instalada |
| `rec_escalar` | recomendacion | 3 | Escalar horizontalmente (más instancias o autoescalado) y activar caché y CDN para el contenido estático. |
| `diag_certificado_invalido` | diagnostico | 4 | Certificado SSL/TLS vencido o mal configurado |
| `rec_renovar_certificado` | recomendacion | 5 | Renovar el certificado (por ejemplo con certbot / Let's Encrypt) y automatizar su renovación. |
