import pandas as pd
import pytest

from fish_bowl.dataio.persistence import SimulationClient, Simulation
from fish_bowl.process.utils import ImpossibleAction, Animal
from fish_bowl.process.topology import SquareGridCoordinate, NonEmptyCoordinate, TopologyError, square_grid_neighbours

sim_config = {
    'grid_size': 10,
    'init_nb_fish': 50,
    'fish_breed_maturity': 3,
    'fish_breed_probability': 80,
    'fish_speed': 2,
    'init_nb_shark': 5,
    'shark_breed_maturity': 5,
    'shark_breed_probability': 100,
    'shark_speed': 4,
    'shark_starving': 4}

animal_list = [
    (Animal.Fish, SquareGridCoordinate(x=1, y=3)),
    (Animal.Fish, SquareGridCoordinate(x=2, y=1)),
    (Animal.Fish, SquareGridCoordinate(x=3, y=2)),
    (Animal.Fish, SquareGridCoordinate(x=4, y=3)),
    (Animal.Fish, SquareGridCoordinate(x=5, y=4)),
    (Animal.Shark, SquareGridCoordinate(x=6, y=5)),
    (Animal.Shark, SquareGridCoordinate(x=6, y=6)),
    (Animal.Fish, SquareGridCoordinate(x=6, y=1)),
]


