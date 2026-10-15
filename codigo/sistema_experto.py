# -*- coding: utf-8 -*-
"""Sistema experto: diagnóstico de rendimiento y caídas de un servidor / aplicación web.

Basado en el motor de inferencia de clase (sistExpMotorInf2026, versión 11 de mayo de 2026).
Cambios frente al código original:
  - La base de conocimiento se carga desde un archivo JSON (base_conocimiento.json).
  - La memoria de trabajo guarda el ciclo en que entró cada hecho, para aplicar la recencia.
  - La resolución de conflictos aplica, en orden configurable:
    refracción -> prioridad -> recencia -> especificidad -> azar con semilla.
  - Cada ciclo queda registrado en una traza que alimenta el módulo de explicación.
"""

import argparse
import json
import os
import random
from datetime import datetime

RUTA_BASE_POR_DEFECTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base_conocimiento.json")
TIPOS_HECHO = {"sintoma", "intermedio", "diagnostico", "severidad", "recomendacion"}
CRITERIOS_VALIDOS = {"prioridad", "recencia", "especificidad", "azar"}
CRITERIOS_POR_DEFECTO = ["prioridad", "recencia", "especificidad", "azar"]


# ---------------------------------------------------------------------------
# Carga de la base de conocimiento
# ---------------------------------------------------------------------------

def cargar_base_conocimiento(ruta):
    """Lee la base de conocimiento desde un archivo JSON y verifica su estructura."""
    with open(ruta, encoding="utf-8") as archivo:
        base = json.load(archivo)

    for seccion in ("hechos", "reglas"):
        if seccion not in base:
            raise ValueError(f"La base de conocimiento no tiene la sección '{seccion}'.")

    for nombre, hecho in base["hechos"].items():
        if hecho.get("tipo") not in TIPOS_HECHO:
            raise ValueError(f"El hecho '{nombre}' tiene un tipo no válido: {hecho.get('tipo')}")
        if hecho["tipo"] == "sintoma" and "pregunta" not in hecho:
            raise ValueError(f"El síntoma '{nombre}' no tiene pregunta para el usuario.")

    ids = set()
    for regla in base["reglas"]:
        for campo in ("id", "nombre", "antecedentes", "consecuentes"):
            if campo not in regla:
                raise ValueError(f"Una regla no tiene el campo '{campo}': {regla}")
        if regla["id"] in ids:
            raise ValueError(f"El identificador de regla {regla['id']} está repetido.")
        ids.add(regla["id"])
        for hecho in regla["antecedentes"] + regla["consecuentes"]:
            if hecho not in base["hechos"]:
                raise ValueError(f"La regla {regla['id']} usa el hecho '{hecho}', que no está definido.")

    estrategia = base.setdefault("estrategia", {})
    estrategia.setdefault("criterios", CRITERIOS_POR_DEFECTO)
    invalidos = set(estrategia["criterios"]) - CRITERIOS_VALIDOS
    if invalidos:
        raise ValueError(f"Criterios de resolución de conflictos no válidos: {invalidos}")

    return base


# ---------------------------------------------------------------------------
# Resolución de conflictos
# ---------------------------------------------------------------------------

def valor_criterio(criterio, regla, memoria):
    """Puntaje de una regla según un criterio (gana el mayor)."""
    if criterio == "prioridad":
        return regla.get("prioridad", 0)
    if criterio == "recencia":
        # Ciclo en que entró el antecedente más nuevo de la regla (Bigus 2 / Rolston 3)
        return max(memoria[antecedente] for antecedente in regla["antecedentes"])
    if criterio == "especificidad":
        # Número de antecedentes (Bigus 3 / Rolston 2)
        return len(regla["antecedentes"])
    raise ValueError(f"Criterio desconocido: {criterio}")


