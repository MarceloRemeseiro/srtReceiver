# streams.py
import json
import os

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
