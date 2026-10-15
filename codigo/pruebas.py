# -*- coding: utf-8 -*-
"""Pruebas automáticas del sistema experto.

Ejecuta todos los casos de la carpeta casos/ sin interacción y verifica:
  1. Que se obtengan los diagnósticos, la severidad, las recomendaciones y las reglas esperadas.
  2. Que entre todos los casos se disparen las 25 reglas de la base de conocimiento.
  3. Que haya encadenamiento: profundidad de la cadena más larga de cada caso.
Además compara el efecto de distintos órdenes de criterios de resolución de conflictos.
Los reportes de cada caso y un resumen quedan en reportes/pruebas/.
"""

import glob
import json
import os

from sistema_experto import (RUTA_BASE_POR_DEFECTO, cargar_base_conocimiento, cargar_caso,
                             generar_reporte, justificaciones, motor_inferencia_avanzado)

CARPETA = os.path.dirname(os.path.abspath(__file__))
CARPETA_CASOS = os.path.join(CARPETA, "casos")
CARPETA_SALIDA = os.path.join(CARPETA, "reportes", "pruebas")


def profundidad(hecho, origen, memo=None):
    """Niveles de reglas encadenadas que hay entre los síntomas (nivel 0) y el hecho."""
    memo = {} if memo is None else memo
    if hecho not in origen:
        return 0
    if hecho not in memo:
        antecedentes = origen[hecho]["regla"]["antecedentes"]
        memo[hecho] = 1 + max(profundidad(a, origen, memo) for a in antecedentes)
    return memo[hecho]


def cadena_mas_larga(hecho, origen):
    """Hechos de la cadena más profunda que termina en el hecho, desde el síntoma."""
    if hecho not in origen:
        return [hecho]
    antecedentes = origen[hecho]["regla"]["antecedentes"]
    mas_profundo = max(antecedentes, key=lambda a: profundidad(a, origen))
    return cadena_mas_larga(mas_profundo, origen) + [hecho]


def de_tipo(base, memoria, tipo):
    return {hecho for hecho in memoria if base["hechos"][hecho]["tipo"] == tipo}


