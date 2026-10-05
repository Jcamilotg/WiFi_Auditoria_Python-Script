import itertools
import os
import random

Green="\033[1;33m"
Blue="\033[1;34m"
Grey="\033[1;30m"
Red="\033[1;34m"

print(" "+ Red + "______________________________________________________________________________")
print(" "+ Blue + "Este Software es creado con fines educativos y evaluar que tu Wi-Fi sea segura")
print(" "+ Red + "______________________________________________________________________________")
print(" "+ Blue + "")


def obtener_datos():
    print(" " + Blue + "\n\nPuede tardar hasta una hora en buscar el password, a corde al tamaño de la wordlist generada\n\n")
    print(" " + Blue + "______________________________________________________________________________")
    print(" " + Blue + "\n\nIntroduce los datos para generar la wordlist personalizada, siempre separando cada palabra por ´,´´:\n\n")
    # --- VALIDACIÓN Y LIMPIEZA DE NOMBRES ---
    while True:
        nombres_input = input("Nombre del objetivo, sea empresa (ej. 'GreenTech', 'GreenTechGreenTech') o persona (ej. 'juan,perez,gomez') **[Mínimo 2 elementos]**: \n")
        nombres = [n.strip().lower() for n in nombres_input.split(',') if n.strip()]
        # *** MODIFICACIÓN CLAVE: Cambiar la validación a >= 2 ***
        if len(nombres) >= 2:
            break
        else:
            print(f"\n{Blue}ERROR: Debes ingresar al menos dos nombres o elementos separados por comas. Esto es necesario para combinaciones de iniciales. Intenta de nuevo.")
    # --- VALIDACIÓN Y LIMPIEZA de PALABRAS CLAVE ---
    while True:
        palabras_clave_input = input("Palabras clave/Servicios (ej. 'admin', 'servicio', 'logistica', nombres de mascotas, hijos, hobbies) **[Mínimo 1 elemento]**: \n")
        palabras_clave = [p.strip().lower() for p in palabras_clave_input.split(',') if p.strip()]
        if palabras_clave:
            break
        else:
            print(f"\n{Blue}ERROR: Debes ingresar al menos una palabra clave. Intenta de nuevo.")

    # --- VALIDACIÓN Y LIMPIEZA de NUM ID ---
    while True:
        num_id_input = input("Números de Identificación/Seriales (ej. RUC/NIT, números de serie, códigos de suerte) **[Mínimo 1 elemento]**: \n")
        num_id = [i.strip() for i in num_id_input.split(',') if i.strip()]
        if num_id:
            break
        else:
            print(f"\n{Blue}ERROR: Debes ingresar al menos un número ID. Intenta de nuevo.")

    # --- VALIDACIÓN DE FECHAS (OBLIGA A TRES MÍNIMO) ---
    while True:
        fechas_str = input("Fechas importantes (ej. inauguración de la empresa, cumpleaños del dueño, años clave) **[Mínimo 3 elementos]** ejemplo: 1976,05,12,2024: \n")
        fechas_validas = [f.strip() for f in fechas_str.split(',') if f.strip()]

        if len(fechas_validas) >= 3:
            fechas = fechas_validas
            break
        else:
            print(f"\n{Blue}ERROR: Debes ingresar al menos 3 fechas o elementos separados por comas para asegurar la calidad del diccionario. Intenta de nuevo.")
    simbolos = ["@","#","*","!","|","&","/","=","?",".","%","+","","-","_","¡"]

    return nombres, fechas, palabras_clave, simbolos, num_id


# Generar combinaciones
def generar_combinaciones(datos, longitud_min=6, longitud_max=15):
    wordlist = set()
    for longitud in range(longitud_min, longitud_max + 1):
        for combinacion in itertools.permutations(datos, 4):
        #for combinacion in itertools.product(datos, repeat=longitud):
            posible = "".join(combinacion)
            if longitud_min <= len(posible) <= longitud_max:
                wordlist.add(posible)
    return wordlist

# Nueva función para obtener iniciales del nombre
def obtener_iniciales(nombre):
    return ''.join([parte[0].upper() for parte in nombre.split()])

