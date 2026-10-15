# Sistema experto para el diagnóstico de servidores web

Taller de **Sistemas Inteligentes Computacionales**. Universidad Nacional de Colombia, Sede Manizales.
Profesor: Néstor Darío Duque Méndez.
Integrantes: Jasmin Camila Guitierrez Maya, Mateo Falla Muños, Andres Hernandez.

El sistema extiende el motor de inferencia visto en clase (encadenamiento hacia adelante) con:
- base de conocimiento cargada desde un archivo JSON,
- resolución de conflictos configurable: refracción → prioridad → recencia → especificidad → azar con semilla,
- ingreso de hechos al ejecutar, por cuestionario, lista numerada o archivo de caso,
- módulo de explicación con diagnósticos, recomendaciones, justificación de cada conclusión y traza.

Se aplica al diagnóstico de rendimiento y caídas de un servidor web: 18 síntomas y 25 reglas encadenadas en 4 niveles.

## Estructura

```
├── entrega/          Informe del taller (plantilla ASI)
├── codigo/           Sistema experto ejecutable
│   ├── sistema_experto.py      motor, ingreso de hechos, explicación y reporte
│   ├── base_conocimiento.json  hechos, reglas y estrategia
│   ├── pruebas.py              pruebas automáticas
│   ├── casos/                  6 casos de prueba
│   ├── reportes/pruebas/       evidencia generada por las pruebas
│   └── sistexpmotorinf2026.py  motor original de clase (referencia)
├── documentacion/    Guía de sustentación, bitácora de IA y figuras
└── material_clase/   Contexto del curso y plantilla Word
```

## Ejecución

Requiere Python 3, sin librerías adicionales.

```
cd codigo
python sistema_experto.py                                  # modo interactivo
python sistema_experto.py --caso casos/ddos.json           # caso desde archivo
python sistema_experto.py --caso casos/ddos.json --criterios especificidad
python pruebas.py                                          # pruebas automáticas
```

Cada ejecución guarda su reporte en `codigo/reportes/`.