class TestPersistence:

    def test_database_init(self):
        client = SimulationClient('sqlite:///:memory:')
        # init DB
        sid = client.init_simulation(**sim_config)
        assert len(client.get_all_simulations()) == 1, 'Should be only one simulation'
        assert isinstance(client.get_simulation(sid), Simulation)

        # check exception raised in init when adding animal on non-existent sim
        with pytest.raises(ValueError):
            client.init_animal(sim_id=10, current_turn=0, animal_type=Animal.Fish,
                               coordinate=SquareGridCoordinate(x=0, y=1))
        # init some animals
        client.init_animal(sim_id=sid, current_turn=0, animal_type=Animal.Fish,
                           coordinate=SquareGridCoordinate(x=0, y=1))
        assert client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(x=0, y=1))

        # check exception for adding animal to an already occupied square
        with pytest.raises(NonEmptyCoordinate):
            client.init_animal(sim_id=sid, current_turn=0, animal_type=Animal.Fish,
                               coordinate=SquareGridCoordinate(x=0, y=1))
        # but should be fine in a new simulation
        sid_2 = client.init_simulation(**sim_config)
        client.init_animal(sim_id=sid_2, current_turn=0, animal_type=Animal.Fish,
                           coordinate=SquareGridCoordinate(x=0, y=1))

        # spawn outside the grid
        with pytest.raises(TopologyError):
            client.init_animal(sim_id=sid_2, current_turn=0, animal_type=Animal.Fish,
                               coordinate=SquareGridCoordinate(x=10, y=1))

    def test_animal_functions(self):
        client = SimulationClient('sqlite:///:memory:')
        # init DB
        sid = client.init_simulation(**sim_config)
        # add a bunch of animals
        for t, c in animal_list:
            client.init_animal(sim_id=sid, current_turn=0, animal_type=t, coordinate=c)
        # retrieve animals
        animals_df = client.get_animals_df(sim_id=1)
        assert isinstance(animals_df, pd.DataFrame), 'results is a DataFrame'
        assert len(animals_df) == 8, 'should be only 9 animals'
        # update animals
        # create update dict
        update_dict = {oid: {'breed_count': 1, 'last_breed': 5, 'last_fed': 4} for oid in animals_df.oid.values}
        client.update_animals(sim_id=sid, update_dict=update_dict)
        animals_df = client.get_animals_df(sim_id=1)
        assert animals_df.breed_count.unique()[0] == 1, 'Breed count should be one now'
        client.update_animals(sim_id=sid, update_dict={1: {'alive': False}})
        # this update should not work
        animal = client.get_animal(sim_id=sid, animal_id=1)
        assert animal.alive, 'Animal should still be alive'
        # but this should work
        client.kill_animal(sim_id=sid, animal_ids=[1, 2, 3])
        animal = client.get_animal(sim_id=sid, animal_id=1)
        assert not animal.alive, 'This time alive was updates'
        # a dead animal does not occupy a square
        assert not client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(1, 3))
        # test get animal by types
        shark_df = client.get_animals_by_type(sim_id=sid, animal_type=Animal.Shark)
        assert shark_df.animal_type.unique()[0] == Animal.Shark

    def test_position_functions(self):
        client = SimulationClient('sqlite:///:memory:')
        # init DB
        sid = client.init_simulation(**sim_config)
        # add a bunch of animals
        for t, c in animal_list:
            client.init_animal(sim_id=sid, current_turn=0, animal_type=t, coordinate=c)
        # check animal in square
        coord = SquareGridCoordinate(x=1, y=3)
        animals_in_square = client.get_animal_in_position(sim_id=sid, coordinate=coord)
        assert len(animals_in_square) == 1
        # kill that animal
        client.kill_animal(sim_id=sid, animal_ids=[animals_in_square[0].oid])
        animals_in_square = client.get_animal_in_position(sim_id=sid, coordinate=coord)
        assert len(animals_in_square) == 0
        # adding a live one in coord
        client.init_animal(sim_id=sid, current_turn=0, animal_type=Animal.Fish, coordinate=coord)
        animals_in_square = client.get_animal_in_position(sim_id=sid, coordinate=coord, live_only=False)
        assert len(animals_in_square) == 2


    def test_moving_animals(self):
        client = SimulationClient('sqlite:///:memory:')
        # init DB
        sid = client.init_simulation(**sim_config)
        # add a bunch of animals
        for v in animal_list:
            client.init_animal(sim_id=sid, current_turn=0, animal_type=v[0], coordinate=v[1])
        # test move
        assert not client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(5, 3))
        client.move_animal(sim_id=sid, animal_id=4, new_position=SquareGridCoordinate(5, 3))
        assert client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(5, 3))
        # trying to move dead animal
        client.kill_animal(sim_id=sid, animal_ids=[3])
        with pytest.raises(ImpossibleAction):
            client.move_animal(sim_id=sid, animal_id=3, new_position=SquareGridCoordinate(3, 3))
        # trying to move to an already occupied square
        with pytest.raises(NonEmptyCoordinate):
            client.move_animal(sim_id=sid, animal_id=5, new_position=SquareGridCoordinate(5, 3))
        # but moving to a square occupied by a dead animal is possible
        assert not client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(3, 2))
        client.move_animal(sim_id=sid, animal_id=1, new_position=SquareGridCoordinate(3, 2))
        assert client.coordinate_is_occupied(sim_id=sid, coordinate=SquareGridCoordinate(3, 2))

    def test_animal_function(self):
        client = SimulationClient('sqlite:///:memory:')
        # init DB
        sid = client.init_simulation(**sim_config)
        # add a bunch of animals
        a_list = [
            (Animal.Fish, SquareGridCoordinate(x=1, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=2, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=3, y=1)),
            (Animal.Fish, SquareGridCoordinate(x=1, y=3)),
            (Animal.Fish, SquareGridCoordinate(x=3, y=2))
        ]
        for t, c in a_list:
            client.init_animal(sim_id=sid, current_turn=0, animal_type=t, coordinate=c)
        coord_list = client.has_fish_in_square(sim_id=sid, coordinates=[SquareGridCoordinate(1, 1)])
        assert len(coord_list) == 1, 'There should be a single fish'
        coord_list = client.has_fish_in_square(sim_id=sid, coordinates=[SquareGridCoordinate(1, 2)])
        assert len(coord_list) == 0, 'There should be no fish here'
        neigh = square_grid_neighbours(grid_size=10, coordinate=SquareGridCoordinate(2, 2))
        coord_list = client.has_fish_in_square(sim_id=sid, coordinates=neigh)
        assert len(coord_list) == 5, 'There should be 5 fishes here'

        # eating animals
        eaten = client.eat_animal_in_square(sim_id=sid, coordinate=SquareGridCoordinate(1, 1))
        assert eaten, 'Fish in 1, 1 should have been eaten'
        # can't eat dead Fish
        eaten = client.eat_animal_in_square(sim_id=sid, coordinate=SquareGridCoordinate(1, 1))
        assert not eaten, 'Should not be able to eat a dead Fish'
        client.init_animal(sim_id=sid, current_turn=0, animal_type=Animal.Shark, coordinate=SquareGridCoordinate(5, 5))
        eaten = client.eat_animal_in_square(sim_id=sid, coordinate=SquareGridCoordinate(5, 5))
        assert not eaten, 'Should not be able to eat a Shark'
