import curses
import json
import os
import subprocess
import time

SRT_FILE = "srt_streams.json"
LOG_FILE = "srt_player.log"

# Inicializa el archivo JSON si no existe
def initialize_json():
    if not os.path.exists(SRT_FILE):
        with open(SRT_FILE, 'w') as f:
            json.dump([], f)

# Carga los streams desde el archivo JSON
def load_streams():
    with open(SRT_FILE, 'r') as f:
        return json.load(f)

# Guarda los streams en el archivo JSON
def save_streams(streams):
    with open(SRT_FILE, 'w') as f:
        json.dump(streams, f)

# Añade un nuevo stream al JSON
def add_new_stream(stdscr, streams):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "INTRODUCE EL NOMBRE DEL STREAM: ")
    name = stdscr.getstr(1, 0).decode('utf-8')
    stdscr.addstr(2, 0, "INTRODUCE EL STREAMID: ")
    streamid = stdscr.getstr(3, 0).decode('utf-8')
    streams.append({"name": name, "streamid": streamid})
    save_streams(streams)
    stdscr.addstr(5, 0, f"STREAM SRT AÑADIDO: {name.upper()}")
    stdscr.refresh()
    stdscr.getch()

# Borra un stream del JSON
def delete_stream(stdscr, streams):
    if not streams:
        stdscr.addstr(5, 0, "NO HAY STREAMS SRT PARA BORRAR.")
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "SELECCIONE EL STREAM SRT QUE DESEA BORRAR:", curses.A_BOLD)

        for idx, stream in enumerate(streams):
            x = 2
            y = idx + 1
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, stream['name'].upper())
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, stream['name'].upper())

        stdscr.addstr(len(streams) + 2, 2, "CANCELAR", curses.A_REVERSE if current_row == len(streams) else curses.A_NORMAL)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(streams):
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(streams):
                return  # Volver al menú principal
            else:
                stdscr.clear()
                stdscr.addstr(0, 0, f"¿SEGURO QUE QUIERES BORRAR '{streams[current_row]['name'].upper()}'? (S/N)")
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm == ord('s') or confirm == ord('S'):
                    del streams[current_row]
                    save_streams(streams)
                    stdscr.addstr(2, 0, "STREAM SRT BORRADO.")
                    stdscr.refresh()
                    stdscr.getch()
                return  # Volver al menú principal

# Reproduce un stream con reconexión automática usando ffplay
def play_stream(stdscr, streams, index):
    if 0 <= index < len(streams):
        streamid = streams[index]["streamid"]
        SRT_URL = f"srt://streamingpro.es:6000/?mode=caller&latency=1200&streamid={streamid}"
        stdscr.clear()
        stdscr.addstr(0, 0, f"INTENTANDO REPRODUCIR: {streams[index]['name'].upper()}")
        stdscr.refresh()

        while True:
            # Registro de inicio de reproducción
            with open(LOG_FILE, 'a') as log:
                log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Intentando reproducir: {streams[index]['name'].upper()} con StreamID: {streamid}\n")
            
            # Ejecuta ffplay en un subproceso
            ffplay_process = subprocess.Popen(
                ["ffplay", "-fflags", "nobuffer", "-i", SRT_URL],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            try:
                while ffplay_process.poll() is None:
                    key = stdscr.getch()
                    if key == 27:  # ESC key
                        ffplay_process.terminate()
                        ffplay_process.wait()
                        return
                # Si el proceso terminó, esperamos 5 segundos y reiniciamos
                stdscr.addstr(1, 0, "CONEXIÓN PERDIDA. RECONEXIÓN EN 5 SEGUNDOS...")
                stdscr.refresh()
                with open(LOG_FILE, 'a') as log:
                    log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Conexión perdida. Intentando reconectar en 5 segundos...\n")
                time.sleep(5)
            except Exception as e:
                stdscr.addstr(2, 0, f"ERROR: {str(e)}")
                stdscr.refresh()
                ffplay_process.terminate()
                ffplay_process.wait()
                return

# Función principal que maneja el menú
def main(stdscr):
    curses.curs_set(0)  # Ocultar el cursor

    streams = load_streams()
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "SELECCIONE UN STREAM SRT PARA REPRODUCIR O GESTIONAR:", curses.A_BOLD)

        for idx, stream in enumerate(streams):
            x = 2
            y = idx + 1
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, stream['name'].upper())
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, stream['name'].upper())

        stdscr.addstr(len(streams) + 2, 2, "AÑADIR NUEVO STREAM SRT", curses.A_REVERSE if current_row == len(streams) else curses.A_NORMAL)
        stdscr.addstr(len(streams) + 3, 2, "BORRAR UN STREAM SRT", curses.A_REVERSE if current_row == len(streams) + 1 else curses.A_NORMAL)
        stdscr.addstr(len(streams) + 4, 2, "SALIR", curses.A_REVERSE if current_row == len(streams) + 2 else curses.A_NORMAL)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(streams) + 2:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(streams):
                add_new_stream(stdscr, streams)
            elif current_row == len(streams) + 1:
                delete_stream(stdscr, streams)
            elif current_row == len(streams) + 2:
                break
            else:
                play_stream(stdscr, streams, current_row)

if __name__ == "__main__":
    initialize_json()
    curses.wrapper(main)
