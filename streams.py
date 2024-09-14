import json
import os
import curses

from config import build_srt_url

SRT_FILE = "srt_streams.json"

def initialize_json():
    if not os.path.exists(SRT_FILE):
        with open(SRT_FILE, 'w') as f:
            json.dump([], f)

def load_streams():
    try:
        with open(SRT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_streams(streams):
    try:
        with open(SRT_FILE, 'w') as f:
            json.dump(streams, f)
    except IOError as e:
        print(f"Error al guardar los streams: {e}")

def add_new_stream(stdscr, streams):
    """
    Solicita al usuario los datos para un nuevo stream y lo añade a la lista.
    """
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "INTRODUCE EL NOMBRE DEL STREAM: ")
    name = stdscr.getstr(1, 0).decode('utf-8').strip()
    if not name:
        stdscr.addstr(2, 0, "EL NOMBRE NO PUEDE ESTAR VACÍO.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(2, 0, "INTRODUCE LA URL DEL SERVIDOR (O DEJA EN BLANCO PARA EL DEFAULT): ")
    url = stdscr.getstr(3, 0).decode('utf-8').strip()

    stdscr.addstr(4, 0, "INTRODUCE EL PUERTO (O DEJA EN BLANCO PARA EL DEFAULT): ")
    port = stdscr.getstr(5, 0).decode('utf-8').strip()
    if port and not port.isdigit():
        stdscr.addstr(6, 0, "EL PUERTO DEBE SER UN NÚMERO ENTERO.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(6, 0, "INTRODUCE LA LATENCIA EN MS (O DEJA EN BLANCO PARA EL DEFAULT): ")
    latency = stdscr.getstr(7, 0).decode('utf-8').strip()
    if latency and not latency.isdigit():
        stdscr.addstr(8, 0, "LA LATENCIA DEBE SER UN NÚMERO ENTERO.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(8, 0, "INTRODUCE EL STREAMID (O DEJA EN BLANCO SI NO LO NECESITA): ")
    streamid = stdscr.getstr(9, 0).decode('utf-8').strip()

    srt_url = build_srt_url(url, port, latency, streamid)

    streams.append({"name": name, "url": srt_url})
    save_streams(streams)
    stdscr.addstr(11, 0, f"STREAM SRT AÑADIDO: {name.upper()}")
    stdscr.refresh()
    stdscr.getch()

def delete_stream(stdscr, streams):
    if not streams:
        stdscr.addstr(5, 0, "NO HAY STREAMS SRT PARA BORRAR.")
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0
    while True:
        options = [stream['name'] for stream in streams] + ["CANCELAR"]
        stdscr.clear()
        stdscr.addstr(0, 0, "SELECCIONE EL STREAM SRT QUE DESEA BORRAR:", curses.A_BOLD)
        for idx, option in enumerate(options):
            x = 2
            y = idx + 1
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, option.upper())
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option.upper())
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) -1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(options) -1:
                return  # Volver al menú principal
            else:
                stdscr.clear()
                stdscr.addstr(0, 0, f"¿SEGURO QUE QUIERES BORRAR '{streams[current_row]['name'].upper()}'? (S/N)")
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm in [ord('s'), ord('S')]:
                    del streams[current_row]
                    save_streams(streams)
                    stdscr.addstr(2, 0, "STREAM SRT BORRADO.")
                    stdscr.refresh()
                    stdscr.getch()
                return  # Volver al menú principal

def edit_stream(stdscr, streams):
    if not streams:
        stdscr.addstr(5, 0, "NO HAY STREAMS SRT PARA EDITAR.")
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0
    while True:
        options = [stream['name'] for stream in streams] + ["CANCELAR"]
        stdscr.clear()
        stdscr.addstr(0, 0, "SELECCIONE EL STREAM SRT QUE DESEA EDITAR:", curses.A_BOLD)
        for idx, option in enumerate(options):
            x = 2
            y = idx + 1
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, option.upper())
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option.upper())
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) -1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(options) -1:
                return  # Volver al menú principal
            else:
                edit_selected_stream(stdscr, streams, current_row)
                return  # Volver al menú principal

def edit_selected_stream(stdscr, streams, index):
    curses.echo()
    stdscr.clear()
    stream = streams[index]
    stdscr.addstr(0, 0, f"EDITANDO EL STREAM: {stream['name'].upper()}")

    stdscr.addstr(2, 0, "INTRODUCE EL NUEVO NOMBRE (O DEJA EN BLANCO PARA MANTENERLO): ")
    name = stdscr.getstr(3, 0).decode('utf-8').strip()
    if not name:
        name = stream['name']

    stdscr.addstr(4, 0, "INTRODUCE LA NUEVA URL DEL SERVIDOR (O DEJA EN BLANCO PARA MANTENERLA): ")
    url = stdscr.getstr(5, 0).decode('utf-8').strip()

    stdscr.addstr(6, 0, "INTRODUCE EL NUEVO PUERTO (O DEJA EN BLANCO PARA MANTENERLO): ")
    port = stdscr.getstr(7, 0).decode('utf-8').strip()
    if port and not port.isdigit():
        stdscr.addstr(8, 0, "EL PUERTO DEBE SER UN NÚMERO ENTERO.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(8, 0, "INTRODUCE LA NUEVA LATENCIA EN MS (O DEJA EN BLANCO PARA MANTENERLA): ")
    latency = stdscr.getstr(9, 0).decode('utf-8').strip()
    if latency and not latency.isdigit():
        stdscr.addstr(10, 0, "LA LATENCIA DEBE SER UN NÚMERO ENTERO.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(10, 0, "INTRODUCE EL NUEVO STREAMID (O DEJA EN BLANCO PARA MANTENERLO): ")
    streamid = stdscr.getstr(11, 0).decode('utf-8').strip()

    srt_url = build_srt_url(url or None, port or None, latency or None, streamid or None)

    streams[index] = {"name": name, "url": srt_url}
    save_streams(streams)
    stdscr.addstr(13, 0, f"STREAM SRT EDITADO: {name.upper()}")
    stdscr.refresh()
    stdscr.getch()
