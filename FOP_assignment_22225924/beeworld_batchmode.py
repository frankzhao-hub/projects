# batch mode
import argparse, csv, random, numpy as np
from worker  import Worker
from flowers import Flower
from comb    import Comb

# argparse- let the script reader -f, -p, --csv from the command line.
# csv - to read the parameter file.
# supplies pseudorandom numbers (for spawning flowers).
# numpy (np) – fast array handling; loads the terrain CSV and stores the log.


# reads key value pairs from a small csv into a dictionary so we can say steps
# steps = int(prm["steps"]) later.
def load_params(path):
    out = {}
    with open(path, newline="") as f:  # open the file at the specified path
        for k, v in csv.reader(f):  # read each row from the csv file as key value pairs
            out[k.strip()] = v.strip() # remove whitespace from keys and values, then store in dictionary
    return out  # return the populated dictionary containing parameters

#Returns a random (row, col) tuple inside an r × c grid—used for placing flowers.
def rand_cell(r, c):
    return random.randrange(r), random.randrange(c)

# -f / --field → file with the terrain matrix (house, pool, etc.)
# -p / --params → file with simulation parameters (steps, bee count, …)
# --csv → optional file where stats will be saved
def main():
    # create argument parser to handle command line arguments
    ap = argparse.ArgumentParser(description="Bee-World batch mode")

    # Define a required argument "-f" or "--field" for specifying terrain CSV file path
    ap.add_argument("-f", "--field",  required=True, help="terrain CSV")

    #  # Define a required argument "-p" or "--params" for specifying parameter CSV file path
    ap.add_argument("-p", "--params", required=True, help="parameter CSV")

    # Define an optional argument "--csv" for specifying an output CSV file for statistics
    ap.add_argument("--csv", help="optional stats CSV")

    # Parse the provided arguments from the command-line and store them in 'args'
    args = ap.parse_args()

# np.loadtxt() function from numpy to read data from csv file.
#loaded data is stored as an array
    humanity   = np.loadtxt(args.field, delimiter=",")
    rows, cols = humanity.shape # world boundary
    prm        = load_params(args.params)


#.get(key, default) means the simulation still runs if the CSV
#omits a field (it falls back to the default in the second argument).
    steps   = int(prm.get("steps",            200))
    n_bees  = int(prm.get("num_bees",         10))
    n_flwr  = int(prm.get("num_flower",       30))
    n_wasps = int(prm.get("num_wasp",          1))
    grow_p  = float(prm.get("spawn_flower_p",  0.02))

    beeholdspawn  = (10, 7)    # start cell in the hive
    beeholdexit   = (0, 7)     # hive> world portal
    beeholdentrance    = (19, 7)   # world > hive portal
    humanityentrance   = (rows - 1, cols // 2)   # matching cell on world grid

    genes = {(r, c) for r in range(rows)
                     for c in range(cols)
                     if humanity[r, c] in (0, 3, 15)}  # <-- grass (10) is walkable
    # collets the coordinates of blocked tiles
    # grass cells = 10 they are walkable so excluded.

#Creates IDs B1 … Bn, all starting at (10,7) inside the hive and given the four portal coordinates.
    bees = [] #
    for i in range(1, n_bees + 1):
        bees.append(Worker("B" + str(i), beeholdspawn,
                           beeholdexit, beeholdentrance, humanityentrance))

# A while loop keeps picking random cells until it has the requested n_flwr flowers, rejecting any cell in genes.
    flowers = []
    while len(flowers) < n_flwr:
        pos = rand_cell(rows, cols)
        if pos not in genes:  # obstacle check
            name = "F" + str(len(flowers) + 1)  # build the ID without f-string
            flowers.append(Flower(name, pos))

#Three comb objects are created at fixed hive positions and
# immediately .build()-ed (they start empty but ready to receive honey).
    combs = [Comb("C1", (7, 7)),
             Comb("C2", (7, 9)),
             Comb("C3", (9, 7))]
    for c in combs:
        c.build()

    nectar_log, alive_log = [], []
    total_nectar = 0

    for step in range(steps):
        if random.random() < grow_p: # Random flower spawn – with probability grow_p (2 % by default)
            pos = rand_cell(rows, cols) # a new flower is added in a random free cell.
            if pos not in genes:
                flower_id = "F" + str(len(flowers) + 1)  # build name without f-string
                flowers.append(Flower(flower_id, pos))


        for b in bees:
            had_muj = b.hasmuj
            b.step_change(combs, flowers, genes, (rows, cols)) # each bee moves
            if had_muj and not b.hasmuj:
                total_nectar += 1 #If a bee unloaded nectar this turn (had_muj→not b.hasmuj) we increment total_nectar.

#Logs – append the cumulative nectar count and the number of bees still alive to two lists (nectar_log, alive_log).
        nectar_log.append(total_nectar)
        alive_log.append(sum(b.alive for b in bees))

    # print
    print("Batch finished –", steps,
          "steps; nectar collected:", total_nectar,
          "; bees alive:", alive_log[-1])

    if args.csv:    # ← Only run this block if the user gave a --csv filename
    # Build a 2-D array with three columns:
    #   column-0: step number   (0..steps-1)
    #   column-1: nectar count  (how many bees carried nectar that step)
    #   column-2: alive count   (how many bees are still alive)

        out = np.column_stack((range(steps), nectar_log, alive_log)) # step counter, nectar history, alive bee history

    # Write that array to disk in plain-text CSV format:
    #   • fmt="%d,%d,%d"        → 3 integers separated by commas
    #   • header="..."          → first line = column labels
    #   • comments=""           → don’t prepend the header with a '#'
        np.savetxt(args.csv, out, fmt="%d,%d,%d",
                   header="step,nectar,bees_alive", comments="")
        print("Stats saved to", args.csv)  # tell the user where the file went

if __name__ == "__main__": # ← True only when executed, not imported
    main()                 # ← kick off the whole program

# Standard “module guard” in Python:
# • When this file is run directly (   python beeworld_batchmode.py   )
#   the special variable __name__ is set to "__main__",
#   so main() gets called and the whole simulation starts.
#
# • When this file is *imported* from some other script
#   (   import beeworld_batchmode   )
#   __name__ is set to the module’s name ("beeworld_batchmode"),
#   the condition is False, and main() is **NOT** executed.
#
#   That prevents the batch-mode run from auto-starting during unit tests
#   or when the code is reused as a library.












