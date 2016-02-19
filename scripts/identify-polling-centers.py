#!/usr/bin/env
# -*- coding: utf-8 -*-
"""Takes a polling booths file as input and generates two files pb.txt and
pc.txt containing polling booths and polling centers respectively.
"""
import sys
import re
import itertools
import unidecode

re_ac = re.compile("[A-Z][A-Z]/AC\d{3}")


def get_ac(key):
    match = re_ac.search(key)
    return match.group()


re_paren = re.compile("\(.*\)")
re_non_alpha = re.compile("[^A-Za-z]+")

re_prefix = re.compile("^[A-Z][A-Z]\d{2,} -")
room_words = """
ROOM CENTER CENTRE PART BOOTH
NORTH SOUTH EAST WEST
AREA ROAD
KA
NAGAR NAG
दक्षिण उत्तरी पश्चिमी मध्य पूर्वी पशि पशिचम पश्चिम
भाग कमरा
के पास
रोड नगर
"""
re_symbols = re.compile("[0-9,. -]+")
re_room = re.compile(
    "(UTTARI|PURVI|PASHCHIMI|U|D) ?BHAG| .$| ..$| ...$|ी$|"
    + "|".join(room_words.strip().split()))


def normalize_name(name):
    # remove code prefix like "PB0001 -"
    name = re_prefix.sub("", name)

    # remove (stuff in side parenthesis)
    name = re_paren.sub("", name).strip()

    # remove words indicating room number
    name = re_room.sub("", name).strip()

    # replace dot, comma etc. with space
    # name = re_non_alpha.sub(" ", name)
    name = re_symbols.sub(" ", name)

    name = unidecode.unidecode(name.decode('utf-8'))

    return name.strip()


def process_rows(rows):
    for parent, key, name in rows:
        yield parent, key, normalize_name(name)


def read_booth_by_wl(filename):
    rows = (line.strip().split("\t", 3) for line in filename)
    return itertools.groupby(rows, lambda row: row[0])


def process_booths(wl, rows):
    pc = {}
    new_rows = []
    for parent, key, name, address in rows:
        address = normalize_name(address)
        pc_name = normalize_name(name)
        sign = pc_name.lower() + address.lower()
        if sign not in pc:
            ac = get_ac(wl)
            pc_code = "PX{:0>3}".format(len(pc) + 1)
            pc_key = "{}/{}".format(ac, pc_code)
            pc[sign] = [wl if 'WL000' not in wl else ac, pc_key, "{} - {}".format(pc_code, pc_name)]
        else:
            pc_key = pc[sign][1]

        pb_code = key.split("/")[-1]
        pb_name = "{} - {}".format(pb_code, name)
        new_rows.append([pc_key, key, pb_name])
    return sorted(pc.values()), new_rows


def write_rows(f, rows):
    for row in rows:
        f.write("\t".join(row))
        f.write("\n")


def main():
    pb_file = open("pb_new.txt", "w")
    px_file = open("pc.txt", "w")
    with open(sys.argv[1], 'r') as file:  # File should be sorted
        lines = sorted(file.readlines())
    for wl, rows in read_booth_by_wl(lines):  # WL = ward
        px_rows, pb_rows = process_booths(wl, rows)
        write_rows(px_file, px_rows)
        write_rows(pb_file, pb_rows)
    pb_file.close()
    px_file.close()
    print "write the output to pb.txt and pc.txt"


if __name__ == "__main__":
    main()
