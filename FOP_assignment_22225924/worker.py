
import random
class Worker:

    # One worker-bee: handles movement, nectar collecting,
    # depositing, ageing, and death.
    def __init__(self, ID, pos, hive_exit, hive_entrance, world_entrance,
                 detection_range=5):
        # Identity & starting position
        self.ID                = ID   # e.g. "w3"
        self.pos               = pos    # (row, col) inside hive at spawn

        # Portal coordinates (shared with queen/wasp logic)
        self.honeyholdexit     = hive_exit # hive → world
        self.honeyholdentrance = hive_entrance  # world → hive
        self.humanityentrance  = world_entrance  # matching cell outside

        # “Vision” distance (Manhattan) for flower hunting
        self.aimrange          = detection_range

        # Life-cycle counters
        self.age          = 0
        self.max_age      = random.randint(120, 200)  # random life span
        self.inhoneyhold  = True   # starts inside hive
        self.hasmuj       = False   # carrying nectar right now?
        self.depositing   = False   # currently heading to comb?
        self.resttime   = 0           # small delay when loading/idle
        self.alive        = True       # flag toggled when age reaches max_age

    # PRIVATE MOVEMENT HELPERS
    # _sorted_neighbours()  → list of free neighbour cells,
    #                         sorted nearest-first to a target.
    # move_towards()        → pick the nearest free neighbour
    # random_move()         → wander randomly until a free cell is found
    def _sorted_neighbours(self, tgt, frame, genes):
        r0, c0 = self.pos
        nbrs = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                cand = (r0 + dr, c0 + dc)
                # inside frame bounds and not an obstacle?
                if (0 <= cand[0] < frame[0] and
                    0 <= cand[1] < frame[1] and
                    cand not in genes):
                    nbrs.append(cand)
        # sort by Euclidean-squared distance to the target cell
        nbrs.sort(key=lambda p: (p[0]-tgt[0])**2 + (p[1]-tgt[1])**2)
        return nbrs

    def move_towards(self, tgt, genes, frame):
        nbrs = self._sorted_neighbours(tgt, frame, genes)
        if nbrs:              # take the closest legal step
            self.pos = nbrs[0]
        else:                  # no legal neighbour → random fallback
            self.random_move(genes, frame)   # never freeze

    def random_move(self, genes, frame):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1),      # 4 orthogonal
                (1, 1), (1, -1), (-1, 1), (-1, -1)]     # 4 diagonal
        random.shuffle(dirs)
        for dr, dc in dirs:
            nxt = (self.pos[0] + dr, self.pos[1] + dc)
            if (0 <= nxt[0] < frame[0] and
                0 <= nxt[1] < frame[1] and
                nxt not in genes):
                self.pos = nxt
                break

    # MAIN PER-TICK STATE MACHINE
    # ▸ step_change() is called once per simulation timestep.
    #   It drives: ageing, movement, nectar collection & deposit.
    # ------------------------------------------------------------------
    # Arguments
    #   hexslot : list[Comb]    – honeycomb cells inside the hive
    #   stacies : list[Flower]  – flower objects in the world
    #   genes   : set[(r,c)]    – obstacle coordinates
    #   frame   : (rows, cols)  – world grid size for bounds checking
    # age killer (time)
    def step_change(self, hexslot, stacies, genes, frame):
        if not self.alive:
            return   # dead bees do nothing

        # 0️⃣  Rest delay: small cooldown after loading or waiting
        if self.resttime:
            self.resttime -= 1
            return

        # 1️⃣  Leaving the hive (only if empty & not depositing)
        if self.inhoneyhold and not self.hasmuj and not self.depositing:
            if self.pos != self.honeyholdexit:
                # still inside hive → walk to exit porta
                self.move_towards(self.honeyholdexit, set(), (20, 15))
            else:
                # step THROUGH portal to the world grid
                self.inhoneyhold = False
                self.pos         = self.humanityentrance
            self.timeisclicking()
            return

        # 2️⃣  Hunting for nectar in the world
        if not self.inhoneyhold and not self.hasmuj:
            # gather flowers within detection_range
            nearbyinrange = [f for f in stacies
                      if f.muj > 0 and
                         abs(f.pos[0]-self.pos[0]) + abs(f.pos[1]-self.pos[1])
                         <= self.aimrange]
            if nearbyinrange:
                # choose closest flower (distance²)
                tgt = min(nearbyinrange,
                          key=lambda f: (f.pos[0] - self.pos[0]) ** 2 +
                                        (f.pos[1] - self.pos[1]) ** 2)

                if self.pos != tgt.pos:
                    self.move_towards(tgt.pos, genes, frame)
                else:
                    # arrived → attempt to collect one nectar unit
                    if tgt.collect_nectar():
                        self.hasmuj    = True   # now carrying
                        self.resttime = 2      # loading delay
            else:
                self.random_move(genes, frame)
            self.timeisclicking()
            return

        # 3️⃣  Returning to the hive entrance (while carrying nectar)
        if self.hasmuj and not self.inhoneyhold:
            if self.pos != self.humanityentrance:
                self.move_towards(self.humanityentrance, genes, frame)
            else:
                # transition back into hive grid
                self.inhoneyhold = True
                self.depositing  = True
                self.pos         = self.honeyholdentrance
            self.timeisclicking()
            return

        # 4️⃣  Depositing nectar into the nearest non-full comb
        if self.depositing:
            # list of (comb, manhattan-distance) pairs for non-full combs
            targets = [(c, abs(c.posrawhoney[0] - self.pos[0]) +
                           abs(c.posrawhoney[1] - self.pos[1]))
                       for c in hexslot if not c.fullrawhoneyy]
            if targets:
                hexslot, _ = min(targets, key=lambda t: t[1])
                if self.pos != hexslot.posrawhoney:
                    self.move_towards(hexslot.posrawhoney, set(), (20, 15))
                else:
                    hexslot.addrawhoney()  # deposit 1 unit
                    self.hasmuj    = False
                    self.depositing = False
            else:
                # all combs full → wait a bit before rechecking
                self.resttime = 3
            self.timeisclicking()
            return

        # 5️⃣  Idle ageing when in hive and not carrying
        self.timeisclicking()

    # AGEING HELPER
    # Adds one tick to age; kills the bee if age exceeds max_age.
    def timeisclicking(self):
        self.age += 1
        if self.age >= self.max_age:
            self.alive = False          # bee dies of old age









