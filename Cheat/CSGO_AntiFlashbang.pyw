# Tools Import
import pymem
import pymem.process
import keyboard
import time

# Patch Import
from patch import *

def main():
    print("CSGO_AntiFlashbang has launched.")
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    while True:
        time.sleep(0.01)
        if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
            exit(0)

        player = pm.read_int(client + dwLocalPlayer)
        if player:
            flash_value = player + m_flFlashMaxAlpha
            if flash_value:
                pm.write_float(flash_value, float(0))

if __name__ == '__main__':
    main()