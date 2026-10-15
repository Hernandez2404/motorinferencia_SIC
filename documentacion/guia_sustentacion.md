# Guía de sustentación: sistema experto para el diagnóstico de servidores web

**Asignatura:** Sistemas Inteligentes Computacionales. Prof. Néstor Darío Duque Méndez
**Integrantes:** Jasmin Camila Guitierrez Maya, Mateo Falla Muños, Andres Hernandez
**Sustentación:** jueves 15 de octubre de 2026

> Cómo usar esta guía: lee primero la sección 1 (el discurso de 1 minuto) y la sección 2 (cifras). Las secciones 3 a 12 explican cada tema a fondo. La 13 es la demostración paso a paso y la 14 tiene las preguntas probables con su respuesta. Los números de línea se refieren a `sistema_experto.py` en su versión actual.

---

## 1. El trabajo en un minuto

> "Tomamos el motor de inferencia de clase, que hace **encadenamiento hacia adelante**, y le hicimos cuatro cambios.
> 1. La **base de conocimiento** ya no está en el código: se carga desde un **archivo JSON** cuya codificación definimos nosotros.
> 2. La **resolución de conflictos** pasó de solo especificidad a un filtro de cinco elementos: **refracción, prioridad, recencia, especificidad y azar con semilla**, en un orden configurable.
> 3. Los **hechos se ingresan al ejecutar el sistema**, por cuestionario, por lista numerada o desde un archivo de caso, y solo los verdaderos entran a la **memoria de trabajo**.
> 4. Agregamos un **módulo de explicación** que genera un reporte con severidad, diagnósticos, recomendaciones, el porqué de cada conclusión, lo que falta verificar y la traza ciclo a ciclo.
>
> Lo aplicamos al **diagnóstico de rendimiento y caídas de un servidor web**: 18 síntomas y 25 reglas en 4 niveles, donde los consecuentes de unas reglas son antecedentes de otras. Lo validamos con 6 casos automáticos que disparan las 25 reglas y llegan a cadenas de 4 niveles."

---

## 2. Cifras que deben saberse de memoria

| Dato | Valor |
|---|---|
| Hechos en la base | **42**: 18 síntomas, 6 intermedios, 8 diagnósticos, 1 severidad, 9 recomendaciones |
| Reglas | **25** en 4 niveles: R01–R06 intermedios, R07–R14 diagnósticos, R15–R16 severidad, R17–R25 recomendaciones |
| Reglas encadenadas (con algún antecedente inferido) | **18 de 25** |
| Cadena más larga | **4 reglas**: `cpu_alta → sobrecarga_cpu → diag_ddos → incidente_critico → rec_plan_contingencia` (R04 → R10 → R16 → R25) |
| Categorías de síntomas | 6: Disponibilidad (4), CPU y tráfico (4), Memoria (4), Disco (2), Base de datos (2), Cambios y seguridad (2) |
| Prioridades | **10** seguridad y caídas · **7** memoria y disco · **5** rendimiento · **3** mantenimiento |
| Orden de la estrategia | refracción (filtro) → prioridad → recencia → especificidad → azar |
| Semilla | **2026** |
| Casos de prueba | **6** (5 con diagnóstico y 1 negativo): 6/6 correctos y **25/25 reglas cubiertas** |
| Hallazgo de estrategia | Incidente crítico en el **ciclo 10** con prioridad primero, en el **ciclo 7** con solo especificidad y en el **ciclo 4** si R02 y R04 tuvieran prioridad 10 (solo simulado) |
| Documento | 29 páginas, 16 tablas, 1 figura |

---

## 3. Conceptos teóricos y lenguaje técnico esencial

Cada término trae su definición y **dónde aparece en el sistema**. Usen estas palabras exactas en la sustentación.

