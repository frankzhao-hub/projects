import numpy as np
import matplotlib.pyplot as plt
import random
from worker import Worker
from flowers import Flower
from comb import Comb
from wasp import Wasp
from Queenbee import QueenBee
from plot import plot_hive, plot_world

#
# 1. reads user inputs like timesteps, bee count, season)
#
dihslen = None                    # number of simulation steps

while dihslen is None or not (50 <= dihslen <= 500):
    try:                                        # try to pass on integer
        dihslen = int(input("Timesteps: "))     # must be 50-500
    except ValueError:                           # if input isnt an integer
        dihslen = None                          # force another iteration

    if dihslen is None or not (50 <= dihslen <= 500):
        print("Error: Enter an integer between 50 and 500.")

numbeetlejuice = None  # number of worker bees
while numbeetlejuice is None or not (1 <= numbeetlejuice <= 20):
    try:
        numbeetlejuice = int(input("Number of worker bees: "))  # must be 1-20
    except ValueError:
        numbeetlejuice = None  # reset if conversion failed

    if numbeetlejuice is None or not (1 <= numbeetlejuice <= 20):
        print("Error: Enter an integer between 1 and 20.")


era = ""                                    # season
while era not in ("summer", "winter"):
    era = input("Season (summer / winter): ")
    if era not in ("summer", "winter"):
        print("Error: Type 'summer' or 'winter'.")

firststacy = 40 if era == "summer" else 20   # initial flower count
stacyborn  = 0.07 if era == "summer" else 0.02   # spawn probability

#
# 2. world / hive grids and static obstacles
#

firstadams   = 20       # starting tree count

world_rows, world_cols = 40, 30           # world grid
hive_rows,  hive_cols  = 20, 15           # hive grid


# hive coordinates in the world graph
scarletcell = (15, 20)          # portal link grids, hive in graph 2 to 1


honeyhold  = np.full((hive_rows, hive_cols), 5)    # hive matrix
humanity = np.full((world_rows, world_cols), 10)    # world matrix

TREE, HOUSE, WATER = 3, 15, 0       # colour
random.seed()
#random.seed() (empty parentheses) tells Python to pull a seed from the
#operating-system’s entropy pool (current time, hardware noise, etc.). That means each time you launch your
#program, the starting seed is different → you get a fresh, unpredictable layout of trees, flowers, wasp starting positions, and so on.
#why random.seed()? because randomness is Generated by a deterministic algorithm long mathematical formula running inside the CPU.
# you will never get true "randomness" through the system without implementing a different seed each run to achieve the " randomness" which is psuedorandomness
# the user wants


# fixed house & pool
humanity[3:9, 25:32] = HOUSE        # filled out shapes of house
humanity[15:20, 3:8]   = WATER       # filled out shapes of water

# collect obstacle coordinates
genes = set()                              # empty set to collect coordinates
for r in range(world_rows):                    # loop every row
    for c in range(world_cols):                # loop every column
        cell_value = humanity[r, c]               # value at this grid location
        if cell_value == HOUSE or cell_value == WATER:
            genes.add((r, c))

humanityentrance = scarletcell  # keep existing logic name
honeyholdexit      = (0, 7)           # exit coordinate soo the bees can exit graph 1
honeyholdentrance  = (19, 7)           # entrance coordinates so the bees can enter graph 1

scarletpatch = set()
for r in range(19, 22):          # rows 19–21
    for c in range(14, 17):      # cols 14–16
        scarletpatch.add((r, c))          # this is the red coloured hive filled out in graph 2

#  protected spots
#thegifted = set([honeyholdexit, honeyholdentrance, humanityentrance]) not needed

#
# 3. random trees generated ( cannot overlap obstacles or red hive patch)
#

adams = []
while len(adams) < firstadams:
    row = random.randint(0, world_rows - 1)
    col = random.randint(0, world_cols - 1)
    pos = (row, col)
    # add the tree only if the spot is free

    if pos not in adams and pos not in genes and pos not in scarletpatch:
        adams.append(pos)
        humanity[row, col] = TREE
        genes.add(pos)

