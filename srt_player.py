# srt_player.py
import curses
import subprocess
import time
from streams import initialize_json, load_streams, add_new_stream, delete_stream
from config import build_srt_url

def play_stream(stdscr, streams, index):
    if 0 <= index < len(streams):
        srt_url = streams[index]["url"]
        stdscr.clear()
        stdscr.addstr(0, 0, f"INTENTANDO REPRODUCIR: {streams[index]['name'].upper()}")
        stdscr.refresh()

        while True:
            ffplay_process = subprocess.Popen(["ffplay", "-fflags", "nobuffer", "-autoexit", "-i", srt_url])

            try:
                while True:
                    ffplay_process.wait()
                    break
            except KeyboardInterrupt:
                ffplay_process.terminate()
                ffplay_process.wait()
                return

            stdscr.clear()
            stdscr.addstr(0, 0, "CONEXIÓN PERDIDA. RECONEXIÓN EN 5 SEGUNDOS...")
            stdscr.refresh()
            time.sleep(5)

def main(stdscr):
    curses.curs_set(0)
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
