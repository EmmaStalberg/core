"""Module to search for addresses or coordinates using the OpenStreetMap API."""

import csv

OSM_SHAREABLE_URL = "https://www.openstreetmap.org/?mlat=%d&mlon=%d#map=%d/%d/%d"


def add_note(coordinates : dict[str, float], msg : str):
    """Find route between two coordinates."""
    with open('notes.csv', mode='a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([coordinates["lon"], coordinates["lat"], msg])


def get_notes():
    """Return a list of notes to the frontend to show."""
    stored_notes = {}
    with open('notes.csv', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            stored_notes[str(reader.index(row))] = {"lon" : row[0], "lat" : row[1], "msg" : row[2]}#some shit here
    return stored_notes

def get_share_link(coordinates : dict[str, float], zoom : int):
    """Find restaurants near route where it is clicked."""

    return (OSM_SHAREABLE_URL % coordinates["lat"], coordinates["lon"], str(zoom), coordinates["lat"], coordinates["lon"])
