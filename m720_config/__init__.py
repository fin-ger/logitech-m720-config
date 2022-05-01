"""
logitech-m720-config - A config script for Logitech M720 button mappings
Copyright (C) 2017  Fin Christensen <christensen.fin@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# logitech_receiver module ships with solaar package
from logitech_receiver.base import receivers
from logitech_receiver import Receiver

class SpecialKeysMseButtons:
    def __init__ (self):
        print("### CURRENTLY CONNECTED DEVICES ###")
        print("     path     vendor_id product_id serial release manufacturer product interface driver               bus_id isDevice")
        for recv in receivers():
            print (
                f"{recv.path!s:<13} {recv.vendor_id!s:<9} {recv.product_id!s:<10} {recv.serial!s:<6} {recv.release!s:<7} {recv.manufacturer!s:<12} {recv.product!s:<7} {recv.interface!s:<9} {recv.driver!s:<20} {recv.bus_id!s:<6} {recv.isDevice!s:<8}"
            )
        print()

        device_info = next (r for r in receivers () if r.product_id.lower() == "c52b")
        assert device_info

        self.receiver = Receiver.open (device_info)
        assert self.receiver

        self.m720 = next (d for d in self.receiver if d.codename == "M720 Triathlon")
        assert self.m720
        assert self.m720.ping ()

        self.features = list (self.m720.features)

        # https://lekensteyn.nl/files/logitech/x1b04_specialkeysmsebuttons.html#divertedButtonsEvent
        # https://lekensteyn.nl/files/logitech/logitech_hidpp_2.0_specification_draft_2012-06-04.pdf
        self.feature_index = self.features.index (0x1B04)
        self.software_id = 0xe # random number in [0x0;0xF]

    def get_count (self):
        return int.from_bytes (self.m720.request ((self.feature_index << 8) + (0 << 4) + self.software_id), byteorder='little')

    def get_cid_info (self, index):
        response = int.from_bytes (self.m720.request ((self.feature_index << 8) + (1 << 4) + self.software_id, index & 0xFF), byteorder='big')
        assert response

        response_length = 9
        response = response >> (16 - response_length) * 8

        cid    = response >> 7 * 8 & 0xFFFF
        tid    = response >> 5 * 8 & 0xFFFF
        flags1 = response >> 4 * 8 & 0xFF
        pos    = response >> 3 * 8 & 0xFF
        group  = response >> 2 * 8 & 0xFF
        gmask  = response >> 1 * 8 & 0xFF
        flags2 = response >> 0 * 8 & 0xFF

        virtual = bool (flags1 & (1 << 7))
        persist = bool (flags1 & (1 << 6))
        divert  = bool (flags1 & (1 << 5))
        reprog  = bool (flags1 & (1 << 4))
        fntog   = bool (flags1 & (1 << 3))
        hotkey  = bool (flags1 & (1 << 2))
        fkey    = bool (flags1 & (1 << 1))
        mouse   = bool (flags1 & (1 << 0))
        rawXY   = bool (flags2 & (1 << 0))

        return {
            "cid": cid,
            "tid": tid,
            "pos": pos,
            "group": group,
            "gmask": gmask,
            "virtual": virtual,
            "persist": persist,
            "divert": divert,
            "reprog": reprog,
            "fntog": fntog,
            "hotkey": hotkey,
            "fkey": fkey,
            "mouse": mouse,
            "rawXY": rawXY
        }

    def get_cid_reporting (self, control_id):
        response = int.from_bytes (self.m720.request (
            (self.feature_index << 8) + (2 << 4) + self.software_id,
            control_id & 0xFF00, control_id & 0x00FF
        ), byteorder='big')
        assert response

        response_length = 5
        response = response >> (16 - response_length) * 8

        cid   = response >> 3 * 8 & 0xFFFF
        flags = response >> 2 * 8 & 0xFF
        remap = response >> 0 * 8 & 0xFFFF

        rawXY   = bool (flags & (1 << 4))
        persist = bool (flags & (1 << 2))
        divert  = bool (flags & (1 << 0))

        return {
            "cid": cid,
            "rawXY": rawXY,
            "persist": persist,
            "divert": divert,
            "remap": remap
        }

    def set_cid_reporting (self, cid, divert, dvalid, persist, pvalid, rawXY, rvalid, remap):
        self.m720.request (
            (self.feature_index << 8) + (3 << 4) + self.software_id,
            cid & 0xFF00,
            cid & 0x00FF,
            (divert << 0) | (dvalid << 1) | (persist << 2) | (pvalid << 3) | (rawXY << 4) | (rvalid << 5),
            remap & 0xFF00,
            remap & 0x00FF
        )

def print_cid_info (buttons):
    cnt = buttons.get_count ()
    cids = []

    print ("### CID INFO ###")
    print ("  CID    TID  virtual persist divert reprog fntog hotkey fkey  mouse pos group gmask      rawXY")
    for i in range (cnt):
        cid_info = buttons.get_cid_info (i)
        cids += [cid_info["cid"]]
        print (
            "0x{cid:04X} 0x{tid:04X} {virtual!r:<7} {persist!r:<7} {divert!r:<6} {reprog!r:<6} {fntog!r:<5} "
            "{hotkey!r:<6} {fkey!r:<5} {mouse!r:<5} {pos:<3} {group:<5} {gmask:#010b} {rawXY!r:<5}".format (**cid_info)
        )
    return cids

def print_cid_reporting (buttons, cids):
    print ("### CID REPORTING ###")
    print ("  CID  rawXY persist divert remap")
    for cid in cids:
        cid_reporting = buttons.get_cid_reporting (cid)
        print (
            "0x{cid:04X} {rawXY!r:<5} {persist!r:<7} {divert!r:<6} 0x{remap:04X}".format (**cid_reporting)
        )

def main ():
    buttons = SpecialKeysMseButtons ()

    cids = print_cid_info (buttons)
    print ()
    print_cid_reporting (buttons, cids)
    print ()
    print ("### REMAP CID 0xD0 TO 0x53 ###")
    buttons.set_cid_reporting (0xD0, False, False, True, True, False, False, 0x53)
    print ()
    print_cid_reporting (buttons, cids)
