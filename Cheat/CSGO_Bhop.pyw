# Tools Import
import keyboard
import pymem
import pymem.process
import time

# Patch Import
from patch import *

def main():
    print("CSGO_Bhop has launched.")
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    while True:
        time.sleep(0.01)
        if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
            exit(0)
            
        if keyboard.is_pressed("space"):
            force_jump = client + dwForceJump
            player = pm.read_int(client + dwLocalPlayer)            
            on_ground = pm.read_int(player + m_fFlags)
            if player and on_ground and on_ground == 257:
                pm.write_int(force_jump, 5)
                time.sleep(0.08)
                pm.write_int(force_jump, 4)

if __name__ == '__main__':
    main()