# Nueva función para generar contraseñas con iniciales, ID y caracteres especiales
def generar_contraseñas_con_iniciales(nombres, ids, simbolos):
    wordlist = set()
    for nombre in nombres:
        iniciales = obtener_iniciales(nombre)
        for id_usuario in ids:
            for simbolo_inicio in simbolos:
                for simbolo_final in simbolos:
                    # Crear combinaciones con iniciales, ID y símbolos
                    contraseña = f"{id_usuario}{simbolo_inicio}{iniciales}{simbolo_final}"
                    wordlist.add(contraseña)
    return wordlist

# Función para generar contraseñas avanzadas con un formato específico
def generar_contraseña_formato_especifico(ids, nombres, simbolos):
    wordlist = set()
    for id_usuario in ids:
        for nombre in nombres:
            iniciales = obtener_iniciales(nombre)
            secuencia = nombre[1:3].lower()  # Ejemplo: tomar las dos primeras letras del apellido
            for _ in range(1500):
                simbolo_inicio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)
                # Formato: [ID][Símbolo][Iniciales][Secuencia][Símbolo]
                contraseña = f"{id_usuario}{simbolo_inicio}{iniciales}{secuencia}{simbolo_final}"
                wordlist.add(contraseña)
    return wordlist

# Función para obtener primera letra
# Función para obtener las iniciales de un nombre compuesto
def obtener_pri_iniciales(nombre):
    # Tomar la primera letra de cada parte del nombre y convertirla a mayúsculas
    pri_iniciales = ''.join([parte[0] for parte in nombre if parte])  # Filtrar partes vacías y tomar la inicial
    return pri_iniciales
def generar_contraseña_prim_ini(ids, nombres, simbolos):
    wordlist = set()
    for id_usuario in ids:
        for nombre in nombres:
            iniciales = obtener_pri_iniciales(nombres)
            secuencia = nombre[1:1].lower()  # Ejemplo: tomar las dos primeras letras del apellido
            for _ in range(1500):
                simbolo_inicio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)
                #simbolos_aleatorios = ''.join(random.choices(simbolos, k=4))  # Genera 4 símbolos aleatorios
                contraseña = f"{id_usuario}{simbolo_inicio}{iniciales}{secuencia}{simbolo_final}"
                #contraseña = f"{id_usuario}{simbolos_aleatorios}{iniciales}{secuencia}{simbolos_aleatorios}"
                wordlist.add(contraseña)
    return wordlist

def generar_contraseña_ini_princ(ids, nombres, simbolos):
    wordlist = set()
    for id_usuario in ids:
        for nombre in nombres:
            iniciales = obtener_pri_iniciales(nombres)
            secuencia = nombre[1:1].lower()  # Ejemplo: tomar las dos primeras letras del apellido
            for _ in range(1500):
                simbolo_inicio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)
                contraseña = f"{iniciales}{id_usuario}{simbolo_inicio}{secuencia}{simbolo_final}"
                wordlist.add(contraseña)
    return wordlist

def nombre_palabra_simbolo(palabras, nombres, simbolos):
    wordlist = set()
    for simbolo in simbolos:
        for nombre in nombres:
            for palabra in palabras:
                contraseña = f"{nombre}{palabra}{simbolo}"
                wordlist.add(contraseña)
    return wordlist
def guardar_listas(fechas, nombres, palabras_clave, num_id):
    # Usar un conjunto para evitar duplicados
    wordlist = set()
    iniciales = obtener_pri_iniciales(nombres)
    # Agregar datos individuales
    for nombre in nombres:
        wordlist.add(nombre)

    for fecha in fechas:
        wordlist.add(fecha)

    for palabra in palabras_clave:
        wordlist.add(palabra)

    for num in num_id:
        wordlist.add(num)

    # Generar combinaciones

    for nombre in nombres:
        for fecha in fechas:
            wordlist.add(f"{nombre}{fecha}")

        for palabra in palabras_clave:
            wordlist.add(f"{nombre}{palabra}")

        for num in num_id:
            wordlist.add(f"{nombre}{num}")

#com iniciales
        for fecha in fechas:
            wordlist.add(f"{iniciales}{fecha}")

        for fecha in fechas:
            wordlist.add(f"{fecha}{iniciales}")


        for palabra in palabras_clave:
            wordlist.add(f"{iniciales}{palabra}")

        for palabra in palabras_clave:
            wordlist.add(f"{palabra}{iniciales}")

        for num in num_id:
            wordlist.add(f"{iniciales}{num}")
        for num in num_id:
            wordlist.add(f"{num}{iniciales}")
