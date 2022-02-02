# Tools Import
import pymem.process
import keyboard
import pymem
import time
from math import asin, atan2

# Patch Import
from patch import *

class Vector3:
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, scale):
        return Vector3(self.x * scale, self.y * scale, self.z * scale)
    def __str__(self):
        return f"(x: {str(self.x)}, y: {str(self.y)}, z: {str(self.z)})"
    def __repr__(self):
        return f"(x: {str(self.x)}, y: {str(self.y)}, z: {str(self.z)})"

    def distanceTo(self, other):
        delta = other - self; return ((delta.x ** 2) + (delta.y ** 2) + (delta.z ** 2))**(0.5)

pm = pymem.Pymem()
pm.open_process_from_name("csgo.exe")

client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll



def getPlayer(index: int) -> int: 
    return pm.read_int(client + dwEntityList + (index * 0x10))

def getLocalPlayer() -> int:
    return pm.read_int(client + dwLocalPlayer)
    
def getPlayerTeam(player: int) -> int:
    return pm.read_int(player + m_iTeamNum)

def getPlayerHealth(player: int) -> int:
    return pm.read_int(player + m_iHealth)
    
def isDormant(player: int) -> bool:
    return bool(pm.read_int(player + m_bDormant))

def getGlowObjectManager() -> int:
    return pm.read_int(client + dwGlowObjectManager)

def getPlayerGlowIndex(player: int) -> int:
    return pm.read_int(player + m_iGlowIndex)

def sameTeam(player: int) -> bool:
    return getPlayerTeam(player) == getPlayerTeam(getLocalPlayer())

def isDead(player: int) -> bool:
    return getPlayerHealth(player) < 1 or getPlayerHealth(player) > 100

def isVisible(player: int) -> bool:
    clientState = pm.read_int(engine + dwClientState)
    localPlayerId = pm.read_int(clientState + dwClientState_GetLocalPlayer)

    spottedByMask = pm.read_int(player + m_bSpottedByMask)

    return spottedByMask & (1 << localPlayerId)

def getPlayerLocation(player: int) -> Vector3:
    return Vector3(
        x = pm.read_float(player + m_vecOrigin + 0x0),
        y = pm.read_float(player + m_vecOrigin + 0x4),
        z = pm.read_float(player + m_vecOrigin + 0x8),
    )

def getPlayerBoneLocation(player: int, bone: int) -> Vector3:
    boneMatrix = pm.read_int(player + m_dwBoneMatrix)
    return Vector3(
        x = pm.read_float(boneMatrix + 0x30 * bone + 0x0C),
        y = pm.read_float(boneMatrix + 0x30 * bone + 0x1C),
        z = pm.read_float(boneMatrix + 0x30 * bone + 0x2C),
    )

def getLocalPlayerViewOffset() -> Vector3:
    return Vector3(
        x = pm.read_float(getLocalPlayer() + m_vecViewOffset + 0x0),
        y = pm.read_float(getLocalPlayer() + m_vecViewOffset + 0x4),
        z = pm.read_float(getLocalPlayer() + m_vecViewOffset + 0x8),
    )

def getLocalPlayerViewAngles() -> Vector3:
    clientState = pm.read_int(engine  + dwClientState); return Vector3(
        x = pm.read_float(clientState + dwClientState_ViewAngles + 0x0),
        y = pm.read_float(clientState + dwClientState_ViewAngles + 0x4),
        z = pm.read_float(clientState + dwClientState_ViewAngles + 0x8),
    )

def writeLocalPlayerViewAngles(x: float, y: float) -> None:
    if y >  180.0: y -= 360.0
    if y < -180.0: y += 360.0
    if x >   89.0: x -= 180.0
    if x <  -89.0: x += 180.0

    clientState = pm.read_int(engine + dwClientState)
    pm.write_float(clientState + dwClientState_ViewAngles + 0x0, x)
    pm.write_float(clientState + dwClientState_ViewAngles + 0x4, y)

def forceLocalPlayerAimTo(target: Vector3) -> None:
    localPlayerHead = getPlayerLocation(getLocalPlayer()) + getLocalPlayerViewOffset()

    delta       = target - localPlayerHead
    deltaLength = localPlayerHead.distanceTo(target)

    writeLocalPlayerViewAngles(-asin(delta.z / deltaLength) * (180.0 / 3.14159235368979), atan2(delta.y , delta.x    ) * (180.0 / 3.14159235368979))

def glowPlayer(player: int) -> None:
    entityGlow  = getPlayerGlowIndex(player)
    glowManager = getGlowObjectManager()

    if sameTeam(player):
        pm.write_float(glowManager + entityGlow * 0x38 + 0x4 , float(0))
        pm.write_float(glowManager + entityGlow * 0x38 + 0x8 , float(0))
        pm.write_float(glowManager + entityGlow * 0x38 + 0xC , float(1))
        pm.write_float(glowManager + entityGlow * 0x38 + 0x10, float(1))
        pm.write_int  (glowManager + entityGlow * 0x38 + 0x24, int  (1))
    else:
        pm.write_float(glowManager + entityGlow * 0x38 + 0x4 , float(1))
        pm.write_float(glowManager + entityGlow * 0x38 + 0x8 , float(0))
        pm.write_float(glowManager + entityGlow * 0x38 + 0xC , float(0))
        pm.write_float(glowManager + entityGlow * 0x38 + 0x10, float(1))
        pm.write_int  (glowManager + entityGlow * 0x38 + 0x24, int  (1))

def findClosestValidEnemy() -> bool or int:

    closestDistance      = 99999999.99
    closestDistanceIndex = -1

    for i in range(1, 32):
        entity = getPlayer(i)

        if not entity            : continue
        if not isVisible(entity) : continue

        if isDormant(entity)     : continue
        if isDead   (entity)     : continue
        if sameTeam (entity)     : continue

        currentDistance = getPlayerLocation(getLocalPlayer() ).distanceTo( getPlayerLocation(entity))
        
        if  currentDistance      < closestDistance:
            closestDistance      = currentDistance
            closestDistanceIndex = i

    return False if closestDistanceIndex == -1 else closestDistanceIndex

def main():
    while True:
        time.sleep(0.01)
        if keyboard.is_pressed('end') or keyboard.is_pressed('F10'): exit(0)
        
        if keyboard.is_pressed('alt'):
            entity = findClosestValidEnemy()
            if entity:forceLocalPlayerAimTo(getPlayerBoneLocation(getPlayer(entity), bone = 8))
        
        for i in range(1, 32):
            entity = getPlayer(i)
            if entity:glowPlayer(entity)
            
if __name__ == '__main__' : main()