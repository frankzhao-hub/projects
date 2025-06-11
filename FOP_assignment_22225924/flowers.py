import random
class Flower:
    # A nectar source in the world grid.
    # • golden == True  → holds more nectar and gives double load.
    def __init__(self, ID, pos, golden=False):
        self.ID         = ID    # unique label, e.g. "flower7"
        self.pos        = pos    # (row, col) tuple on the world map
        self.golden     = golden  # True → special high-value flower

        # Current nectar units (“muj”).  Randomised so flowers start at
        # different fill levels:
        #   golden  → 2–6 units
        #   regular → 1–3 units
        self.muj        = random.randint(2, 6) if golden else random.randint(1, 3)

        # Maximum capacity once fully regrown:
        self.primemuj   = 6 if golden else 3     # maximum capacity

        # Countdown timer (in timesteps) until the next single unit of
        # nectar regrows.  Re-randomised every time a unit is collected.
        self.mujcomeback = random.randint(5, 10)

    # Bee calls collect_nectar() when it lands on this flower.
    # Returns the *amount* delivered to the comb:
    #   2 for golden (double load), 1 for regular, 0 if empty.
    # Also triggers the regrow timer.
    def collect_nectar(self):
        if self.muj > 0: # flower still has nectar?
            self.muj         -= 1   # remove one unit
            self.mujcomeback  = random.randint(5, 10)   # reset regrow timer
            return 2 if self.golden else 1   # payload to the bee
        return 0    # empty → nothing collected

    # Called once per simulation step.
    # Decrements the regrow timer; when it hits zero, add one unit
    # of nectar back (but never exceed primemuj).
    def step_changes(self):

        if self.muj < self.primemuj:  # only regrow if not full
            self.mujcomeback -= 1
            if self.mujcomeback <= 0:
                self.muj        += 1      # regrow one nectar unit
                self.mujcomeback = random.randint(5, 10)    # reset timer

    # RGB colour for plotting:
    #   • empty      → grey
    #   • golden     → bright yellow-gold
    #   • regular    → pink-magenta
    def colour(self):

        if self.muj == 0:
            return (0.6, 0.6, 0.6)  # drained
        if self.golden:
            return (1.0, 0.85, 0.20)  # golden flower
        return (0.87, 0.18, 0.38)  # ordinary flower



