import numpy as np

class Wasp:
    """
      Predator that hunts worker-bees in the world grid.

      Parameters:
      ##########
      ID            : str            unique label (e.g. "wasp")
      pos           : (row, col)     starting coordinate in the world
      manualsigma   : bool           • True  → player drives the wasp
                                     • False → autonomous A.I. mode
      """

    # Constructor – set identity, position, control mode, life-flag
    def __init__(self, ID, pos, manualsigma=False):
        self.ID          = ID  # printable name
        self.pos         = pos   # current (row, col) location
        self.manualsigma = manualsigma     # if True, on-key handler moves it
        self.alive       = True       # could be extended for combat later

    # _step_ai()
    # Internal helper: one “thinking” step for autonomous mode.
    # 1. Find the nearest *alive, outdoor* bee.
    # 2. Move one cell closer (Manhattan step) if that cell is
    #    inside the grid AND not an obstacle (genes set).

    def _step_ai(self, swarm, size, genes):
        # choose nearest bee
        tgt = None
        best = 10 ** 9   # large sentinel distance
        for bee in swarm:
            d = abs(bee.pos[0]-self.pos[0]) + abs(bee.pos[1]-self.pos[1])
            if d < best:
                best = d
                tgt = bee
        if tgt is None:     # no outdoor bees → stay put
            return

        dx = np.sign(tgt.pos[0] - self.pos[0])
        dy = np.sign(tgt.pos[1] - self.pos[1])

        nxt = (self.pos[0] + dx, self.pos[1] + dy)
        if (0 <= nxt[0] < size[0] and 0 <= nxt[1] < size[1] and
            nxt not in genes):
            self.pos = nxt     # commit the move

    # eliminate_bees()
    # Sting (kill) every bee within a Manhattan radius.
    # Quickly turns nearby Worker.alive to False.
    def eliminate_bees(self, swarm, radius=2):
        for bee in swarm:
            if (abs(bee.pos[0]-self.pos[0]) <= radius and
                abs(bee.pos[1]-self.pos[1]) <= radius):
                bee.alive = False

    # step_change()
    # Called once per simulation tick.
    # • Does nothing if wasp is dead or under manual control.
    # • Otherwise stings, moves via _step_ai, then stings again.
    #   (Two stings so a bee that moves INTO radius this tick
    #    still gets caught.)
    # -----------------------------------------------------------------
    # Parameters
    # ----------
    # beetlejuices : list[Worker]   all worker bees in the world
    # size         : (rows, cols)  grid dimensions
    # genes        : set[(r,c)]    obstacle coordinates

    def step_change(self, beetlejuices, size, genes):
        if not self.alive or self.manualsigma:
            return     # manual mode → external key handler

        # build list of targetable bees (alive and outside the hive)
        swarm = []
        for b in beetlejuices:
            if b.alive and not b.inhoneyhold:
                swarm.append(b)

        # sting → move → sting pattern
        self.eliminate_bees(swarm, radius=2)
        self._step_ai(swarm, size, genes)
        self.eliminate_bees(swarm, radius=2)



