##################################################################

    for palabra in palabras_clave:
        for fecha in fechas:
            wordlist.add(f"{palabra}{fecha}")

        for num in num_id:
            wordlist.add(f"{palabra}{num}")

    for fecha in fechas:
        for num in num_id:
            wordlist.add(f"{fecha}{num}")



    return wordlist

#dos primeras iniciales:
def generar_2prim_ini(ids, nombres, simbolos):
    wordlist = set()
    for id_usuario in ids:
        for nombre in nombres:
            iniciales = obtener_pri_iniciales(nombres)
            inicial1 = iniciales[0]
            inicial2 = iniciales[1]
            secuencia = nombre[1:1].lower()  # Ejemplo: tomar las dos primeras letras del apellido
            for _ in range(1500):
                simbolo_inicio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)
                contraseña = f"{inicial1}{inicial2}{id_usuario}{simbolo_inicio}{secuencia}{simbolo_final}"
                wordlist.add(contraseña)
    return wordlist

def generar_2prim_fin(ids, nombres, simbolos):
    wordlist = set()
    for id_usuario in ids:
        for nombre in nombres:
            iniciales = obtener_pri_iniciales(nombres)
            inicial1 = iniciales[0]
            inicial2 = iniciales[1]
            secuencia = nombre[1:1].lower()  # Ejemplo: tomar las dos primeras letras del apellido
            for _ in range(1500):
                simbolo_inicio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)
                contraseña = f"{id_usuario}{simbolo_inicio}{secuencia}{simbolo_final}{inicial1}{inicial2}"
                wordlist.add(contraseña)
    return wordlist


def nombre_simbolo_fecha(fechas, nombres, simbolos):
    wordlist = set()
    for simbolo in simbolos:
        for nombre in nombres:
            for _ in range(1500):  # Puedes ajustar el número de combinaciones
                simbolo_inicio = random.choice(simbolos)
                simbolo_intermedio = random.choice(simbolos)
                simbolo_final = random.choice(simbolos)

                # Seleccionar 3 elementos únicos de `fechas`
                fecha_comb = random.sample(fechas, 3)  # Selecciona 3 elementos diferentes

                contraseña = f"{nombre}{simbolo_inicio}{fecha_comb[0]}{simbolo_intermedio}{fecha_comb[1]}{simbolo_final}{fecha_comb[2]}"
                wordlist.add(contraseña)
    return wordlist
# Nueva función para generar números aleatorios de 4 dígitos basados en fechas


def generar_palabra_clave_con_año(palabras_clave, fechas, simbolos, num_años=5):
    """
    Combina palabras clave (mascotas, empresas, hobbies) con fechas y años comunes.

    Args:
        palabras_clave (list): Lista de nombres, mascotas, o palabras clave.
        fechas (list): Lista de fechas importantes (días, meses, años).
        simbolos (list): Lista de símbolos para intercalar.
        num_años (int): Número de años futuros a incluir.
    """
    wordlist = set()
    años_comunes = ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"]  # Años comunes de la empresa/usuario

    # Añadir los últimos 5 años y los próximos 5 años (para cobertura)
    año_actual = 2025  # Asumiendo el año de la tesis
    años_comunes.extend([str(año_actual + i) for i in range(1, num_años + 1)])
    años_comunes.extend([str(año_actual - i) for i in range(1, num_años + 1)])

    # 1. Palabra Clave + Año/Fecha
    for palabra in palabras_clave:
        for año in set(fechas + años_comunes):
            # Formato 1: Palabra + Año (Ej: Firulais2025)
            wordlist.add(f"{palabra}{año}")
            wordlist.add(f"{palabra.capitalize()}{año}")

            # Formato 2: Año + Palabra (Ej: 2025Firulais)
            wordlist.add(f"{año}{palabra}")

            # Formato 3: Palabra + Símbolo + Año (Ej: Firulais@2025)
            for simbolo in random.sample(simbolos, k=min(3, len(simbolos))):
                wordlist.add(f"{palabra}{simbolo}{año}")
                wordlist.add(f"{palabra.capitalize()}{simbolo}{año}")
                wordlist.add(f"{año}{simbolo}{palabra}")

    return wordlist
