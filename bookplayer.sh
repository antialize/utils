#!/bin/bash

mkdir -p ~/.books
UUID="$1/.uuid"
if ! [ -e "$UUID" ]; then
    uuid > "$UUID"
fi
UUID=$(cat "$UUID")
DB=~/.books/$UUID
echo "$DB"
touch "$DB"
IFS="
"

function control_c() {
    exit
}

trap control_c SIGINT SIGTERM SIGQUIT

for name in $(find "$1" -iname '*.mp3' -or -iname '*.flac'  | atsort ); do
    nh=$(echo "$name" | sha1sum | sed -re 's/([a-z0-9]*).*/\1/')
    if ! grep -q "$nh" "$DB"; then
	mplayer "$name"
	echo "$nh" >> "$DB"
    fi
done