def resolver_conflicto(reglas_aplicables, memoria, criterios, azar):
    """Aplica los criterios en orden; cada uno conserva solo las reglas con el mejor puntaje.

    Devuelve la regla elegida (índice, regla) y un registro de la decisión con el
    criterio que deshizo el empate y los puntajes de cada paso.
    """
    candidatas = list(reglas_aplicables)
    pasos = []

    if len(candidatas) == 1:
        return candidatas[0], {"criterio": "única aplicable", "pasos": pasos}

    for criterio in criterios:
        if criterio == "azar":
            # Bigus 4 / Rolston 5: sorteo reproducible gracias a la semilla
            elegida = azar.choice(candidatas)
            pasos.append({"criterio": "azar", "puntajes": {}, "quedan": [elegida[1]["id"]]})
            return elegida, {"criterio": "azar", "pasos": pasos}

        puntajes = {regla["id"]: valor_criterio(criterio, regla, memoria) for _, regla in candidatas}
        mejor = max(puntajes.values())
        candidatas = [(i, regla) for i, regla in candidatas if puntajes[regla["id"]] == mejor]
        pasos.append({"criterio": criterio, "puntajes": puntajes,
                      "quedan": [regla["id"] for _, regla in candidatas]})

        if len(candidatas) == 1:
            return candidatas[0], {"criterio": criterio, "pasos": pasos}

    # Sin azar configurado: se toma la primera en el orden del archivo (Rolston 1)
    return candidatas[0], {"criterio": "orden del archivo", "pasos": pasos}


def describir_decision(decision):
    """Texto corto del criterio que decidió la elección, para la consola y el reporte."""
    if not decision["pasos"]:
        return decision["criterio"]
    ultimo = decision["pasos"][-1]
    if decision["criterio"] == "azar":
        return "azar (empate en todos los criterios anteriores)"
    if decision["criterio"] == "orden del archivo":
        return "orden del archivo (empate en todos los criterios)"
    puntajes = ", ".join(f"{id_regla}={valor}" for id_regla, valor in ultimo["puntajes"].items())
    return f"{decision['criterio']} ({puntajes})"


# ---------------------------------------------------------------------------
# Motor de inferencia (encadenamiento hacia adelante)
# ---------------------------------------------------------------------------

def motor_inferencia_avanzado(hechos_iniciales, base, criterios=None, semilla=None, mostrar=True):
    """Encadenamiento hacia adelante sobre la base de conocimiento cargada.

    hechos_iniciales: iterable de hechos presentes, o diccionario {hecho: True/False}.
    Devuelve la memoria de trabajo {hecho: ciclo de ingreso} y la traza del razonamiento.
    """
    reglas = base["reglas"]
    estrategia = base.get("estrategia", {})
    criterios = criterios or estrategia.get("criterios", CRITERIOS_POR_DEFECTO)
    semilla = semilla if semilla is not None else estrategia.get("semilla")
    azar = random.Random(semilla)

    # A diferencia del original, solo cuentan los hechos verdaderos
    if isinstance(hechos_iniciales, dict):
        hechos_iniciales = [hecho for hecho, valor in hechos_iniciales.items() if valor]

    # Memoria de trabajo: hecho -> ciclo en que entró (los iniciales en el ciclo 0).
    # Reemplaza el conjunto 'hechos_nuevos' del código original y permite aplicar la recencia.
    memoria = {hecho: 0 for hecho in hechos_iniciales}
    reglas_disparadas = set()
    traza = []
    ciclo = 0

    while True:
        ciclo += 1
        reglas_aplicables = []
        for i, regla in enumerate(reglas):
            # Refracción: no repetir reglas ya disparadas
            if i not in reglas_disparadas:
                # Verificar si todos los antecedentes están presentes en la memoria de trabajo
                if set(regla["antecedentes"]).issubset(memoria):
                    reglas_aplicables.append((i, regla))

        if mostrar:
            print(f"\n--- Ciclo {ciclo} ---")
            print("Conjunto de conflictos (Reglas aplicables):")
            if reglas_aplicables:
                for _, regla in reglas_aplicables:
                    print(f"- {regla['id']} {regla['nombre']} (prioridad {regla.get('prioridad', 0)})")
            else:
                print("- Ninguna")

        if not reglas_aplicables:
            break  # No hay reglas aplicables, detener la inferencia

        # ***** Resolver conflicto *****
        (indice_regla, regla), decision = resolver_conflicto(reglas_aplicables, memoria, criterios, azar)

        # Disparar la regla y agregar los consecuentes nuevos
        reglas_disparadas.add(indice_regla)
        nuevos_hechos = []
        for consecuente in regla["consecuentes"]:
            if consecuente not in memoria:
                memoria[consecuente] = ciclo
                nuevos_hechos.append(consecuente)

        traza.append({
            "ciclo": ciclo,
            "conjunto_conflicto": [r["id"] for _, r in reglas_aplicables],
            "regla": regla,
            "decision": decision,
            "antecedentes": {a: memoria[a] for a in regla["antecedentes"]},
            "nuevos_hechos": nuevos_hechos,
        })

        if mostrar:
            print(f"Regla seleccionada: {regla['id']} {regla['nombre']}")
            print(f"Criterio decisivo: {describir_decision(decision)}")
            if nuevos_hechos:
                print(f"Nuevos hechos agregados: {', '.join(nuevos_hechos)}")
            else:
                print("No se agregaron nuevos hechos (ya existían en la memoria de trabajo).")

    return memoria, traza


