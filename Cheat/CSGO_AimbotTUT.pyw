# Tools Import
import pymem
import pymem.process
import keyboard
import time
from math import sqrt, pi, atan

# Patch Import
from patch import *

print("CSGO_AimbotTUT has launched.")
pm = pymem.Pymem("csgo.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

aimfov = 120

def normalizeAngles(viewAngleX, viewAngleY):
	if viewAngleX > 89:
		viewAngleX -= 360
	if viewAngleX < -89:
		viewAngleX += 360
	if viewAngleY > 180:
		viewAngleY -= 360
	if viewAngleY < 180:
		viewAngleY += 360
	return viewAngleX, viewAngleY

def checkangles(x, y):
	if x > 89:
		return False
	elif x < -89:
		return False
	elif y > 360:
		return False
	elif y < -360:
		return False
	else:
		return True

def nanchecker(first, second):
	if math.insan(first) or math.insan(second):
		return False
	else:
		return True

def calc_distance(current_x, current_y, new_x, new_y):
	distancex = new_x - current_x
	if distancex < -89:
		distancex += 360
	elif distancex > 89:
		distancex -= 360
	if distancex < 0.0:
		distancex = -distancex

	distancey = new_y - current_y
	if distancey < -180:
		distancey += 360
	elif distancey > 180:
		distancey -= 360
	if distancey < 0.0:
		distancey = -distancey

	return distancex, distancey

def calcangle(localpos1, localpos2, localpos3, enemypos1, enemypos2, enemypos3):
	try:
		delta_x = localpos1 - enemypos1
		delta_y = localpos2 - enemypos2
		delta_z = localpos3 - enemypos3
		hyp = sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
		x = atan(delta_z / hyp) * 180 / pi
		y = atan(delta_y / delta_x) * 180 / pi
		if delta_x >= 0.0:
			y += 180.0
		return x, y
	except:
		pass

def main():
	player = pm.read_int(client + dwLocalPlayer)
	engine_pointer = pm.read_int(engine + dwClientState)
	localTeam = pm.read_int(player + m_iTeamNum)

	while True:
		time.sleep(0.01)
		target = None
		olddistx = 111111111111
		olddisty = 111111111111

		for i in range(1, 32):
			entity = pm.read_int(client + dwEntityList + i * 0x10)

			if entity:
				try:
					entity_team_id = pm.read_int(entity + m_iTeamNum)
					entity_hp = pm.read_int(entity + m_iHealth)
					entity_dormant = pm.read_int(entity + m_bDormant)
				except:
					print('Finds player info once')

				if localTeam != entity_team_id and entity_hp > 0:
					entity_bones = pm.read_int(entity + m_dwBoneMatrix)
					localpos_x_angles = pm.read_float(engine_pointer + dwClientState_ViewAngles)
					localpos_y_angles = pm.read_float(engine_pointer + dwClientState_ViewAngles + 0x4)
					localpos_z_angles = pm.read_float(player + m_vecViewOffset + 0x8)
					localpos1 = pm.read_float(player + m_vecOrigin)
					localpos2 = pm.read_float(player + m_vecOrigin + 4)
					localpos3 = pm.read_float(player + m_vecOrigin + 8) + localpos_z_angles

					try:
						entitypos_x = pm.read_float(entity_bones + 0x30 * 8 + 0xC)
						entitypos_y = pm.read_float(entity_bones + 0x30 * 8 + 0x1C)
						entitypos_z = pm.read_float(entity_bones + 0x30 * 8 + 0x2C)
					except:
						continue
					X, Y = calcangle(localpos1, localpos2, localpos3, entitypos_x, entitypos_y, entitypos_z)
					newdist_x,  newdist_y = calc_distance(localpos_x_angles, localpos_y_angles, X, Y)

					if newdist_x < olddistx and newdist_y < olddisty and newdist_x <= aimfov and newdist_y <= aimfov:
						olddistx, olddisty = newdist_x, newdist_y
						target, target_hp, target_dormant = entity, entity_hp, entity_dormant
						target_x, target_y, target_z = entitypos_x, entitypos_y, entitypos_z

				if keyboard.is_pressed('alt') and player:
					if target and target_hp > 0 and not target_dormant:
						x, y = calcangle(localpos1, localpos2, localpos3, target_x, target_y, target_z)
						normalize_x, normalize_y = normalizeAngles(x, y)

						pm.write_float(engine_pointer + dwClientState_ViewAngles, normalize_x)
						pm.write_float(engine_pointer + dwClientState_ViewAngles + 0x4, normalize_y)

				if keyboard.is_pressed('End') or keyboard.is_pressed('F10'):
					exit(0)

if __name__ == '__main__':
	main()