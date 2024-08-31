#!/bin/bash

SRT_FILE="srt_streams.json"

# Inicializa el archivo JSON si no existe
initialize_json() {
    if [ ! -f "$SRT_FILE" ]; then
        echo "[]" > "$SRT_FILE"
    fi
}

# Carga los streams desde el archivo JSON
load_streams() {
    streams=$(jq -c '.[]' "$SRT_FILE")
}

# Muestra el menú
display_menu() {
    clear
    echo "Seleccione un stream SRT para reproducir o gestionar:"
    index=1
    echo "$streams" | while IFS= read -r stream; do
        name=$(echo "$stream" | jq -r '.name')
        echo "$index. $name"
        ((index++))
    done
    echo "a. Añadir nuevo stream SRT"
    echo "d. Borrar un stream SRT"
    echo "q. Salir"
}

# Añade un nuevo stream al JSON
add_new_stream() {
    read -p "Introduce el nombre del stream: " name
    read -p "Introduce el streamid: " streamid
    new_stream=$(jq -n --arg name "$name" --arg streamid "$streamid" '{"name": $name, "streamid": $streamid}')
    jq ". += [$new_stream]" "$SRT_FILE" > tmp.$$.json && mv tmp.$$.json "$SRT_FILE"
    load_streams
    echo "Stream SRT añadido: $name"
    read -p "Presione Enter para continuar..."
}

# Borra un stream del JSON
delete_stream() {
    read -p "Seleccione el número del stream SRT que desea borrar: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "$(echo "$streams" | wc -l)" ]]; then
        jq "del(.[$((choice-1))])" "$SRT_FILE" > tmp.$$.json && mv tmp.$$.json "$SRT_FILE"
        load_streams
        echo "Stream SRT eliminado."
    else
        echo "Opción no válida."
    fi
    read -p "Presione Enter para continuar..."
}

# Reproduce un stream con reconexión automática usando ffplay
play_stream() {
    selected_stream=$(echo "$streams" | sed -n "${1}p")
    streamid=$(echo "$selected_stream" | jq -r '.streamid')
    SRT_URL="srt://streamingpro.es:6000/?mode=caller&latency=1200&streamid=$streamid"

    while true; do
        echo "Intentando reproducir: $streamid"
        ffplay -fflags nobuffer -autoexit "$SRT_URL"
        echo "La conexión se perdió. Intentando reconectar en 5 segundos..."
        sleep 5
    done
}

# Función principal
main() {
    initialize_json
    load_streams

    while true; do
        display_menu
        read -p "Seleccione una opción: " choice

        if [[ "$choice" == "q" ]]; then
            break
        elif [[ "$choice" == "a" ]]; then
            add_new_stream
        elif [[ "$choice" == "d" ]]; then
            delete_stream
        elif [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "$(echo "$streams" | wc -l)" ]]; then
            play_stream "$choice"
        else
            echo "Opción no válida. Inténtelo de nuevo."
            read -p "Presione Enter para continuar..."
        fi
    done
}

# Ejecutar el script principal
main
