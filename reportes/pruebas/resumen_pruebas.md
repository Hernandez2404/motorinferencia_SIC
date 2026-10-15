# Resumen de pruebas del sistema experto

## Casos de prueba

| Caso | Descripción | Ciclos | Reglas disparadas | Profundidad | Cadena más larga | Resultado |
|---|---|---|---|---|---|---|
| bd_despliegue | Base de datos saturada después de un despliegue | 6 | R02 R13 R23 R05 R11 R21 | 3 | respuesta_lenta -> servicio_degradado -> diag_regresion_despliegue -> rec_rollback | OK |
| caida_disco | Sitio caído con el disco lleno por logs | 6 | R03 R15 R25 R06 R12 R22 | 3 | sitio_no_disponible -> servicio_caido -> incidente_critico -> rec_plan_contingencia | OK |
| ddos | Ataque de denegación de servicio que degrada el sitio | 6 | R02 R04 R10 R16 R25 R20 | 4 | cpu_alta -> sobrecarga_cpu -> diag_ddos -> incidente_critico -> rec_plan_contingencia | OK |
| memoria | Fuga de memoria que termina en caída por OOM | 5 | R01 R07 R17 R08 R18 | 3 | memoria_alta -> presion_memoria -> diag_fuga_memoria -> rec_fuga_memoria | OK |
| pico_certificado | Pico de demanda por campaña y certificado vencido | 5 | R04 R09 R19 R14 R24 | 3 | cpu_alta -> sobrecarga_cpu -> diag_pico_demanda -> rec_escalar | OK |
| sin_diagnostico | Síntomas aislados sin diagnóstico concluyente | 0 | - | 0 | (sin inferencias) | OK |

## Cobertura de reglas

Reglas disparadas en al menos un caso: 25 de 25. Cobertura completa.

## Comparación de estrategias (caso combinado ddos + memoria)

| Orden de criterios | Secuencia de reglas disparadas | Ciclo del primer diagnóstico | Ciclo de incidente crítico |
|---|---|---|---|
| prioridad -> recencia -> especificidad -> azar | R01 R07 R17 R08 R18 R04 R10 R20 R02 R16 R25 | 2 | 10 |
| recencia -> prioridad -> especificidad -> azar | R01 R07 R17 R08 R18 R04 R10 R20 R02 R16 R25 | 2 | 10 |
| especificidad | R01 R02 R04 R07 R08 R10 R16 R17 R18 R20 R25 | 4 | 7 |

Las tres estrategias llegan al mismo conjunto final de hechos: sí.
