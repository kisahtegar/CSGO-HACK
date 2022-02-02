# Tools Import
import pymem
import pymem.process
import keyboard
import time

# Patch Import
from patch import *

def main():
    print("CSGO_TriggerBotOP has launched.")
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    while True:
        time.sleep(0.01)
        localPlayer = pm.read_int(client + dwLocalPlayer)
        crosshairID = pm.read_int(localPlayer + m_iCrosshairId)
        getTeam = pm.read_int(client + dwEntityList + (crosshairID - 1) * 0x10)
        localTeam = pm.read_int(localPlayer + m_iTeamNum)
        crosshairTeam = pm.read_int(getTeam + m_iTeamNum)

        if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
            exit(0)

        if crosshairID > 0 and crosshairID < 32 and localTeam != crosshairTeam:
            pm.write_int(client + dwForceAttack, 6)

if __name__ == '__main__':
    main()