# ---------------------------------------------------------------------------
# Ingreso de hechos (interfaz de consola)
# ---------------------------------------------------------------------------

RESPUESTAS_SI = {"s", "si", "sí", "y", "yes"}
RESPUESTAS_NO = {"n", "no"}


def leer_entrada(mensaje):
    """input() sin espacios ni marca BOM (la agregan algunas consolas al redirigir la entrada)."""
    try:
        return input(mensaje).strip().lstrip("﻿")
    except EOFError:
        raise SystemExit("\nEntrada finalizada antes de completar el cuestionario.")


def preguntar_si_no(pregunta):
    """Repite la pregunta hasta obtener una respuesta válida (s/n)."""
    while True:
        respuesta = leer_entrada(f"{pregunta} (s/n): ").lower()
        if respuesta in RESPUESTAS_SI:
            return True
        if respuesta in RESPUESTAS_NO:
            return False
        print("  Respuesta no válida. Escriba 's' para sí o 'n' para no.")


def sintomas_por_categoria(base):
    """Agrupa los síntomas de la base por categoría, respetando el orden del archivo."""
    categorias = {}
    for nombre, hecho in base["hechos"].items():
        if hecho["tipo"] == "sintoma":
            categorias.setdefault(hecho.get("categoria", "General"), []).append(nombre)
    return categorias


def ingresar_por_categorias(base):
    """Modo 1: se pregunta por cada categoría y, solo si hay problemas, por cada síntoma."""
    respuestas = {}
    for categoria, sintomas in sintomas_por_categoria(base).items():
        print()
        if preguntar_si_no(f"¿Observa problemas de {categoria.upper()}?"):
            for sintoma in sintomas:
                respuestas[sintoma] = preguntar_si_no("  " + base["hechos"][sintoma]["pregunta"])
        else:
            for sintoma in sintomas:
                respuestas[sintoma] = False
    return respuestas


def ingresar_por_lista(base):
    """Modo 2: se muestra la lista numerada de síntomas y el usuario escribe los números."""
    numerados = []
    for categoria, sintomas in sintomas_por_categoria(base).items():
        print(f"\n  {categoria}")
        for sintoma in sintomas:
            numerados.append(sintoma)
            print(f"   {len(numerados):2d}. {base['hechos'][sintoma]['texto']}")

    while True:
        entrada = leer_entrada("\nNúmeros de los síntomas presentes, separados por comas (Enter si ninguno): ")
        partes = entrada.replace(",", " ").split()
        if all(parte.isdigit() and 1 <= int(parte) <= len(numerados) for parte in partes):
            break
        print(f"  Entrada no válida. Use números entre 1 y {len(numerados)}, por ejemplo: 1, 5, 9")

    elegidos = {numerados[int(parte) - 1] for parte in partes}
    return {sintoma: sintoma in elegidos for sintoma in numerados}


def mostrar_sintomas_presentes(base, respuestas):
    presentes = [sintoma for sintoma, valor in respuestas.items() if valor]
    print("\nSíntomas que se cargarán en la memoria de trabajo:")
    for sintoma in presentes:
        print(f"  - {base['hechos'][sintoma]['texto']}")
    if not presentes:
        print("  (ninguno)")


