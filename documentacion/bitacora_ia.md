# Bitácora de uso de IA

Registro de las interacciones con IA durante el taller. Es la misma información del capítulo 4 y del Anexo A de `entrega/Informe_Taller_Sistema_Experto.docx`, más la columna "Resultado obtenido". Las entradas 13 a 15 son posteriores a la generación del informe.

- **Herramienta:** Claude Code (CLI), con acceso a los archivos del proyecto
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Fecha:** 14 de octubre de 2026
- **Escala de nivel de intervención de la IA:**
  - *Bajo:* la IA solo explica o consulta; el grupo decide y produce.
  - *Medio:* la IA propone opciones o borradores; el grupo elige, corrige y ajusta.
  - *Alto:* la IA genera el producto; el grupo revisa y valida.
- **Nota:** los resultados de aprendizaje los redactó la IA como borrador, a solicitud del grupo (decisión B1), y están pendientes de revisión por los integrantes.

---

## Registro

| # | Modelo | Prompt (resumen) | Nivel de intervención | Resultado obtenido | Resultado de aprendizaje |
|---|---|---|---|---|---|
| 1 | Claude Opus 5.5 | **Prompt inicial:** realizar el taller (cargar BC desde archivo, nuevos criterios de resolución de conflictos, ingreso de hechos, reporte y explicación, caso de informática con al menos 15 reglas encadenadas); leer `contexto_sistemas_expertos.md`, preguntar antes de cada paso, incluir bitácora de IA y flujo de prompts. | Medio | La IA leyó el contexto y propuso un plan de 7 pasos. El usuario interrumpió porque quería poder escribir su propia respuesta. | Descomponer un requerimiento amplio en decisiones de diseño verificables (caso, codificación, estrategia, entrada y reporte) antes de programar, siguiendo la metodología de desarrollo de sistemas expertos. |
| 2 | Claude Opus 5.5 | **Ajuste:** preguntas con respuesta abierta y análisis de `sistexpmotorinf2026.py`. | Medio | La IA ejecutó el código original y documentó 9 hallazgos. Las preguntas pasaron a hacerse en texto con opción abierta. | Reconocer las limitaciones del motor base (hechos tomados de las claves aunque valgan False, recencia no implementada, desempate por el orden del archivo) y su efecto sobre la inferencia. |
| 3 | Claude Opus 5.5 | **Decisión paso 1:** "vamos a escoger el caso 4". | Medio | Caso: rendimiento y caídas de un servidor / aplicación web. | Identificar qué hace adecuado un dominio para un sistema experto: síntomas observables y conclusiones que se encadenan en varios niveles. |
| 4 | Claude Opus 5.5 | **Decisión paso 2:** "escogemos la opción 2, JSON". | Medio | Esquema JSON y borrador de 25 reglas en 4 niveles. | Comparar codificaciones del conocimiento y entender por qué las acciones procedimentales (lambdas) deben pasar a una representación declarativa para separar conocimiento y control (shell). |
| 5 | Claude Opus 5.5 | **Decisión paso 3:** "aprobar tal cual". | Alto | `base_conocimiento.json` con 42 hechos y 25 reglas, validado: 18 de 25 reglas encadenadas. | Diseñar reglas por niveles garantiza el encadenamiento; varias reglas con el mismo consecuente representan una disyunción; la consistencia de la base puede validarse automáticamente. |
| 6 | Claude Opus 5.5 | **Decisión paso 4:** "opción 1". | Alto | Estrategia refracción → prioridad → recencia → especificidad → azar (semilla 2026), configurable. Se comprobó que los 4 criterios llegan a decidir. | Implementar la resolución de conflictos como filtro lexicográfico; la recencia exige registrar el ciclo de ingreso de cada hecho y la semilla hace reproducible el desempate. |
| 7 | Claude Opus 5.5 | **Ajuste paso 5:** "crea una opción que contenga la opción 1 y 3". | Medio | Cuestionario por categorías y lista numerada, con confirmación de los datos. Se corrigió el BOM de la entrada redirigida en PowerShell. | Equilibrar número de preguntas y rapidez en la interfaz, validar entradas y confirmar los hechos antes de razonar. |
| 8 | Claude Opus 5.5 | **Ajuste paso 6:** usar la plantilla Word ASI y los nombres de los integrantes. | Medio | Análisis de la plantilla (márgenes, estilos, numeración, títulos de tablas y figuras). La IA pidió aclaraciones. | Reconocer las exigencias de la plantilla institucional basada en la NTC 1486 y APA. |
| 9 | Claude Opus 5.5 | **Ajuste paso 6:** el reporte es el Word, con la bitácora; nombres como se dieron; agregar al profesor; aceptar el contenido completo y `--caso`. | Alto | Módulo de explicación (resumen, árbol "¿cómo?", hipótesis "¿por qué no?", traza, memoria final) y opciones `--caso`, `--criterios` y `--salida`. | Un módulo de explicación debe responder qué se concluyó, cómo se llegó y qué falta verificar; la traza es la evidencia del razonamiento. |
| 10 | Claude Opus 5.5 | **Decisión paso 7:** "1" (6 casos y pruebas automáticas). | Alto | 6/6 casos correctos, 25/25 reglas cubiertas y cadenas de hasta 4 niveles. Hallazgo: con prioridad primero, el incidente crítico se detecta en el ciclo 10 frente al 7. | Validar con casos de resultado esperado y cobertura de reglas; en un sistema monótono el orden de los criterios cambia el momento de las conclusiones, no el conjunto final. |
| 11 | Claude Opus 5.5 | **Decisión paso 8:** "A:2 B:1 C: aprobada". | Medio | No se ajustaron las prioridades (queda como hallazgo documentado), la IA redactó el borrador de aprendizajes y se generó el Word de 29 páginas sobre la plantilla, con índice actualizado y PDF. | Diferenciar entre documentar un hallazgo y modificar la base de conocimiento, y transparentar qué partes redactó la IA. |
| 12 | Claude Opus 5.5 | **Ajuste:** guía de estudio en Markdown para la sustentación. | Alto | `guia_sustentacion.md`. | Sintetizar el trabajo en conceptos, flujo y decisiones para explicarlo con lenguaje técnico. |
| 13 | Claude Opus 5.5 | **Ajuste:** "dame en una carpeta con solo los códigos necesarios". | Alto | Carpeta `codigo_sistema_experto/` con `sistema_experto.py`, `base_conocimiento.json`, `pruebas.py` y `casos/`; se verificó que funciona por sí sola. | Identificar los componentes mínimos de un sistema experto distribuible: el shell (motor), la base de conocimiento y los casos de prueba. |
| 14 | Claude Opus 5.5 | **Ajuste:** "sube todo el proyecto al siguiente repositorio: https://github.com/Hernandez2404/motorinferencia_SIC.git". | Alto | Repositorio inicializado, `.gitignore` (excluye `__pycache__`, `.obsidian/` y reportes de cada ejecución), commit y push a `main`, verificado contra el remoto. | Versionar un proyecto académico: qué incluir y qué excluir (archivos generados y configuración personal). |
| 15 | Claude Opus 5.5 | **Decisión:** "organiza las carpetas del proyecto, están un caos" → opción 1 (estructura propuesta y push). | Medio | Estructura `entrega/`, `codigo/`, `documentacion/` y `material_clase/` con README; se eliminaron los duplicados tras comprobar que eran idénticos; se movieron los archivos con `git mv` y se verificó con `pruebas.py`. | Organizar un proyecto por propósito y separar la entrega, el código ejecutable, la documentación y el material de referencia. |

