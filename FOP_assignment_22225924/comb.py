class Comb:
    # a single storage cell inside the hive

    def __init__(self, ID, pos):
        self.ID            = ID # unique label
        self.posrawhoney   = pos # (row,col)  tuple inside the hive grid
        self.built         = False  #starts as an empty frame
        self.rawhoneylvl   = 0 # how many loads of nectar stored
        self.maxrawhoneyy  = 5   #capacity: 5 loads fills the comb
        self.fullrawhoneyy = False # flag becomes True when level==capacity

    # called once by the simulation to mark the wax cell built
    def build(self):
        self.built = True  # comb can now accept nectar

    # Worker bee deposits one load of raw honey (nectar)
    # Only allowed if comb is built and not yet full.
    def addrawhoney(self):
        if self.built and not self.fullrawhoneyy:
            self.rawhoneylvl += 1  # increment level
            if self.rawhoneylvl >= self.maxrawhoneyy:
                self.fullrawhoneyy = True   # comb now is full

    # Return an RGB colour for plotting:
    # • Starts pale (#FFF8E6) when empty/unbuilt.
    # • Gets darker & more orange as honey level rises.
    #   ratio = 0   → light ; ratio = 1 → dark amber.
    def hexslotcolour(self):
        if not self.built:
            return '#FFF8E6'     #  unbuilt frame colour
        ratio = self.rawhoneylvl / self.maxrawhoneyy
        r = 1.0            # keep red channel full
        g = 0.8 - 0.4 * ratio  # fade green as it fills
        b = 0.5 - 0.2 * ratio  # fade blue as it fills
        return (r, g, b)   # matplotlib accepts RGB tuple









