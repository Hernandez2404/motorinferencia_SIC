# Reporte del sistema experto

- **Dominio:** Diagnóstico de rendimiento y caídas de un servidor / aplicación web
- **Fecha:** 2026-10-14 22:20:14
- **Base de conocimiento:** `base_conocimiento.json` (25 reglas)
- **Ingreso de hechos:** archivo de caso `sin_diagnostico.json`: Síntomas aislados sin diagnóstico concluyente
- **Estrategia de resolución de conflictos:** refracción -> prioridad -> recencia -> especificidad -> azar (semilla 2026)

## 1. Datos del caso

**Síntomas reportados:**

- Uso de memoria RAM por encima del 90 % (`memoria_alta`)
- Muchas consultas lentas en la base de datos (`consultas_lentas_bd`)

**Síntomas descartados por el usuario:** 0

## 2. Resumen para la toma de decisiones

**Severidad:** sin incidente crítico identificado; atender según la prioridad de los diagnósticos.

**Diagnósticos:**

- No se identificó el problema con la información suministrada. Se sugiere consultar con un técnico especializado.

**Recomendaciones (en orden de prioridad):**

- (ninguna)

## 3. Explicación: ¿cómo se llegó a cada conclusión?

No se llegó a ningún diagnóstico.

## 4. Hipótesis por confirmar (¿por qué no?)

- Para concluir **El servidor está bajo presión de memoria (RAM saturada y uso de swap)** (R01) solo falta: ¿El servidor está usando memoria swap de forma intensiva? (no fue informado). Conviene verificarlo.
- Para concluir **La base de datos es el cuello de botella del tiempo de respuesta** (R05) solo falta: ¿Las páginas tardan más de lo normal en responder (más de 3 segundos)? (no fue informado). Conviene verificarlo.

## 5. Traza del razonamiento

| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |
|---|---|---|---|---|

Inferencia terminada: no quedan reglas aplicables.

## 6. Memoria de trabajo final

| Hecho | Tipo | Ciclo de ingreso | Descripción |
|---|---|---|---|
| `memoria_alta` | sintoma | 0 | Uso de memoria RAM por encima del 90 % |
| `consultas_lentas_bd` | sintoma | 0 | Muchas consultas lentas en la base de datos |