---

## Flujo de prompts

1. **Prompt inicial** → la IA propone el plan y pregunta por el caso de estudio.
2. **Revisión** → el usuario rechaza el formato de pregunta (quiere escribir su propia respuesta).
3. **Prompt de ajuste 1** → preguntas con respuesta abierta y análisis del código base.
4. **Revisión** → el grupo revisa el análisis y las 4 opciones de caso.
5. **Prompt de decisión (paso 1)** → caso 4: servidor / aplicación web.
6. **Revisión** → comparación de 4 codificaciones.
7. **Prompt de decisión (paso 2)** → JSON.
8. **Revisión** → esquema JSON y borrador de 25 reglas.
9. **Prompt de decisión (paso 3)** → se aprueban las reglas; la IA genera y valida el JSON.
10. **Revisión** → 3 estrategias de resolución de conflictos.
11. **Prompt de decisión (paso 4)** → opción 1; implementación y prueba.
12. **Revisión** → tabla de ciclos con el criterio decisivo; 4 modos de ingreso.
13. **Prompt de ajuste (paso 5)** → combinar cuestionario por categorías y lista numerada.
14. **Revisión** → contenido propuesto del reporte y formatos.
15. **Prompt de ajuste (paso 6)** → plantilla Word y nombres de los integrantes.
16. **Revisión** → la IA pide aclarar "el reporte", la ortografía y los pendientes.
17. **Prompt de ajuste (paso 6)** → reporte = Word con bitácora; nombres como se dieron; profesor; contenido completo y `--caso`.
18. **Revisión** → 6 casos de prueba propuestos.
19. **Prompt de decisión (paso 7)** → pruebas automáticas y hallazgo sobre prioridades.
20. **Revisión** → hallazgo, borrador de aprendizajes y estructura del Word.
21. **Prompt de decisión (paso 8)** → "A:2 B:1 C: aprobada".
22. **Prompt de ajuste** → guía de estudio en Markdown.
23. **Revisión** → la IA genera el Word, el PDF y la guía; queda la revisión final del grupo.
24. **Prompt de ajuste** → carpeta con solo los códigos necesarios.
25. **Revisión** → carpeta `codigo_sistema_experto/` verificada (pruebas 6/6).
26. **Prompt de ajuste** → subir el proyecto al repositorio de GitHub.
27. **Revisión** → push verificado; la IA advierte que el PDF ya no estaba en la carpeta y pregunta si el repositorio es público.
28. **Prompt de decisión** → organizar las carpetas: se aprueba la estructura propuesta y el push (opción 1).
29. **Revisión** → reorganización verificada con `pruebas.py` y publicada en GitHub.