| Término | Definición | En nuestro sistema |
|---|---|---|
| **Sistema de producción** | Modelo basado en reglas SI condición ENTONCES acción que opera sobre una memoria de trabajo | Todo el programa |
| **Sistema experto** | Software de apoyo a la decisión que imita el razonamiento de un experto en un dominio acotado | Diagnóstico de servidores web |
| **Base de conocimiento** (base de reglas) | Conocimiento del dominio: reglas, y aquí también el catálogo de hechos | `base_conocimiento.json` |
| **Memoria de trabajo** (base de hechos) | Hechos conocidos: los iniciales y los inferidos | Diccionario `memoria = {hecho: ciclo}` en `motor_inferencia_avanzado` (línea 131) |
| **Hecho** | Afirmación verdadera sobre el problema | `cpu_alta`, `diag_ddos`, etc. Tipos: sintoma, intermedio, diagnostico, severidad, recomendacion |
| **Regla / antecedente / consecuente** | SI (antecedentes, en conjunción) ENTONCES (consecuentes) | `"antecedentes": [...]`, `"consecuentes": [...]` |
| **Motor de inferencia** | Mecanismo general que decide qué reglas aplicar; no contiene conocimiento del dominio | `motor_inferencia_avanzado` |
| **Shell (concha)** | Lo que queda al quitar el conocimiento del dominio: motor + interfaz + explicación | `sistema_experto.py`: con otro JSON sirve para otro dominio |
| **Emparejamiento** (*matching*) | Comparar los antecedentes de cada regla con la memoria de trabajo | `set(regla["antecedentes"]).issubset(memoria)` |
| **Conjunto de conflicto** | Reglas no disparadas cuyos antecedentes están todos en la memoria | Lista `reglas_aplicables` |
| **Resolución de conflictos / estrategia de control** | Criterio para elegir una regla del conjunto de conflicto | `resolver_conflicto` (línea 82) |
| **Disparar una regla** | Ejecutarla: sus consecuentes entran a la memoria de trabajo | `memoria[consecuente] = ciclo` |
| **Refracción** | Una regla no se vuelve a disparar con los mismos hechos | `reglas_disparadas` (Rolston 4, Bigus 1, Rete) |
| **Prioridad** (*salience*) | Importancia que el experto asigna a la regla | Campo `prioridad` (Rete, MYCIN, Drools) |
| **Recencia** | Preferir reglas cuyos antecedentes entraron más recientemente | Puntaje = ciclo del antecedente más nuevo (Bigus 2, Rolston 3) |
| **Especificidad** | Preferir la regla con más antecedentes | `len(antecedentes)` (Bigus 3, Rolston 2) |
| **Azar con semilla** | Desempate aleatorio pero reproducible | `random.Random(2026).choice(...)` (Bigus 4, Rolston 5) |
| **Filtro lexicográfico** | Aplicar criterios en orden; cada uno solo desempata lo que el anterior dejó empatado | Bucle de `resolver_conflicto` |
| **Encadenamiento hacia adelante** | Búsqueda guiada por los datos: de los hechos a las conclusiones | Lo que hace nuestro motor |
| **Encadenamiento hacia atrás** | Búsqueda guiada por metas: de una hipótesis a los hechos que la soportan | No implementado (trabajo futuro) |
| **Encadenamiento de reglas** | El consecuente de una regla es antecedente de otra | 18 reglas; ver Figura 1 del informe |
| **Monotonía** | Los hechos solo se agregan, nunca se retiran | Por eso el orden no cambia el conjunto final |
| **Condición de parada** | Cuándo termina la inferencia | Conjunto de conflicto vacío |
| **Módulo de explicación** | Justifica cómo se llegó a una conclusión (popularizado por MYCIN) | Secciones 3 y 4 del reporte |
| **Traza** | Registro de cada ciclo del razonamiento | Lista `traza` y sección 5 del reporte |
| **Representación declarativa / procedimental** | Declarativa: el *qué* como datos. Procedimental: el *cómo* como código | La `lambda accion` (procedimental) se reemplazó por el `tipo` del hecho (declarativo) |
| **Supuesto de mundo cerrado** | Lo que no está en la memoria se trata como no cierto | Un síntoma no reportado no entra a la memoria |
| **Rete** | Algoritmo de emparejamiento incremental (Forgy, 1982) usado por CLIPS, Drools y Jess | Referencia teórica de los criterios |
| **Factores de certeza** | Grado de creencia en una conclusión (MYCIN) | Siguiente tema del curso, trabajo futuro |

**Distinción clave que suelen preguntar:** la **prioridad** es un concepto de **control** (en qué orden se disparan las reglas). La **severidad** es una **conclusión del dominio**, un hecho (`incidente_critico`). No hay que confundirlas.

---

## 4. Los 5 requisitos del taller y cómo se cumplieron

| Requisito | Cómo se cumplió | Dónde mostrarlo |
|---|---|---|
| 1. Base de conocimiento desde archivo (definir codificación) | JSON con esquema propio y validación al cargar | `base_conocimiento.json`; `cargar_base_conocimiento` (línea 29); Tabla 5 del informe |
| 2. Otros elementos en la resolución de conflictos | Prioridad, recencia y azar con semilla, además de refracción y especificidad; orden configurable | `resolver_conflicto` (línea 82); bloque `"estrategia"` del JSON; Tablas 7 y 13 |
| 3. Ingresar hechos al ejecutar | Cuestionario por categorías, lista numerada o `--caso` | `ingresar_hechos` (línea 286); `cargar_caso` (línea 307) |
| 4. Reporte que documente el proceso y apoye la decisión | Reporte de 6 secciones en consola y en `.md`; el informe Word lo documenta | `generar_reporte` (línea 377); capítulo 3 del informe |
| 5. Caso de informática con al menos 15 reglas encadenadas | 25 reglas, 18 encadenadas y cadenas de 4 niveles | Tabla 6 y Figura 1; `pruebas.py` |

---

## 5. Análisis del código original (`sistexpmotorinf2026.py`)

Qué hacía bien: encadenamiento hacia adelante con el ciclo emparejar → conjunto de conflicto → resolver → disparar → repetir; reglas declarativas (diccionarios); refracción que garantiza la terminación.

**Los 9 hallazgos** (Tabla 3 del informe):

1. **Toma los hechos de las claves del diccionario sin mirar el valor** (`hechos = set(datos_iniciales.keys())`). El "Paciente 1" tiene todo en `False` y aun así el motor concluye `posible_resfriado` y `necesita_descanso`. **Es lo primero que conviene mostrar en la demo.**
2. **La recencia (criterio c) no está implementada:** `hechos_nuevos` se llena pero nunca se usa.
3. **El desempate no es al azar:** `sort` es estable, así que gana la primera regla del archivo (Rolston 1).
4. `hechos_nuevos` no guarda el ciclo de ingreso, de modo que no se puede medir qué tan reciente es un hecho.
5. La refracción es por índice: cada regla se dispara una sola vez. Se conservó.
6. Reglas dentro del código y acciones como `lambda`, que no se pueden guardar en un archivo.
7. No hay módulo de explicación; solo `print`.
8. Retorna `list(hechos)` sin orden y mezclando hechos iniciales con inferidos.
9. Reglas redundantes: *Tiene Fiebre* y *Tiene Fiebre Alta* tienen el mismo antecedente.