#
# 4. combs cells ( 3 fixed positions inside hive)
#

honeyhold[honeyholdexit]      = 2          # mark portoals
honeyhold[honeyholdentrance]  = 2

hexslotspos = [(7, 7), (7, 9), (9, 7)]
hexslot = []
psl = 1                      # start counting at 1
for pos in hexslotspos:     # loop directly over the positions
    name = "comb" + str(psl) # build the name without f-strings
    hexslot.append(Comb(name, pos))
    psl += 1
for comb in hexslot:
    comb.build()              # at the start the combs are built already

#
# 5. flowers (ordinary / golden) - spawn in free cells only
#
stacies = []
# the loops keeps running until the list length equals the target intial trees
while len(stacies) < firststacy:
    row = random.randint(0, world_rows - 1)
    col = random.randint(0, world_cols - 1)
    pos = (row, col)

    # assume the spot is OK, then disprove it if necessary
    valid = (row, col) != scarletcell and (row, col) not in genes
    #
    for fl in stacies:   # every flower already pllaced
        if fl.pos == pos:   # position clash
            valid = False    # disqualify this cell

    if valid:                                 # only add when the spot is free
        name = "flower" + str(len(stacies) + 1)
        is_golden = random.random() < 0.15    # 15 % chance of golden
        stacies.append(Flower(name, pos, golden=is_golden))

#
# all creatures ( queen, bees, wasp)
#
#The QueenBee just keeps time and makes workers: every 30 game-ticks she adds
#a new worker bee at her spot, and after about 500-700 ticks she dies and stops.
honeyholderspawn = (10, 7)
eve   = QueenBee("queen",
                 honeyholderspawn,
                 honeyholdexit,
                 honeyholdentrance,
                 humanityentrance)

beetlejuices = []               # list that will hold worker objects
for i in range(numbeetlejuice):    #create exactly 'numbeetlejuice'  bees
    name = "w" + str(i + 1)         # w1,w2,w3....
    beetlejuices.append(Worker(name,      # unique worker ID
                               honeyholderspawn,   # all workers start at (10,7)
                               honeyholdexit,       # exit portal
                               honeyholdentrance,     # entry portal
                               humanityentrance))    # world-side coordinate

# manualsigma=True tells the Wasp class that its sting radius (σ)
goati   = Wasp("wasp", (10, 10), manualsigma=True)  # will be set interactively by the
goatis  = [goati]                                           #keyboard handler instead of default behaviour.
# small list so plot_world() can iterate

#
# 7. live plot set-up ( hive world stats)
#

nectar_log = []
beetlejuicehistory   = []
fig, axes = plt.subplots(1, 3, figsize=(21, 7), gridspec_kw=dict(width_ratios=(1, 2, 1)))
# gridSpec= a blueprint that divides the figure into a grid of rectangular cells, each cell host one axes
#width ratio = tells gridspec how to apportion the available width among three columns relative to ach other
# 1,2,1 = 1 part for column 0, 2 parts for column 1 and 1 part to column 2
# centre graph gets 50% of the width and the other 2 gets 25% each.
plt.ion()
nectar_log = []
beetlejuice_log = []
ascended = False        # set true when combs filled

#
# 8. arrow-key handler for wasp movement and sting
#

