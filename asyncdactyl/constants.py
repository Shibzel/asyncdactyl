POWER_STATES = ("start", "stop", "restart", "kill")
class PowerState:
    start = POWER_STATES[0]
    stop = POWER_STATES[1]
    restart = POWER_STATES[2]
    kill = POWER_STATES[3]

REQUEST_TYPES = ("GET", "POST", "PATCH", "DELETE", "PUT")