# Programa principal

def obtener_iniciales_capitalizadas(nombres):
    """
    """
    if not nombres:
        return ""

    # Obtener todas las iniciales en minúsculas
    iniciales_min = ''.join([nombre[0] for nombre in nombres if nombre])

    if not iniciales_min:
        return ""

    # Capitalizar la primera letra y dejar el resto en minúsculas
    return iniciales_min[0].upper() + iniciales_min[1:].lower()

def generar_iniciales_id_capitalizadas(nombres, ids):
    """
    """
    wordlist = set()

    iniciales_formato_cm = obtener_iniciales_capitalizadas(nombres)

    if not iniciales_formato_cm:
        return wordlist

    for id_usuario in ids:
        # Formato 1: Iniciales + ID
        wordlist.add(f"{iniciales_formato_cm}{id_usuario}")

        # Formato 2 (Inverso): ID + Iniciales
        wordlist.add(f"{id_usuario}{iniciales_formato_cm}")

    return wordlist

#tomar 2 primeras
def obtener_iniciales_2primerasconID(nombres):
    """
    Toma una lista de nombres y devuelve una cadena con las iniciales de
    SOLO LOS DOS PRIMEROS NOMBRES, donde la primera es mayúscula y las
    subsiguientes son minúsculas.
    Ej: ['claudia', 'maria', 'perez', 'gomez'] -> 'Cm'
    """
    if not nombres:
        return ""

    # *** MODIFICACIÓN CLAVE: Usar slice [0:2] ***
    # Seleccionamos solo los dos primeros nombres de la lista (índices 0 y 1)
    primeros_dos_nombres = nombres[:2]

    # Obtener todas las iniciales de los DOS PRIMEROS nombres en minúsculas
    iniciales_min = ''.join([nombre[0] for nombre in primeros_dos_nombres if nombre])

    if not iniciales_min:
        return ""

    # Si solo se genera una inicial (ej. 'c'), la regresamos capitalizada.
    # Si se generan dos (ej. 'cm'), regresamos 'Cm'.
    if len(iniciales_min) == 1:
        return iniciales_min[0].upper()

    # Capitalizar la primera letra y dejar la segunda y el resto en minúsculas
    return iniciales_min[0].upper() + iniciales_min[1:].lower()

def generar_iniciales_2primerasconID(nombres, ids):
    """
    """
    wordlist = set()

    iniciales_formato_cm = obtener_iniciales_2primerasconID(nombres)

    if not iniciales_formato_cm:
        return wordlist

    for id_usuario in ids:
        # Formato 1: Iniciales + ID
        wordlist.add(f"{iniciales_formato_cm}{id_usuario}")

        # Formato 2 (Inverso): ID + Iniciales
        wordlist.add(f"{id_usuario}{iniciales_formato_cm}")

    return wordlist
def generar_leetspeak_variantes(nombres, palabras_clave):
    wordlist = set()

    # 1. Definir las sustituciones más comunes
    sustituciones = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!', '|'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+'],
        'l': ['1', '7'],
    }

    # 2. Combinar todas las palabras base
    palabras_base = list(set(nombres + palabras_clave))

    for palabra in palabras_base:
        # Añadir la palabra original (minúscula)
        wordlist.add(palabra)

        # Generar variantes de una sola sustitución
        for i, char in enumerate(palabra):
            if char in sustituciones:
                for sub in sustituciones[char]:
                    # Crear una nueva palabra con una sola sustitución
                    nueva_palabra = list(palabra)
                    nueva_palabra[i] = sub
                    wordlist.add("".join(nueva_palabra))

        # Generar variantes con sustituciones múltiples (más agresivo)
        # Usaremos itertools para generar todas las combinaciones posibles de sustitución

        # Mapear la palabra a las posibles sustituciones por carácter
        posibles_chars = []
        for char in palabra:
            # Incluir el carácter original y sus sustitutos
            posibilidades = [char]
            if char in sustituciones:
                posibilidades.extend(sustituciones[char])
            posibles_chars.append(posibilidades)

        # Generar el producto cartesiano de todas las posibilidades
        for combinacion_chars in itertools.product(*posibles_chars):
            leetspeak_word = "".join(combinacion_chars)
            # Solo añadir si la variante Leet Speak es diferente de la palabra original
            if leetspeak_word != palabra:
                wordlist.add(leetspeak_word)

    return wordlist

