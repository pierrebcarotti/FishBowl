# Fish Bowl
A predator-prey simulator that aims to simulate very simple ecosystem.

## Setup
Use the attached simul-dev.txt file to create a conda environment for the simulation.
To run a demo simulation, use the simple_simulation.py in fish_bowl/scripts.

## Create a simulation config
New simulation configuration files can be added in fish_bowl/configuration folder. They must be '.json' files  with the below element specified:

{
  "grid_size": 20,
  "init_nb_fish": 150,
  "fish_breed_maturity": 2,
  "fish_breed_probability": 0.8,
  "fish_speed": 2,
  "init_nb_shark": 5,
  "shark_breed_maturity": 5,
  "shark_breed_probability": 0.8,
  "shark_speed": 4,
  "shark_starving": 4
}
### grid_size:
grids are squares with grid_size cell per side.
### init_nb_fish / sharks:
Specify the initial population for both fish and sharks
### fish/shark_breed_maturity:
Set number of turn from which fish/sharks can reproduce after they have spawn. From that moment, they can breed at any turn.
### fish/sharks_breed_probability:
If a shark or fish as the maturity to reproduce, then it can do so at each turn with this probability.
### fish/shark_speed:
How many cells a fish/shark can move at each turn (Not Implemented)
### shark_starving:
Number of turn a shark can live without feeding. Shark dies if they are not fed after this number of turns.
Note, fish do not starve.

## Simulation rules:
- Only a single living animal is allowed per cell at each turn
- Shark can eat any fish adjacent to its cell. Shark move into the eaten fish cell.
- Shark dies of starvation at the beginning of the turn {shark_starving} turns after they last dinner.
- In order to breed, shark/fish need to have a free space around them. When breeding, parent move to the free cell and child spawn into original cell
 