**Qué cambió (original → nuevo):**

| Aspecto | Original | Nuevo |
|---|---|---|
| Firma | `motor_inferencia_avanzado(datos_iniciales, reglas)` | `motor_inferencia_avanzado(hechos_iniciales, base, criterios, semilla, mostrar)` |
| Memoria de trabajo | `set` de hechos | `dict {hecho: ciclo de ingreso}` |
| `hechos_nuevos` | Conjunto sin uso | Eliminado; lo reemplaza el ciclo guardado en la memoria |
| Reglas | Lista en el código | Archivo JSON validado |
| Acción | `lambda` que imprime | `tipo` del hecho concluido + `texto` |
| Resolución | `sort` por número de antecedentes | Filtro lexicográfico configurable que registra el criterio decisivo |
| Entrada | Diccionario fijo (cuenta las claves) | Interactiva o archivo; solo cuentan los `True` |
| Salida | `print` + `list(hechos)` | `(memoria, traza)` + reporte de 6 secciones |

---

## 6. Decisiones tomadas: qué, alternativas y por qué

| Paso | Decisión | Alternativas consideradas | Justificación para defenderla |
|---|---|---|---|
| 1. Caso | **Servidor / app web** (opción 4) | Fallas de PC, ciberseguridad, fallas de red (repetía el taller anterior) | Síntomas observables y conclusiones que se encadenan en niveles (hallazgo → diagnóstico → severidad → acción); es un problema real de operación |
| 2. Codificación | **JSON** | Texto propio SI/ENTONCES, CSV, YAML | Estándar, legible, soportado por la biblioteca estándar (`json`), sin dependencias, jerárquico (permite metadatos como tipo, pregunta y explicación). YAML requiere PyYAML; CSV no maneja bien listas ni textos largos |
| 3. Reglas | **25 reglas en 4 niveles**, aprobadas tal cual | Compactar a 18 reglas metiendo la recomendación como campo | Las reglas de recomendación aparte agregan un nivel de encadenamiento y hacen explícita la cadena |
| 4. Estrategia | **Refracción → prioridad → recencia → especificidad → azar**, configurable | Estrategia propia de clase (con relevancia), combinada completa | Prioridad por impacto en el negocio; recencia para seguir la línea de razonamiento actual; especificidad para la regla más informada; azar reproducible. Configurable para comparar |
| 5. Ingreso | **Cuestionario por categorías + lista numerada** (combinación pedida por el grupo) + `--caso` | Una pregunta por síntoma, interfaz gráfica | El cuestionario reduce preguntas; la lista es rápida; el archivo permite repetir pruebas |
| 6. Reporte | **Word con la plantilla ASI** como informe; el programa genera el reporte en consola y `.md` | HTML, texto plano | Formato académico exigido; el `.md` del programa es evidencia de cada ejecución |
| 7. Pruebas | **6 casos + `pruebas.py`** automático | Solo casos manuales, o 3 casos | Resultados esperados en cada caso, cobertura de las 25 reglas y comparación de estrategias |
| 8. Prioridades | **No ajustarlas; documentar el hallazgo** (A2) | Subir R02 y R04 a 10 | Se conserva la base aprobada y se documenta la mejora con evidencia (simulación) |

---

## 7. La codificación JSON (base de conocimiento)

Estructura del archivo `base_conocimiento.json`:

```json
{
  "dominio": "...", "version": "1.0",
  "estrategia": {"criterios": ["prioridad", "recencia", "especificidad", "azar"], "semilla": 2026},
  "hechos": {
    "cpu_alta":  {"tipo": "sintoma", "categoria": "CPU y tráfico",
                  "pregunta": "¿El uso de CPU ... supera el 90 %...?", "texto": "Uso de CPU sostenido..."},
    "diag_ddos": {"tipo": "diagnostico", "texto": "Posible ataque de denegación de servicio (DDoS)"}
  },
  "reglas": [
    {"id": "R10", "nombre": "Posible ataque DDoS", "prioridad": 10,
     "antecedentes": ["sobrecarga_cpu", "trafico_origen_concentrado"],
     "consecuentes": ["diag_ddos"],
     "explicacion": "Una sobrecarga producida por tráfico de pocas IP ... sugiere un ataque..."}
  ]
}
```

- **El tipo va en el hecho, no en la regla.** Así el reporte agrupa automáticamente síntomas, diagnósticos, etc.
- `pregunta` existe solo en los síntomas, porque es lo que se le pregunta al usuario. `texto` es lo que se muestra en el reporte; en las recomendaciones, es la acción sugerida.
- **Validaciones al cargar** (`cargar_base_conocimiento`, líneas 29-63): que existan las secciones `hechos` y `reglas`, que cada hecho tenga un tipo válido, que los síntomas tengan pregunta, que no haya ids de regla repetidos, que toda regla use solo hechos definidos y que los criterios de la estrategia sean válidos. Si algo falla, lanza un `ValueError` con un mensaje claro.
- **Para agregar una regla** basta con editar el JSON, sin tocar el código. Eso es tener un **shell**.