def ejecutar_casos(base, criterios, semilla):
    resultados = []
    for ruta in sorted(glob.glob(os.path.join(CARPETA_CASOS, "*.json"))):
        with open(ruta, encoding="utf-8") as archivo:
            esperado = json.load(archivo).get("esperado", {})
        descripcion, respuestas = cargar_caso(ruta, base)
        memoria, traza = motor_inferencia_avanzado(respuestas, base, criterios, semilla, mostrar=False)
        origen = justificaciones(traza)

        obtenido = {
            "diagnosticos": de_tipo(base, memoria, "diagnostico"),
            "severidad": de_tipo(base, memoria, "severidad"),
            "recomendaciones": de_tipo(base, memoria, "recomendacion"),
            "reglas": {paso["regla"]["id"] for paso in traza},
        }
        fallas = [clave for clave in obtenido if obtenido[clave] != set(esperado.get(clave, []))]
        inferidos = list(origen)
        hecho_final = max(inferidos, key=lambda h: profundidad(h, origen)) if inferidos else None

        nombre = os.path.splitext(os.path.basename(ruta))[0]
        secciones = generar_reporte(base, RUTA_BASE_POR_DEFECTO, respuestas, memoria, traza,
                                    f"archivo de caso `{nombre}.json`: {descripcion}", criterios, semilla)
        os.makedirs(CARPETA_SALIDA, exist_ok=True)
        with open(os.path.join(CARPETA_SALIDA, f"reporte_{nombre}.md"), "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(linea for lineas in secciones.values() for linea in lineas))

        resultados.append({
            "nombre": nombre,
            "descripcion": descripcion,
            "ciclos": len(traza),
            "reglas": [paso["regla"]["id"] for paso in traza],
            "profundidad": profundidad(hecho_final, origen) if hecho_final else 0,
            "cadena": cadena_mas_larga(hecho_final, origen) if hecho_final else [],
            "fallas": fallas,
            "obtenido": obtenido,
        })
    return resultados


def comparar_estrategias(base, semilla):
    """Mismo caso con distintos órdenes de criterios: cambia el orden de disparo, no las conclusiones."""
    _, ddos = cargar_caso(os.path.join(CARPETA_CASOS, "ddos.json"), base)
    _, memoria_caso = cargar_caso(os.path.join(CARPETA_CASOS, "memoria.json"), base)
    respuestas = {**ddos, **memoria_caso}
    estrategias = [
        ["prioridad", "recencia", "especificidad", "azar"],
        ["recencia", "prioridad", "especificidad", "azar"],
        ["especificidad"],
    ]
    filas = []
    for criterios in estrategias:
        memoria, traza = motor_inferencia_avanzado(respuestas, base, criterios, semilla, mostrar=False)
        ciclo_incidente = memoria.get("incidente_critico")
        primer_diagnostico = min((c for h, c in memoria.items()
                                  if base["hechos"][h]["tipo"] == "diagnostico"), default=None)
        filas.append({
            "criterios": criterios,
            "orden": [paso["regla"]["id"] for paso in traza],
            "primer_diagnostico": primer_diagnostico,
            "ciclo_incidente": ciclo_incidente,
            "conclusiones": frozenset(memoria),
        })
    return filas


def main():
    base = cargar_base_conocimiento(RUTA_BASE_POR_DEFECTO)
    criterios = base["estrategia"]["criterios"]
    semilla = base["estrategia"].get("semilla")

    resultados = ejecutar_casos(base, criterios, semilla)
    todas = {regla["id"] for regla in base["reglas"]}
    cubiertas = set().union(*(set(r["reglas"]) for r in resultados))
    comparacion = comparar_estrategias(base, semilla)
    mismas_conclusiones = len({fila["conclusiones"] for fila in comparacion}) == 1

    lineas = ["# Resumen de pruebas del sistema experto", "",
              "## Casos de prueba", "",
              "| Caso | Descripción | Ciclos | Reglas disparadas | Profundidad | Cadena más larga | Resultado |",
              "|---|---|---|---|---|---|---|"]
    for r in resultados:
        estado = "OK" if not r["fallas"] else "FALLA en " + ", ".join(r["fallas"])
        cadena = " -> ".join(r["cadena"]) or "(sin inferencias)"
        lineas.append(f"| {r['nombre']} | {r['descripcion']} | {r['ciclos']} | {' '.join(r['reglas']) or '-'} | "
                      f"{r['profundidad']} | {cadena} | {estado} |")

    faltantes = sorted(todas - cubiertas)
    lineas += ["", "## Cobertura de reglas", "",
               f"Reglas disparadas en al menos un caso: {len(cubiertas)} de {len(todas)}."
               + (f" Sin cubrir: {', '.join(faltantes)}." if faltantes else " Cobertura completa."), ""]

    lineas += ["## Comparación de estrategias (caso combinado ddos + memoria)", "",
               "| Orden de criterios | Secuencia de reglas disparadas | Ciclo del primer diagnóstico | Ciclo de incidente crítico |",
               "|---|---|---|---|"]
    for fila in comparacion:
        lineas.append(f"| {' -> '.join(fila['criterios'])} | {' '.join(fila['orden'])} | "
                      f"{fila['primer_diagnostico']} | {fila['ciclo_incidente']} |")
    lineas += ["", "Las tres estrategias llegan al mismo conjunto final de hechos: "
               + ("sí." if mismas_conclusiones else "no."), ""]

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    with open(os.path.join(CARPETA_SALIDA, "resumen_pruebas.md"), "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
    print("\n".join(lineas))

    exito = all(not r["fallas"] for r in resultados) and not faltantes
    print("RESULTADO GLOBAL:", "TODAS LAS PRUEBAS PASARON" if exito else "HAY FALLAS")
    raise SystemExit(0 if exito else 1)


if __name__ == "__main__":
    main()