def main():
    # Definición de nombres de archivos
    ARCHIVO_BASE = "password_personalizados.txt"
    ARCHIVO_FINAL = "password_comunes.txt"
    try:
        nombres, fechas, palabras_clave, simbolos, num_id = obtener_datos()
        datos = nombres + fechas + palabras_clave + simbolos + num_id
        contraseña_palsimfecha = generar_palabra_clave_con_año(palabras_clave, fechas, simbolos)
        contraseñas_ini_id_cap = generar_iniciales_id_capitalizadas(nombres, num_id)
        contraseñas_leetspeak = generar_leetspeak_variantes(nombres, palabras_clave)
        contraseñas_ini2conID = generar_iniciales_2primerasconID(nombres, num_id)

    #LLamando las funciones
        combinaciones = generar_combinaciones(datos)
        contraseñas_iniciales = generar_contraseñas_con_iniciales(nombres, num_id, simbolos)
        contraseñas_formato = generar_contraseña_formato_especifico(num_id, nombres, simbolos)
        contraseñas_pri_ini = generar_contraseña_prim_ini(num_id, nombres, simbolos)
        contraseñas_ini_primero = generar_contraseña_ini_princ(num_id, nombres, simbolos)
        contraseñas_listas = guardar_listas(fechas, nombres, palabras_clave, num_id)
        contraseña_nompalsim = nombre_palabra_simbolo(palabras_clave, nombres, simbolos)
        contraseña_2primini = generar_2prim_ini(num_id, nombres, simbolos)
        contraseña_2prifin = generar_2prim_fin(num_id, nombres, simbolos)
        contraseña_nomsimfech = nombre_simbolo_fecha(fechas, nombres, simbolos)

        # Unir ambas listas de contraseñas
        wordlist_generada = combinaciones.union(
            contraseñas_iniciales,
            contraseñas_formato,
            contraseñas_pri_ini,
            contraseñas_ini_primero,
            contraseñas_listas,
            contraseña_nompalsim,
            contraseña_2primini,
            contraseña_2prifin,
            contraseña_nomsimfech,
            contraseña_palsimfecha,
            contraseñas_ini_id_cap,
            contraseñas_leetspeak,
            contraseñas_ini2conID
                                       )

        # 2. Cargar lista base (password_personalizados.txt)
        wordlist_base = set()
        if os.path.exists(ARCHIVO_BASE):
            with open(ARCHIVO_BASE, "r") as f:
                # Leer y limpiar cada línea antes de agregar al conjunto
                wordlist_base = {line.strip() for line in f if line.strip()}
            print(f"[INFO] Se cargaron {len(wordlist_base)} contraseñas desde {ARCHIVO_BASE}.")
        else:
            print(
                f"[ALERTA] No se encontró el archivo base: {ARCHIVO_BASE}. Se creará {ARCHIVO_FINAL} solo con contraseñas generadas.")

        # 3. CONSOLIDAR: Unir la lista base con las generadas (el conjunto elimina duplicados)
        wordlist_final = wordlist_generada.union(wordlist_base)

        total_wordlist = len(wordlist_final)

        # 4. Guardar el conjunto total en ARCHIVO_FINAL
        with open(ARCHIVO_FINAL, "w") as archivo:
            for palabra in sorted(wordlist_final):
                archivo.write(palabra + "\n")

        # 5. Mostrar resultados
        print(f"\nGenerando combinaciones de contraseñas...\n")
        print(" " + Blue + f"Total de contraseñas generadas por ingeniería social: {len(wordlist_generada)}.")
        print(" " + Blue + f"Total de contraseñas consolidadas (incluyendo archivo base): {total_wordlist}.")
        print(" " + Blue + f"Guardada como {ARCHIVO_FINAL}'. Puedes usarla como herramientas de auditoría.")

    except Exception as e:
        print("\n\n "+ Red +f"Valida de Nuevo la Información {e}, ingresaste algún dato erróneo\n\n")
        os.system("python3 Password_Auditoria.py")

if __name__ == "__main__":
    main()