def ingresar_hechos(base):
    """Pregunta cómo ingresar los síntomas.

    Devuelve {síntoma: True/False} para la memoria de trabajo y el nombre del modo usado.
    """
    modos = {"1": "Cuestionario guiado por categorías", "2": "Lista numerada de síntomas"}
    while True:
        print("\n¿Cómo desea ingresar los síntomas?")
        print(f"  1. {modos['1']}")
        print(f"  2. {modos['2']}")
        opcion = leer_entrada("Opción (1/2): ")
        if opcion not in modos:
            print("  Opción no válida.")
            continue

        respuestas = ingresar_por_categorias(base) if opcion == "1" else ingresar_por_lista(base)
        mostrar_sintomas_presentes(base, respuestas)
        if preguntar_si_no("¿Los datos son correctos?"):
            return respuestas, modos[opcion]


def cargar_caso(ruta, base):
    """Lee un caso desde JSON: {"descripcion": "...", "sintomas": [...]} o {"sintomas": {hecho: bool}}."""
    with open(ruta, encoding="utf-8") as archivo:
        caso = json.load(archivo)

    sintomas = caso.get("sintomas", [])
    respuestas = dict(sintomas) if isinstance(sintomas, dict) else {sintoma: True for sintoma in sintomas}
    no_validos = [s for s in respuestas if base["hechos"].get(s, {}).get("tipo") != "sintoma"]
    if no_validos:
        raise ValueError(f"El caso {ruta} incluye hechos que no son síntomas de la base: {no_validos}")

    return caso.get("descripcion", os.path.basename(ruta)), respuestas


# ---------------------------------------------------------------------------
# Módulo de explicación y reporte
# ---------------------------------------------------------------------------

def justificaciones(traza):
    """Para cada hecho inferido, el paso de la traza que lo agregó a la memoria de trabajo."""
    return {hecho: paso for paso in traza for hecho in paso["nuevos_hechos"]}


def respaldos(traza):
    """Para cada hecho, todas las reglas disparadas que lo concluyen (también las que no aportaron hechos nuevos)."""
    resultado = {}
    for paso in traza:
        for hecho in paso["regla"]["consecuentes"]:
            resultado.setdefault(hecho, []).append(paso["regla"]["id"])
    return resultado


def conclusiones_por_tipo(base, memoria, origen, tipo):
    """Hechos inferidos de un tipo, ordenados por la prioridad de la regla que los concluyó y luego por ciclo."""
    hechos = [hecho for hecho in memoria if base["hechos"][hecho]["tipo"] == tipo]
    return sorted(hechos, key=lambda h: (-origen[h]["regla"].get("prioridad", 0), origen[h]["ciclo"]))


def arbol_explicacion(hecho, base, origen, ya_explicados=(), nivel=0):
    """Líneas Markdown con la cadena de reglas que justifica un hecho, bajando hasta los síntomas."""
    sangria = "  " * nivel
    texto = base["hechos"][hecho]["texto"]
    if hecho not in origen:
        return [f"{sangria}- {texto} (`{hecho}`): síntoma reportado"]
    if nivel > 0 and hecho in ya_explicados:
        return [f"{sangria}- **{texto}** (`{hecho}`): ver su explicación arriba"]

    paso = origen[hecho]
    regla = paso["regla"]
    lineas = [f"{sangria}- **{texto}** (`{hecho}`): concluido por {regla['id']} *{regla['nombre']}* "
              f"en el ciclo {paso['ciclo']}. {regla.get('explicacion', '')}"]
    for antecedente in regla["antecedentes"]:
        lineas += arbol_explicacion(antecedente, base, origen, ya_explicados, nivel + 1)
    return lineas


def hipotesis_por_confirmar(base, memoria):
    """Reglas no disparadas a las que solo les falta un síntoma: indican qué verificar a continuación."""
    hipotesis = []
    for regla in base["reglas"]:
        faltantes = [a for a in regla["antecedentes"] if a not in memoria]
        if len(regla["antecedentes"]) < 2 or len(faltantes) != 1:
            continue
        if all(consecuente in memoria for consecuente in regla["consecuentes"]):
            continue  # La conclusión ya se obtuvo por otro camino
        if base["hechos"][faltantes[0]]["tipo"] == "sintoma":
            hipotesis.append((regla, faltantes[0]))
    return hipotesis


