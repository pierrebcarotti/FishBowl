from fish_bowl.dataio.persistence import SimulationClient, get_database_string
from fish_bowl.process.topology import SquareGridCoordinate
from fish_bowl.process.simple_display import display_simple_grid


client = SimulationClient(get_database_string())
print(display_simple_grid(client.get_animals_df(sim_id=1), 10))
coord_1 = SquareGridCoordinate(6, 8)
coord_2 = SquareGridCoordinate(7, 9)
print(client.get_animal_in_position(sim_id=1, coordinate=coord_1, live_only=False))
print(client.get_animal_in_position(sim_id=1, coordinate=coord_2, live_only=False))
