# Tools Import
import pymem
import pymem.process
import keyboard
import time

# Patch Import
from patch import *

def main():
	print("CSGO_Thirdperson has launched.")
	switch = 0
	pm = pymem.Pymem('csgo.exe')
	client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
	
	while True:
		time.sleep(0.01)
		localplayer = pm.read_int(client + dwLocalPlayer)
		
		if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
			exit(0)

		if keyboard.is_pressed('z') and switch == 0:
			pm.write_int(localplayer + m_iObserverMode, 1)
			switch = 1
			time.sleep(0.5)

		elif keyboard.is_pressed('z') and switch == 1:
			pm.write_int(localplayer + m_iObserverMode, 0)
			switch = 0
			time.sleep(0.5)

if __name__ == '__main__':
	main()