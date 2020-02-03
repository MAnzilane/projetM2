from enum import Enum

class Mvt_State(Enum):
	FORWARD  = 0
	BACKWARD = 1
	IDLE     = 2
	ROTATE   = 3

class Direction_State(Enum):
	STRAIGHT     = 0
	RIGHT        = 1
	LEFT         = 2
	MANUALLY_SET = 3

class State(Enum):
	FINE	= 0
	IMPACT	= 1
	BLOCKED = 2

class Routine_Running(Enum):
	NONE     = 0
	AVOIDING = 1
	UNBLOCKING = 2
	
class Sought_Routine(Enum):
	NONE     = 0
	AVOID    = 1
	UNBLOCK  = 2
	STOP     = 3