---

## 8. La base de reglas y el encadenamiento

**Niveles:**
- **Nivel 1, síntomas → intermedios:** R01 presión de memoria, R02 servicio degradado, R03 servicio caído, R04 sobrecarga de CPU, R05 cuello de botella en BD, R06 escritura bloqueada.
- **Nivel 2, intermedios (+ síntomas) → diagnósticos:** R07 fuga de memoria, R08 caída por OOM, R09 pico legítimo, R10 DDoS, R11 saturación BD, R12 logs sin rotación, R13 regresión por despliegue, R14 certificado inválido.
- **Nivel 3, severidad:** R15 (servicio caído) y R16 (DDoS + servicio degradado) concluyen `incidente_critico`.
- **Nivel 4, recomendaciones:** R17 a R25, una por diagnóstico, más R25 para el incidente crítico.

**Cómo explicar el encadenamiento:** "El consecuente `sobrecarga_cpu` de R04 es antecedente de R09 y R10; el consecuente `diag_ddos` de R10 es antecedente de R16 y R20; el consecuente `incidente_critico` de R16 es antecedente de R25."

**R15 y R16 concluyen el mismo hecho.** Nuestro formalismo solo tiene conjunciones (∧) en el antecedente, así que un **O lógico** se representa con **dos reglas con el mismo consecuente**: incidente crítico ⇐ servicio caído **o** (DDoS ∧ servicio degradado).

**¿Cómo distinguen pico legítimo de DDoS?** Las dos reglas parten de `sobrecarga_cpu`, pero R09 exige `evento_o_campana` y R10 exige `trafico_origen_concentrado`. Si ambos síntomas están presentes, se reportan los dos diagnósticos y el administrador decide; el sistema apoya la decisión, no la reemplaza.

**Cadenas por caso de prueba:**

| Caso | Reglas en orden de disparo | Niveles |
|---|---|---|
| ddos | R02 R04 R10 R16 R25 R20 | 4 |
| memoria | R01 R07 R17 R08 R18 | 3 |
| caida_disco | R03 R15 R25 R06 R12 R22 | 3 |
| bd_despliegue | R02 R13 R23 R05 R11 R21 | 3 |
| pico_certificado | R04 R09 R19 R14 R24 | 3 |
| sin_diagnostico | ninguna | 0 |

---

## 9. Flujo del motor de inferencia

```
             +----------------------------------+
             | 1. cargar_base_conocimiento(JSON) |  valida estructura
             +----------------+-----------------+
                              v
             +----------------------------------+
             | 2. ingresar_hechos / cargar_caso  |  solo los True -> memoria {hecho: 0}
             +----------------+-----------------+
                              v
     +---------------> 3. ciclo += 1
     |                  EMPAREJAMIENTO: reglas no disparadas con
     |                  antecedentes ⊆ memoria -> conjunto de conflicto
     |                        |
     |                 ¿conjunto vacío? --- sí ---> 7. FIN -> generar_reporte
     |                        | no
     |                        v
     |                 4. RESOLUCIÓN DE CONFLICTOS (resolver_conflicto)
     |                  prioridad -> recencia -> especificidad -> azar
     |                        v
     |                 5. ACCIÓN: marcar la regla como disparada;
     |                  consecuentes nuevos -> memoria[c] = ciclo
     |                        v
     |                 6. registrar paso en la TRAZA
     +------------------------+
```

**Pseudocódigo fiel al código** (`motor_inferencia_avanzado`, línea 131):

```python
memoria = {hecho: 0 for hecho in hechos_iniciales}      # solo hechos verdaderos
reglas_disparadas, traza, ciclo = set(), [], 0
while True:
    ciclo += 1
    aplicables = [(i, r) for i, r in enumerate(reglas)
                  if i not in reglas_disparadas                   # refracción
                  and set(r["antecedentes"]).issubset(memoria)]   # emparejamiento
    if not aplicables:
        break                                                    # condición de parada
    (i, regla), decision = resolver_conflicto(aplicables, memoria, criterios, azar)
    reglas_disparadas.add(i)                                     # disparo
    nuevos = [c for c in regla["consecuentes"] if c not in memoria]
    for c in nuevos:
        memoria[c] = ciclo                                       # se guarda el ciclo (para la recencia)
    traza.append({...ciclo, conjunto, regla, decision, nuevos...})
return memoria, traza
```

**¿Por qué termina siempre?** Cada ciclo dispara exactamente una regla, la refracción impide repetirla y hay 25 reglas. Por eso hay como máximo 25 ciclos con disparo y luego un ciclo que encuentra el conjunto vacío. La memoria además es monótona: solo crece.

**Complejidad:** en cada ciclo se revisan todas las reglas, O(R·A); en total, O(R²·A). Con 25 reglas es trivial. Rete evita revisar todo en cada ciclo porque hace emparejamiento incremental.

---

## 10. Estrategia de resolución de conflictos (el tema más importante)

### 10.1 Cómo funciona `resolver_conflicto` (línea 82)

1. Si hay una sola regla aplicable, se elige y el criterio queda como "única aplicable".
2. Para cada criterio, en el orden configurado, se calcula el puntaje de cada candidata (`valor_criterio`, línea 69) y se **conservan solo las que tienen el mejor puntaje**.
   - **prioridad** = campo `prioridad` de la regla
   - **recencia** = `max(ciclo de cada antecedente)`, es decir, el ciclo del antecedente más nuevo
   - **especificidad** = número de antecedentes