def generar_reporte(base, ruta_base, respuestas, memoria, traza, origen_datos, criterios, semilla):
    """Construye el reporte en Markdown. Devuelve {sección: líneas} para poder mostrar solo una parte en consola."""
    hechos = base["hechos"]
    origen = justificaciones(traza)
    todos_respaldos = respaldos(traza)
    secciones = {}

    secciones["encabezado"] = [
        "# Reporte del sistema experto",
        "",
        f"- **Dominio:** {base.get('dominio', '')}",
        f"- **Fecha:** {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"- **Base de conocimiento:** `{os.path.basename(ruta_base)}` ({len(base['reglas'])} reglas)",
        f"- **Ingreso de hechos:** {origen_datos}",
        f"- **Estrategia de resolución de conflictos:** refracción -> {' -> '.join(criterios)} (semilla {semilla})",
        "",
    ]

    reportados = [s for s, valor in respuestas.items() if valor]
    descartados = [s for s, valor in respuestas.items() if not valor]
    lineas = ["## 1. Datos del caso", "", "**Síntomas reportados:**", ""]
    lineas += [f"- {hechos[s]['texto']} (`{s}`)" for s in reportados] or ["- (ninguno)"]
    lineas += ["", f"**Síntomas descartados por el usuario:** {len(descartados)}", ""]
    secciones["datos"] = lineas

    severidades = conclusiones_por_tipo(base, memoria, origen, "severidad")
    diagnosticos = conclusiones_por_tipo(base, memoria, origen, "diagnostico")
    recomendaciones = conclusiones_por_tipo(base, memoria, origen, "recomendacion")
    lineas = ["## 2. Resumen para la toma de decisiones", ""]
    if severidades:
        for hecho in severidades:
            lineas.append(f"**Severidad:** {hechos[hecho]['texto']} (respaldado por {', '.join(todos_respaldos[hecho])})")
    else:
        lineas.append("**Severidad:** sin incidente crítico identificado; atender según la prioridad de los diagnósticos.")
    lineas += ["", "**Diagnósticos:**", ""]
    if diagnosticos:
        for hecho in diagnosticos:
            regla = origen[hecho]["regla"]
            lineas.append(f"- {hechos[hecho]['texto']} (prioridad {regla.get('prioridad', 0)}, {regla['id']})")
    else:
        lineas.append("- No se identificó el problema con la información suministrada. "
                      "Se sugiere consultar con un técnico especializado.")
    lineas += ["", "**Recomendaciones (en orden de prioridad):**", ""]
    for numero, hecho in enumerate(recomendaciones, start=1):
        regla = origen[hecho]["regla"]
        causa = ", ".join(hechos[a]["texto"] for a in regla["antecedentes"])
        lineas.append(f"{numero}. {hechos[hecho]['texto']} *(por {regla['id']}, a partir de: {causa})*")
    if not recomendaciones:
        lineas.append("- (ninguna)")
    lineas.append("")
    secciones["resumen"] = lineas

    lineas = ["## 3. Explicación: ¿cómo se llegó a cada conclusión?", ""]
    for hecho in diagnosticos + severidades:
        lineas += arbol_explicacion(hecho, base, origen, ya_explicados=diagnosticos)
        otros = [r for r in todos_respaldos[hecho] if r != origen[hecho]["regla"]["id"]]
        if otros:
            lineas.append(f"  - *También respaldado por: {', '.join(otros)}*")
        lineas.append("")
    if not severidades and not diagnosticos:
        lineas += ["No se llegó a ningún diagnóstico.", ""]
    secciones["explicacion"] = lineas

    lineas = ["## 4. Hipótesis por confirmar (¿por qué no?)", ""]
    hipotesis = hipotesis_por_confirmar(base, memoria)
    for regla, faltante in hipotesis:
        conclusion = ", ".join(hechos[c]["texto"] for c in regla["consecuentes"])
        estado = "el usuario respondió que no" if respuestas.get(faltante) is False else "no fue informado"
        lineas.append(f"- Para concluir **{conclusion}** ({regla['id']}) solo falta: "
                      f"{hechos[faltante]['pregunta']} ({estado}). Conviene verificarlo.")
    if not hipotesis:
        lineas.append("- No hay reglas a las que les falte un único síntoma.")
    lineas.append("")
    secciones["hipotesis"] = lineas

    lineas = ["## 5. Traza del razonamiento", "",
              "| Ciclo | Conjunto de conflictos | Regla seleccionada | Criterio decisivo | Hechos nuevos |",
              "|---|---|---|---|---|"]
    for paso in traza:
        nuevos = ", ".join(f"`{h}`" for h in paso["nuevos_hechos"]) or "(ninguno)"
        lineas.append(f"| {paso['ciclo']} | {', '.join(paso['conjunto_conflicto'])} | "
                      f"{paso['regla']['id']} {paso['regla']['nombre']} | {describir_decision(paso['decision'])} | {nuevos} |")
    lineas += ["", "Inferencia terminada: no quedan reglas aplicables.", ""]
    secciones["traza"] = lineas

    lineas = ["## 6. Memoria de trabajo final", "",
              "| Hecho | Tipo | Ciclo de ingreso | Descripción |", "|---|---|---|---|"]
    for hecho, ciclo in sorted(memoria.items(), key=lambda item: item[1]):
        lineas.append(f"| `{hecho}` | {hechos[hecho]['tipo']} | {ciclo} | {hechos[hecho]['texto']} |")
    lineas.append("")
    secciones["memoria"] = lineas

    return secciones


