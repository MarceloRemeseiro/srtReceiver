import curses
import json
import os
import subprocess
import time
import select

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
    stdscr.addstr(2, 0, "INTRODUCE EL STREAMID: ")
    streamid = stdscr.getstr(3, 0).decode('utf-8')
    streams.append({"name": name, "streamid": streamid})
    save_streams(streams)
    stdscr.addstr(5, 0, f"STREAM SRT AÑADIDO: {name.upper()}")
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

def play_stream(stdscr, streams, index):
    if 0 <= index < len(streams):
        streamid = streams[index]["streamid"]
        SRT_URL = f"srt://streamingpro.es:6000/?mode=caller&latency=1200&streamid={streamid}"
        stdscr.clear()
        stdscr.addstr(0, 0, f"INTENTANDO REPRODUCIR: {streams[index]['name'].upper()}")
        stdscr.refresh()

        while True:
            ffplay_process = subprocess.Popen(["ffplay", "-fflags", "nobuffer", "-i", SRT_URL], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ffplay_fd = ffplay_process.stderr.fileno()
            poller = select.poll()
            poller.register(ffplay_fd, select.POLLIN)

            while True:
                events = poller.poll(100)
                if events:
                    output = ffplay_process.stderr.readline()
                    if b"Input/output error" in output:
                        ffplay_process.terminate()
                        ffplay_process.wait()
                        stdscr.clear()
                        stdscr.addstr(0, 0, "CONEXIÓN PERDIDA. RECONEXIÓN EN 5 SEGUNDOS...")
                        stdscr.refresh()
                        time.sleep(5)
                        break  # Reinicia ffplay después de 5 segundos
                else:
                    key = stdscr.getch()
                    if key == 27:  # ESC key
                        ffplay_process.terminate()
                        ffplay_process.wait()
                        return

                # Si ffplay ha terminado de forma inesperada
                if ffplay_process.poll() is not None:
                    break

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