3. Si queda una sola, ese es el **criterio decisivo**, y se registran los puntajes de cada paso.
4. Si llega a `azar`, se sortea con `random.Random(semilla)`. La misma semilla produce los mismos sorteos, así que el resultado es **reproducible**. Sin semilla no lo sería.
5. Si no se configuró `azar`, se toma la primera según el orden del archivo (Rolston 1).

> **¿Por qué un filtro y no un `sort`?** Un `sort` por la tupla (prioridad, recencia, especificidad) elige lo mismo, pero el filtro permite saber **qué criterio deshizo el empate**, y esa información alimenta la explicación.

**La refracción** no es un criterio de orden: es un **filtro previo**, porque las reglas disparadas ni siquiera entran al conjunto de conflicto.

### 10.2 Ejemplo trabajado: caso `ddos.json` (Tabla 11 del informe)

Síntomas: `cpu_alta`, `trafico_alto`, `trafico_origen_concentrado`, `respuesta_lenta`, `errores_5xx`.

| Ciclo | Conjunto de conflicto | Elegida | Por qué |
|---|---|---|---|
| 1 | R02, R04 | **R02** | Prioridad 5 = 5; recencia 0 = 0; especificidad 2 = 2 → **azar** (semilla 2026) |
| 2 | R04 | R04 → `sobrecarga_cpu` | Única aplicable |
| 3 | R10 | R10 → `diag_ddos` (entra en el ciclo 3) | Única aplicable |
| 4 | R16, R20 | **R16** → `incidente_critico` | Prioridad 10 = 10; recencia 3 = 3; **especificidad 2 > 1** |
| 5 | R20, R25 | **R25** → `rec_plan_contingencia` | Prioridad 10 = 10; **recencia: R25 usa `incidente_critico` (ciclo 4), más nuevo que `diag_ddos` (ciclo 3)** |
| 6 | R20 | R20 → `rec_mitigar_ataque` | Única aplicable |
| 7 | (vacío) | — | Fin |

Este caso muestra **azar, especificidad y recencia** decidiendo. La **prioridad** decide en el caso `caida_disco`: R03 (10) frente a R06 (7), luego R15 (10) frente a R06 (7) y luego R25 (10) frente a R06 (7). El sistema atiende primero la caída y deja el disco para después. También decide en el caso combinado: R01 (7) frente a R02 y R04 (5). En el caso `memoria` la prioridad **no** decide, porque R07 y R08 tienen ambas 7: ahí deciden el **azar** (R07 frente a R08) y la **recencia** (R17 frente a R08).

### 10.3 Comparación de estrategias (Tabla 13) y hallazgo

Caso combinado (síntomas de ddos + memoria):

| Orden de criterios | Secuencia | Primer diagnóstico | Incidente crítico |
|---|---|---|---|
| prioridad → recencia → especificidad → azar | R01 R07 R17 R08 R18 R04 R10 R20 R02 R16 R25 | ciclo 2 | **ciclo 10** |
| recencia → prioridad → especificidad → azar | (igual) | ciclo 2 | ciclo 10 |
| solo especificidad | R01 R02 R04 R07 R08 R10 R16 R17 R18 R20 R25 | ciclo 4 | **ciclo 7** |
| Simulación con R02 y R04 en prioridad 10 | R02 R04 R10 R16 R25 R20 R01 R08 R18 R07 R17 | ciclo 3 | **ciclo 4** |

**Conclusiones que hay que saber decir:**
1. **Las tres estrategias llegan al mismo conjunto final de hechos.** El sistema es **monótono**, tiene **refracción** y **corre hasta agotar las reglas**, así que toda regla que llega a ser aplicable termina disparándose. La estrategia cambia el **orden**, no el **resultado final**.
2. El orden importa si el sistema **se detuviera en la primera conclusión crítica** o si las acciones **modificaran la memoria** (sistemas no monótonos).
3. **Hallazgo:** con la prioridad primero, el incidente crítico sale **tarde** porque la cadena crítica pasa por **R02 y R04, que tienen prioridad 5**, mientras que las reglas de memoria tienen 7. **La prioridad de una regla intermedia debería reflejar la de la conclusión más crítica a la que lleva.** Se simuló y no se aplicó, por decisión del grupo.
4. Recencia-primero dio la misma secuencia porque, tras R01, las reglas que usan su hecho nuevo (R07 y R08) también son las de mayor prioridad: los dos criterios coinciden.

**Cómo demostrarlo en vivo:** `python sistema_experto.py --caso casos/ddos.json --criterios especificidad`

---

## 11. Ingreso de hechos (memoria de trabajo)

- Al iniciar se elige entre **1. Cuestionario guiado por categorías** y **2. Lista numerada de síntomas** (`ingresar_hechos`, línea 286).
  - **Cuestionario** (`ingresar_por_categorias`, línea 243): pregunta "¿Observa problemas de MEMORIA?" y solo si la respuesta es sí pregunta por cada síntoma de esa categoría. Pasa de 18 a unas 6-10 preguntas.
  - **Lista** (`ingresar_por_lista`, línea 257): el usuario escribe los números separados por comas, por ejemplo `1, 2, 5, 6, 7`.
  - **Archivo** (`--caso`, `cargar_caso`, línea 307): `{"descripcion": "...", "sintomas": [...]}`. Valida que todo sea un síntoma de la base.