def guardar_reporte(secciones, carpeta, nombre_caso=None):
    os.makedirs(carpeta, exist_ok=True)
    sufijo = f"_{nombre_caso}" if nombre_caso else ""
    ruta = os.path.join(carpeta, f"reporte{sufijo}_{datetime.now():%Y%m%d_%H%M%S}.md")
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(linea for lineas in secciones.values() for linea in lineas))
    return ruta


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def mostrar_bienvenida(base):
    total_sintomas = sum(1 for hecho in base["hechos"].values() if hecho["tipo"] == "sintoma")
    print("=" * 72)
    print("SISTEMA EXPERTO")
    print(base.get("dominio", ""))
    print("=" * 72)
    print(f"Base de conocimiento cargada: {len(base['reglas'])} reglas y {total_sintomas} síntomas.")
    print("Indique los síntomas que observa en el servidor. El sistema encadenará")
    print("las reglas para llegar a diagnósticos y recomendaciones.")


def main():
    carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Sistema experto de diagnóstico de servidores web.")
    parser.add_argument("--base", default=RUTA_BASE_POR_DEFECTO,
                        help="ruta del archivo JSON con la base de conocimiento")
    parser.add_argument("--caso", help="archivo JSON con los síntomas del caso (omite el cuestionario)")
    parser.add_argument("--criterios",
                        help="orden de los criterios de resolución de conflictos, separados por comas "
                             "(por ejemplo: recencia,prioridad,especificidad,azar)")
    parser.add_argument("--salida", default=os.path.join(carpeta_proyecto, "reportes"),
                        help="carpeta donde se guarda el reporte")
    args = parser.parse_args()

    base = cargar_base_conocimiento(args.base)
    criterios = args.criterios.split(",") if args.criterios else base["estrategia"]["criterios"]
    if set(criterios) - CRITERIOS_VALIDOS:
        parser.error(f"criterios no válidos: {set(criterios) - CRITERIOS_VALIDOS}")
    semilla = base["estrategia"].get("semilla")

    mostrar_bienvenida(base)
    if args.caso:
        descripcion, respuestas = cargar_caso(args.caso, base)
        origen_datos = f"archivo de caso `{os.path.basename(args.caso)}`: {descripcion}"
        print(f"\nCaso cargado desde archivo: {descripcion}")
        mostrar_sintomas_presentes(base, respuestas)
    else:
        respuestas, origen_datos = ingresar_hechos(base)

    print("\n" + "=" * 72)
    print("PROCESO DE INFERENCIA")
    print("=" * 72)
    memoria, traza = motor_inferencia_avanzado(respuestas, base, criterios=criterios, semilla=semilla)

    secciones = generar_reporte(base, args.base, respuestas, memoria, traza, origen_datos, criterios, semilla)

    # En consola se muestra la parte para la toma de decisiones; la traza ya se imprimió arriba
    print("\n" + "=" * 72)
    for clave in ("resumen", "explicacion", "hipotesis"):
        for linea in secciones[clave]:
            print(linea.replace("**", "").replace("`", ""))

    nombre_caso = os.path.splitext(os.path.basename(args.caso))[0] if args.caso else None
    ruta = guardar_reporte(secciones, args.salida, nombre_caso)
    print("=" * 72)
    print(f"Reporte completo guardado en: {ruta}")


if __name__ == "__main__":
    main()
