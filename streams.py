import json
import os
import curses

SRT_FILE = "srt_streams.json"

def initialize_json():
    if not os.path.exists(SRT_FILE):
        with open(SRT_FILE, 'w') as f:
            json.dump([], f)

def load_streams():
    with open(SRT_FILE, 'r') as f:
        return json.load(f)

def save_streams(streams):
    with open(SRT_FILE, 'w') as f:
        json.dump(streams, f)

def add_new_stream(stdscr, streams):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "INTRODUCE EL NOMBRE DEL STREAM: ")
    name = stdscr.getstr(1, 0).decode('utf-8')
    stdscr.addstr(2, 0, "INTRODUCE LA URL DEL SERVIDOR (O DEJA EN BLANCO PARA EL DEFAULT): ")
    url = stdscr.getstr(3, 0).decode('utf-8')
    stdscr.addstr(4, 0, "INTRODUCE EL PUERTO (O DEJA EN BLANCO PARA EL DEFAULT): ")
    port = stdscr.getstr(5, 0).decode('utf-8')
    stdscr.addstr(6, 0, "INTRODUCE LA LATENCIA EN MS (O DEJA EN BLANCO PARA EL DEFAULT): ")
    latency = stdscr.getstr(7, 0).decode('utf-8')
    stdscr.addstr(8, 0, "INTRODUCE EL STREAMID (O DEJA EN BLANCO SI NO LO NECESITA): ")
    streamid = stdscr.getstr(9, 0).decode('utf-8')

    from config import build_srt_url
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