- **Validación:** solo acepta s/n (`preguntar_si_no`, línea 223) y números dentro del rango, y al final pregunta "¿Los datos son correctos?" para que el usuario corrija.
- **Solo los `True` entran a la memoria, con ciclo 0.** Esto corrige el hallazgo 1 del código original.
- **Detalle técnico** (por si preguntan por robustez): PowerShell antepone un **BOM** (`﻿`) al redirigir la entrada. `leer_entrada` (línea 215) lo limpia y termina de forma ordenada si la entrada se acaba (`EOFError`).

**Numeración de la lista**, útil para la demo:
1 respuesta_lenta · 2 errores_5xx · 3 sitio_no_disponible · 4 proceso_web_detenido · 5 cpu_alta · 6 trafico_alto · 7 trafico_origen_concentrado · 8 evento_o_campana · 9 memoria_alta · 10 swap_activa · 11 memoria_crece_sin_liberarse · 12 oom_en_logs · 13 disco_lleno · 14 logs_crecen_rapido · 15 consultas_lentas_bd · 16 conexiones_bd_agotadas · 17 despliegue_reciente · 18 alerta_certificado

---

## 12. Módulo de explicación y reporte

**Estructura del reporte del programa** (consola + `reportes/reporte_<caso>_<fecha>.md`):

| Sección | Qué responde | Función |
|---|---|---|
| Encabezado | Fecha, base, modo de ingreso, estrategia y semilla | `generar_reporte` (377) |
| 1. Datos del caso | ¿Qué se observó? (síntomas reportados y descartados) | — |
| 2. Resumen para la toma de decisiones | ¿Qué tengo y qué hago? Severidad, diagnósticos y recomendaciones **por prioridad**; si no hay diagnóstico: "consulte con un técnico" | `conclusiones_por_tipo` (339) |
| 3. Explicación | **¿Cómo se llegó?** Árbol desde cada conclusión hasta los síntomas, con regla, ciclo y `explicacion` | `justificaciones` (325), `arbol_explicacion` (345) |
| 4. Hipótesis por confirmar | **¿Por qué no?** ¿Qué conviene verificar? | `hipotesis_por_confirmar` (363) |
| 5. Traza | ¿Cómo razonó el motor? Ciclo, conjunto, regla, criterio decisivo y hechos nuevos | `describir_decision` (114) |
| 6. Memoria final | ¿Qué sabe al final? Hecho, tipo y ciclo | — |

**Algoritmos que hay que poder explicar:**
- **Árbol "¿cómo?":** `justificaciones` arma el mapa *hecho → paso de la traza que lo agregó*. `arbol_explicacion` toma la regla de ese paso y baja **recursivamente** por sus antecedentes hasta llegar a los síntomas ("síntoma reportado"). Si un diagnóstico ya se explicó, la severidad dice "ver su explicación arriba".
- **"También respaldado por":** `respaldos` lista todas las reglas que concluyeron un hecho, incluso las que se dispararon sin aportar nada nuevo.
- **Hipótesis "¿por qué no?":** reglas **no disparadas**, con **al menos 2 antecedentes**, a las que les falta **exactamente un síntoma** y cuya conclusión aún no se tiene. Ejemplo en ddos: "Para concluir *Pico de demanda legítimo* (R09) solo falta verificar: ¿hay una campaña o evento…?". Indica si el usuario dijo "no" o si el dato no fue informado.
- **Orden de las recomendaciones:** por la prioridad de la regla que las concluyó y, en empate, por ciclo.

---

## 13. Guion de demostración para la sustentación

Ejecutar dentro de la carpeta `codigo/` (`cd codigo`), en PowerShell o CMD (Python 3, sin librerías adicionales).

1. **El error del código original:**
   `python sistexpmotorinf2026.py`
   Muestren que con todos los datos en `False` concluye `posible_resfriado` y `necesita_descanso`: "por eso solo cargamos los hechos verdaderos".
2. **Modo interactivo con lista (caso DDoS):**
   `python sistema_experto.py` → opción `2` → escribir `1, 2, 5, 6, 7` → `s`
   Recorran la traza: azar en el ciclo 1, especificidad en el 4, recencia en el 5. Luego el resumen: severidad crítica, diagnóstico DDoS y 2 recomendaciones. Luego el árbol de explicación y las hipótesis.
3. **Modo cuestionario (caída con disco lleno), donde decide la prioridad:**
   `python sistema_experto.py` → opción `1` → Disponibilidad `s` → respuesta lenta `n`, errores 5xx `n`, sitio no carga `s`, proceso detenido `s` → CPU `n` → Memoria `n` → Disco `s` → disco lleno `s`, logs `s` → Base de datos `n` → Cambios `n` → confirmar `s`
   En los ciclos 1, 2 y 3 decide la **prioridad**: R03, R15 y R25 (10) le ganan a R06 (7). Resultado: incidente crítico + logs sin rotación, con plan de contingencia y rotación de logs.
   *(Variante: con `s` solo en Memoria y sus 4 síntomas sale fuga de memoria + caída por OOM; ahí deciden el azar y la recencia.)*
4. **Cambiar la estrategia sin tocar el código:**
   `python sistema_experto.py --caso casos/ddos.json --criterios especificidad`
   Al final cambia el orden: R20 se dispara antes que R25, porque sin recencia el empate entre ellas se resuelve por el orden del archivo. Las conclusiones finales son las mismas.
