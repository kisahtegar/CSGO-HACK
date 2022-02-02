# Tools Import
import pymem
import pymem.process
import keyboard
import time

# Patch Import
from patch import *

def main():
	print("CSGO_Chams has launched.")
	pm = pymem.Pymem("csgo.exe")
	client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

	rgbT  = [255, 51, 0]
	rgbCT = [0, 51, 255]

	while True:
		time.sleep(0.01)
		if keyboard.is_pressed("End") or keyboard.is_pressed("F10"):
			exit(0)
		try:
			for i in range(32):
				entity = pm.read_int(client + dwEntityList + i * 0x10)
				if entity:
					entity_team_id = pm.read_int(entity + m_iTeamNum)

					if entity_team_id == 2: #Terrorist
						pm.write_int(entity + m_clrRender, (rgbT[0])) #R
						pm.write_int(entity + m_clrRender + 0x1, (rgbT[1])) #G
						pm.write_int(entity + m_clrRender + 0x2, (rgbT[2])) #G

					elif entity_team_id == 3:
						pm.write_int(entity + m_clrRender, (rgbCT[0])) #R
						pm.write_int(entity + m_clrRender + 0x1, (rgbCT[1])) #G
						pm.write_int(entity + m_clrRender + 0x2, (rgbCT[2])) #B
				else:
					pass
		except Exception as e:
			print(e)

if __name__ == '__main__':
	main()