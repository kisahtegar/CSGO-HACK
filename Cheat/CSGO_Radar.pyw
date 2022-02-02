# Tools Import
import pymem
import pymem.process
import keyboard
import time

# Patch Import
from patch import *

def main():
	print("CSGO_Radar has launched.")
	pm = pymem.Pymem("csgo.exe")
	client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

	while True:
		time.sleep(0.01)
		if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
			exit(0)

		for i in range(1,32):
			entity = pm.read_int(client + dwEntityList + i * 0x10)
			if entity:
				pm.write_uchar(entity + m_bSpotted, 1)

if __name__ == '__main__':
	main()