5. **Pruebas automáticas:**
   `python pruebas.py` → 6/6 casos, 25/25 reglas, tabla de comparación y "TODAS LAS PRUEBAS PASARON".
6. **Mostrar el reporte generado:** abrir el `.md` más reciente en `reportes/` (o `reportes/pruebas/reporte_ddos.md`).
7. **(Opcional) Mostrar la validación:** cambiar en el JSON un antecedente por un nombre inexistente → al ejecutar sale `ValueError: La regla Rxx usa el hecho '...', que no está definido.` **Recuerden deshacer el cambio.**

---

## 14. Preguntas probables y respuestas

1. **¿Qué es el conjunto de conflicto y cómo lo calculan?** Son las reglas no disparadas cuyos antecedentes están todos en la memoria de trabajo. Se calcula con `set(antecedentes).issubset(memoria)`, filtrando las que ya están en `reglas_disparadas`.
2. **¿Qué estrategia usan y por qué en ese orden?** Refracción como filtro; luego prioridad (lo más importante para el negocio va primero), recencia (sigue la línea de razonamiento recién abierta), especificidad (prefiere la regla más informada) y azar con semilla para el empate final reproducible.
3. **¿Cómo implementaron la recencia?** La memoria guarda el ciclo en que entró cada hecho (los iniciales en el 0). El puntaje de una regla es el ciclo de su antecedente más reciente; gana el mayor.
4. **¿Qué pasa si dos reglas empatan en todo?** Decide el azar con `random.Random(2026)`, que es reproducible. Si se quita `azar` de los criterios, gana la primera según el orden del archivo.
5. **¿Por qué JSON?** Es estándar, legible, sin dependencias (`json` es de la biblioteca estándar) y jerárquico. Permite guardar tipo, pregunta, texto, prioridad y explicación. La "codificación" es nuestro esquema: qué campos hay y qué significan (Tabla 5).
6. **¿Dónde se ve el encadenamiento?** En la Figura 1 y en la traza: R04 produce `sobrecarga_cpu`, que habilita R10; R10 produce `diag_ddos`, que habilita R16 y R20; R16 produce `incidente_critico`, que habilita R25. Son 18 reglas encadenadas y 4 niveles.
7. **¿Cómo evitan ciclos infinitos?** Con la refracción: cada regla se dispara una vez. Con 25 reglas hay como máximo 25 disparos, y además la memoria es monótona.
8. **¿Hacia adelante o hacia atrás? ¿Por qué?** Hacia adelante, porque el administrador parte de los síntomas y no sabe cuál es la falla. Hacia atrás convendría para comprobar una hipótesis concreta y preguntar solo lo necesario (trabajo futuro).
9. **¿Qué es la memoria de trabajo en el código?** El diccionario `memoria = {hecho: ciclo}`.
10. **¿Si cambian el orden de los criterios cambian los diagnósticos?** No cambia el conjunto final (sistema monótono, refracción, se ejecuta hasta agotar las reglas). Cambia el orden y el momento en que aparece cada conclusión. Ejemplo: incidente crítico en el ciclo 10 o en el ciclo 7.
11. **¿Qué diferencia hay entre prioridad y severidad?** La prioridad es control: orden de disparo. La severidad es una conclusión del dominio, el hecho `incidente_critico`.
12. **¿Qué hace el sistema si no hay diagnóstico?** Lo dice ("No se identificó el problema; consulte con un técnico") y muestra las hipótesis por confirmar (caso `sin_diagnostico`).
13. **¿Cómo agregarían una regla nueva?** Agregando el objeto en `reglas` y, si hay hechos nuevos, en `hechos`. La validación avisa si falta algo. El código no se toca, porque es un shell.
14. **¿Cómo se construye la explicación?** A partir de la traza: para cada conclusión se toma la regla que la produjo y se baja recursivamente por sus antecedentes hasta los síntomas.
15. **¿Qué son las hipótesis por confirmar?** Las reglas a las que les falta un solo síntoma: el siguiente dato que conviene verificar. Responden al "¿por qué no concluyó X?".
16. **¿Por qué R15 y R16 concluyen lo mismo?** Para representar una disyunción (O) en un formalismo que solo admite conjunciones en el antecedente.
17. **¿Cómo pueden manejar la negación ("no hay tráfico alto")?** No la manejamos: trabajamos con hechos positivos (supuesto de mundo cerrado). Por eso modelamos `evento_o_campana` como hecho positivo para distinguir pico legítimo de DDoS.
18. **¿Por qué el desempate al azar usa semilla?** Para que la misma entrada produzca siempre la misma traza; así las pruebas y la sustentación son repetibles.
19. **¿Qué validan las pruebas?** Que cada caso produzca exactamente los diagnósticos, severidad, recomendaciones y reglas esperados (definidos dentro del JSON del caso); la cobertura de las 25 reglas, y la profundidad de las cadenas.
20. **¿Cómo calculan la profundidad de la cadena?** Recursivamente: un síntoma vale 0 y un hecho inferido vale 1 + la máxima profundidad de los antecedentes de la regla que lo produjo (`profundidad` en `pruebas.py`).
21. **¿Por qué la prioridad de DDoS es 10?** Porque es un problema de seguridad que afecta la disponibilidad; la escala de impacto es 10 seguridad y caídas, 7 memoria y disco (riesgo de caída), 5 rendimiento y 3 mantenimiento.
22. **¿Qué limitaciones tiene?** No maneja incertidumbre (todo es sí o no), no tiene negación, es monótono, el conocimiento no fue validado por un experto externo y la prioridad de las reglas intermedias está subestimada (hallazgo).
23. **¿Qué mejorarían?** Factores de certeza (MYCIN, siguiente tema del curso), encadenamiento hacia atrás, propagar la prioridad a lo largo de las cadenas o detenerse en la primera conclusión crítica, una interfaz gráfica y la validación con un experto.
24. **¿Qué tiene que ver con Rete?** De Rete tomamos los criterios de conflicto (refracción, recencia, especificidad, prioridad). Nuestro emparejamiento no es incremental como el de Rete: revisa todas las reglas en cada ciclo, lo que es suficiente para 25 reglas.
25. **¿Qué hizo la IA y qué hicieron ustedes?** La IA propuso opciones, implementó el código y redactó borradores. Nosotros tomamos cada decisión de diseño (caso, JSON, estrategia, ingreso, reporte, pruebas, no ajustar prioridades) y revisamos los resultados. Todo está en la bitácora (capítulo 4) y en el flujo de prompts (Anexo A).