# Matplotlib calls this function each time a key is pressed while
# the figure window has focus.  `event.key` contains the literal
# key name the user hit (e.g., "up", "left", "a", "space", …).
def on_key(event):
    move_map = {'up': (1, 0),
                'down': (-1, 0),
                'left': (0, -1),
                'right': (0, 1)}

    # only react when the key pressed is one of the four arrows
    if event.key in move_map:    # event .key> Arrow keys → 'up', 'down', 'left', 'right'
        dr, dc = move_map[event.key] # unpack movement delta

        # target coordinate (row, col)
        new_r = goati.pos[0] + dr
        new_c = goati.pos[1] + dc


        # ── Boundary check: keep the wasp inside the world grid ──
        # • 0 ≤ new_r < world_rows   ensures row is in range
        # • 0 ≤ new_c < world_cols   ensures col is in range
        if (0 <= new_r < world_rows and
            0 <= new_c < world_cols):
            # ── Obstacle check: avoid trees, house, pool, etc. ──
            # `genes` is a pre-computed set of all obstacle cells.
            if (new_r, new_c) not in genes:     # stay on grid annd avoid obstacles
                goati.pos = (new_r, new_c)     # updating the move

        # ── Build a list of potential victims ─────────────────
        # • must be alive
        # • must currently be *outside* the hive (`not b.inhoneyhold`)
        swarm = [b for b in beetlejuices
                 if b.alive and not b.inhoneyhold]
        # ── Sting any worker within radius 0.5 cells ──────────
        # `eliminate_bees` sets each bee’s .alive flag to False
        # if their distance to `goati.pos` ≤ radius.
        goati.eliminate_bees(swarm, radius=0.5)    # sting any bees in radius 0.5

        # ── Trigger an immediate redraw so the figure shows the
        #    wasp’s new position (and possibly fewer bees).
        plt.draw()

# Matplotlib event-hook: connect the above function to *every*
# key-press event in the figure’s GUI window.
fig.canvas.mpl_connect('key_press_event', on_key)

#
# 9. main simulation loop
#

for t in range(dihslen):
    # queen lays an egg / changes combs
    eve.step_change(hexslot, beetlejuices, genes)   # queen lay eggs / changes combs

    # each worker acts ( move,collect nectar,deposit,etc)
    for bee in beetlejuices[:]:
        bee.step_change(hexslot, stacies, genes, (world_rows, world_cols))

        all_full = True

        # check each comb
        for comb in hexslot:
            if not comb.fullrawhoneyy:     # once a comb isnt full
                all_full = False           # flag mission incomplete

        # if every comb was full, end the simulation
        if all_full:
            print("HOORAYYY Mission complete! All combs are full of honey.")
            ascended = True
            # keep only flowers that still have nectar
    full_count = 0
    total_combs = len(hexslot)
    for comb in hexslot:
        if comb.fullrawhoneyy:
            full_count += 1

    if full_count == total_combs:
        print("HOORAYYY Mission complete! All combs are full of honey.")
        ascended = True
        break      # breaks everything including the for loop above and then proceed to the next thing

    remaining_flowers = []
    for fl in stacies:
        if fl.muj > 0:  # skip empty flowers
            remaining_flowers.append(fl)
    stacies = remaining_flowers  # update the original list


    if random.random() < stacyborn:
        rr = random.randint(0, world_rows - 1)
        cc = random.randint(0, world_cols - 1)
        # only add a flower if the spot is free and not on the hive cell
        duplicate = False
        for fl in stacies:  # scan existing flowers
            if fl.pos == (rr, cc):
                duplicate = True  # same position found


        if not duplicate and (rr, cc) != scarletcell and (rr, cc) not in genes:
            name = "flower" + str(len(stacies) + 1)  # build the name
            is_golden = random.random() < 0.15  # 15 % chance
            stacies.append(Flower(name, (rr, cc), golden=is_golden))

    nectar_log.append(sum(b.hasmuj for b in beetlejuices))
    beetlejuicehistory.append(sum(b.alive for b in beetlejuices))
    for ax in axes:
        ax.clear()
    plot_hive(honeyhold, beetlejuices, hexslot, axes[0], eve)
    axes[0].set_title("Hive")
    plot_world(humanity, beetlejuices, stacies, goatis, axes[1], humanityentrance)
    axes[1].set_xlim(-0.5, world_cols-0.5)
    axes[1].set_ylim(-0.5, world_rows-0.5)
    axes[1].set_title("World")
    axes[2].plot(nectar_log, label='Nectar')
    axes[2].plot(beetlejuicehistory, label='Bees')
    axes[2].legend()
    axes[2].set_title("Stats")
    fig.suptitle("Time Step: " +str(t+1))
    plt.pause(0.1)

plt.ioff()
# interactive off stop redrawing the figure
if ascended:
    print("Simulation ended early, bees filled every comb!!!!!")
else:
    print("Simulation complete.")






