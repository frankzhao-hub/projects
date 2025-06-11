import random
from worker import Worker

class QueenBee:
    """
    Queen that ages, dies after a random life‑span (500‑700 ticks),
    and spawns a new Worker every 30 ticks while alive.
    """

    # Constructor: set up identity, location, portal coords,
    #              and life-cycle parameters.
    def __init__(self, ID, pos,
                 hive_exit, hive_entrance, world_entrance):
        self.ID                = ID  # e.g. "queen"
        self.pos               = pos   # (row, col) inside the hive grid

        # Remember the three portals so new workers know the routes
        self.honeyholdexit     = hive_exit  # hive → world
        self.honeyholdentrance = hive_entrance   # world → hive
        self.humanityentrance  = world_entrance   # matching cell outside

        # Life-cycle counters
        self.age       = 0    # how many ticks lived
        self.max_age   = random.randint(500, 700)  # random life span
        self.spawn_cd  = 30          # countdown to next spawn
        self.alive     = True      # becomes False when she die

    # step_change() is called **once per simulation tick**.
    # * increments age
    # * kills queen if age limit reached
    # * spawns a new worker every 30 ticks while alive

    def step_change(self, hexslot, beetlejuices, genes):

        if not self.alive:
            return   # queen already dead → nothing to do

        # ageing and death
        self.age += 1
        if self.age >= self.max_age:   # natural death check
            self.alive = False
            return

        # spawning
        self.spawn_cd -= 1     # countdown one tick
        if self.spawn_cd <= 0:    # time to lay an egg?
            new_id = "w" + str(len(beetlejuices) + 1)    # generate "wN"
            beetlejuices.append(
                Worker(
                    new_id,
                    self.pos,                  # newborn appears at queen’s cell
                    self.honeyholdexit,
                    self.honeyholdentrance,
                    self.humanityentrance
                )
            )
            self.spawn_cd = 30                # reset 30-tick timer