---

## 15. Estructura del resultado entregado

### 15.1 Archivos

| Archivo | Para qué |
|---|---|
| `entrega/Informe_Taller_Sistema_Experto.docx` | **Informe de entrega** con la plantilla ASI (29 páginas) |
| `codigo/sistema_experto.py` | Motor + carga + ingreso de hechos + explicación + `main` |
| `codigo/base_conocimiento.json` | Base de conocimiento (estrategia, 42 hechos, 25 reglas) |
| `codigo/casos/*.json` | 6 casos con resultados esperados |
| `codigo/pruebas.py` | Pruebas automáticas y comparación de estrategias |
| `codigo/reportes/pruebas/*.md` | Evidencia: un reporte por caso + `resumen_pruebas.md` |
| `codigo/sistexpmotorinf2026.py` | Motor original de la clase |
| `documentacion/guia_sustentacion.md` | Esta guía |
| `documentacion/bitacora_ia.md` | Bitácora de IA (con la columna "resultado obtenido") |
| `documentacion/figuras/grafo_encadenamiento.png` | Figura 1 |
| `material_clase/` | Contexto del curso y plantilla Word ASI |

### 15.2 Estructura del informe Word (páginas según el índice)

| Sección | Pág. | Contenido clave |
|---|---|---|
| Portada | 1 | Título, integrantes, profesor, UNAL Manizales, 2026 |
| Resumen y palabras clave | 2 | Unas 230 palabras; 6 palabras clave |
| Contenido | 3 | Tabla de contenido automática |
| Introducción | 5 | Contexto, objetivo, metodología, alcance, **Tabla 1** (requisitos → secciones) |
| 1. Antecedentes | 7 | Sistemas de producción, encadenamiento, **Tabla 2** (criterios), **Tabla 3** (9 hallazgos) |
| 2. Desarrollo | 10 | Caso (**T4**), codificación (**T5**), reglas (**T6** + **Figura 1**), flujo, estrategia (**T7**), ingreso, reporte (**T8**), archivos (**T9**) |
| 3. Resultados | 18 | Casos (**T10**), caso DDoS (**T11** traza + explicación + hipótesis), decisiones por caso (**T12**), comparación de estrategias (**T13**) |
| 4. Bitácora de IA | 24 | **T14** (herramienta y escala), **T15** (12 interacciones: modelo, prompt, nivel, aprendizaje) |
| 5. Conclusiones | 26 | 7 conclusiones |
| Bibliografía | 28 | APA: Rich y Knight, Rolston, Russell y Norvig, Bigus y Bigus, Buchanan y Shortliffe, Forgy (Rete), etc. |
| Anexo A. Flujo de prompts | 29 | **T16**: prompt inicial → revisión → ajustes → … |

---

## 16. Reparto sugerido de la exposición (opcional)

| Integrante | Temas | Secciones de esta guía |
|---|---|---|
| Integrante 1 | Problema, caso de estudio, codificación JSON, base de reglas y encadenamiento | 4, 7, 8 |
| Integrante 2 | Análisis del código original, flujo del motor, resolución de conflictos y comparación | 5, 9, 10 |
| Integrante 3 | Ingreso de hechos, módulo de explicación, pruebas, demo y bitácora de IA | 11, 12, 13, 14 (#25) |

Todos deben dominar las secciones 1, 2, 3 y 10, porque son las más preguntadas.

---

## 17. Checklist antes de entrar

- [ ] `python pruebas.py` termina con "TODAS LAS PRUEBAS PASARON".
- [ ] Revisaron y ajustaron la columna **Resultado de aprendizaje** de la bitácora: la redactó la IA como borrador.
- [ ] El informe (`entrega/Informe_Taller_Sistema_Experto.docx`, o un PDF exportado desde Word) está subido antes de la clase.
- [ ] Tienen a mano la numeración de la lista de síntomas (sección 11) para la demo.
- [ ] Saben explicar la tabla del caso DDoS ciclo por ciclo (sección 10.2).
- [ ] Saben decir por qué el orden de los criterios no cambia el conjunto final (sección 10.3).
- [ ] Si alguien edita el JSON durante la demo, deshacer el cambio y volver a correr `pruebas.py`.
