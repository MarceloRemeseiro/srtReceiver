# srt_player.py
import curses
import subprocess
import time
import logging
import shutil

from streams import initialize_json, load_streams, save_streams, add_new_stream, delete_stream, edit_stream
from config import build_srt_url

def check_ffplay():
    return shutil.which("ffplay") is not None

def display_menu(stdscr, title, options, current_row):
    stdscr.clear()
    stdscr.addstr(0, 0, title, curses.A_BOLD)
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

def play_stream(stdscr, streams, index):
    """
    Reproduce el stream seleccionado utilizando ffplay.
    """
    if 0 <= index < len(streams):
        srt_url = streams[index]["url"]
        stream_name = streams[index]["name"]
        stdscr.clear()
        stdscr.addstr(0, 0, f"INTENTANDO REPRODUCIR: {stream_name.upper()}")
        stdscr.refresh()
        logging.info(f"Intentando reproducir el stream: {stream_name}")

        while True:
            try:
                ffplay_process = subprocess.Popen(
                    ["ffplay", "-fflags", "nobuffer", "-autoexit", "-i", srt_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                ffplay_process.wait()
            except KeyboardInterrupt:
                ffplay_process.terminate()
                ffplay_process.wait()
                return
            except Exception as e:
                stdscr.addstr(2, 0, f"Error al ejecutar ffplay: {e}")
                logging.error(f"Error al ejecutar ffplay: {e}")
                stdscr.refresh()
                stdscr.getch()
                return

            stdscr.clear()
            stdscr.addstr(0, 0, "CONEXIÓN PERDIDA. RECONEXIÓN EN 5 SEGUNDOS...")
            stdscr.refresh()
            time.sleep(5)

def main(stdscr):
    curses.curs_set(0)
    initialize_json()
    streams = load_streams()
    current_row = 0

    while True:
        menu_options = [stream['name'] for stream in streams] + ["AÑADIR NUEVO STREAM SRT", "EDITAR UN STREAM SRT", "BORRAR UN STREAM SRT", "SALIR"]
        display_menu(stdscr, "SELECCIONE UN STREAM SRT PARA REPRODUCIR O GESTIONAR:", menu_options, current_row)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
            current_row += 1
        elif key == ord('q') or key == ord('Q'):
            stdscr.clear()
            stdscr.addstr(0, 0, "¿SEGURO QUE QUIERES SALIR? (S/N)")
            stdscr.refresh()
            confirm = stdscr.getch()
            if confirm in [ord('s'), ord('S')]:
                break
            else:
                continue
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(streams):
                add_new_stream(stdscr, streams)
            elif current_row == len(streams) + 1:
                edit_stream(stdscr, streams)
            elif current_row == len(streams) + 2:
                delete_stream(stdscr, streams)
            elif current_row == len(streams) + 3:
                stdscr.clear()
                stdscr.addstr(0, 0, "¿SEGURO QUE QUIERES SALIR? (S/N)")
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm in [ord('s'), ord('S')]:
                    break
                else:
                    continue
            else:
                play_stream(stdscr, streams, current_row)
        logging.info(f"Opción seleccionada: {menu_options[current_row]}")
    logging.info("Aplicación finalizada.")

if __name__ == "__main__":
    logging.basicConfig(
        filename='srt_player.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    if not check_ffplay():
        print("Error: ffplay no está instalado. Por favor, instala ffplay para usar esta aplicación.")
    else:
        curses.wrapper(main)
