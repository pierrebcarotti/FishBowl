import datetime as dt
import logging
import os
from typing import List, Dict, Optional

import pandas as pd

from fish_bowl.dataio.database import SQLAlchemyQueries
from sqlalchemy import Column, DateTime, Float, ForeignKey, Enum, Boolean, Integer
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from fish_bowl.process.utils import ImpossibleAction, Animal
from fish_bowl.process.topology import SquareGridCoordinate, square_grid_valid, NonEmptyCoordinate

_logger = logging.getLogger(__name__)

DB_LOC = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'simuldb_{}.db'))

Base = declarative_base()
schema = 'main'  # in sqlite, schema is always main, in other db, look for the owner schema name


def get_database_string(ref: Optional[str] = '', memory: Optional[bool] = False):
    if memory:
        return 'sqlite://'
    else:
        return r'sqlite:///{}'.format(DB_LOC.format(ref))


class Simulation(Base):
    __tablename__ = 'SIMULATIONS'
    sid = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    grid_size = Column(Integer)
    init_nb_fish = Column(Integer)
    fish_breed_maturity = Column(Integer)
    fish_breed_probability = Column(Integer)
    fish_speed = Column(Integer)
    init_nb_shark = Column(Integer)
    shark_breed_maturity = Column(Integer)
    shark_breed_probability = Column(Integer)
    shark_speed = Column(Integer)
    shark_starving = Column(Integer)

    __table_args__ = ({'schema': schema})

    @validates('shark_breed_probability', 'fish_breed_probability')
    def validate_proba(self, key, value):
        if value < 0 or value > 100:
            raise ValueError('{} must be between 0 and 100, not {}'.format(key, value))
        else:
            return value


class Animals(Base):
    __tablename__ = 'ANIMALS'
    oid = Column(Integer, primary_key=True, autoincrement=True)
    sim_id = Column(ForeignKey("{}.{}.sid".format(schema, Simulation.__tablename__)))
    animal_type = Column(Enum(Animal))
    spawn_turn = Column(Integer)
    breed_count = Column(Integer)
    last_breed = Column(Integer)
    last_fed = Column(Integer)
    alive = Column(Boolean)
    coord_x = Column(Integer)
    coord_y = Column(Integer)

    __table_args__ = ({'schema': schema})

    def __repr__(self):
        if self.alive:
            type_display = self.animal_type.name
        else:
            type_display = 'Dead_{}'.format(self.animal_type.name)
        return "<oid={oid}: {type} :x={x:>3}, y={y:>3}".format(oid=self.oid, type=type_display, x=self.coord_x,
                                                               y=self.coord_y)


class SimulationClient(SQLAlchemyQueries):
    def __init__(self, database_url):
        super().__init__(database_url=database_url, declarative_base=Base, expire_on_commit=False)

    def init_simulation(self, grid_size, init_nb_fish, init_nb_shark, fish_breed_maturity, fish_breed_probability,
                        fish_speed, shark_breed_maturity, shark_breed_probability, shark_speed,
                        shark_starving):
        """
        Initialize a simulation and return the sid
        :param grid_size:
        :param init_nb_fish:
        :param init_nb_shark:
        :param fish_breed_maturity:
        :param fish_breed_probability:
        :param fish_speed:
        :param shark_breed_maturity:
        :param shark_breed_probability:
        :param shark_speed:
        :param shark_starving:
        :return:
        """
        # first check some inputs
        if grid_size ** 2 < (init_nb_fish + init_nb_shark):
            raise ValueError('initial number of animals bigger than grid size....')
        assert fish_breed_maturity > 0, "fish_breed_maturity must be positive"
        assert fish_speed > 0, "fish_speed must be positive"
        assert shark_breed_maturity > 0, "shark_breed_maturity must be positive"
        assert shark_speed > 0, "shark_speed must be positive"
        assert shark_starving > 0, "shark_starving must be positive"

        with self.session_scope() as s:
            s.add(Simulation(timestamp=dt.datetime.now(), grid_size=grid_size, init_nb_fish=init_nb_fish,
                             init_nb_shark=init_nb_shark, fish_breed_maturity=fish_breed_maturity,
                             fish_breed_probability=fish_breed_probability,
                             fish_speed=fish_speed, shark_breed_maturity=shark_breed_maturity,
                             shark_breed_probability=shark_breed_probability, shark_speed=shark_speed,
                             shark_starving=shark_starving))
            s.flush()
            sid = s.query(func.max(Simulation.sid)).one()[0]
        return sid

    def get_simulation(self, sim_id: int) -> Simulation:
        """
        Fetch a simulation by id
        :param sim_id:
        :return:
        """
        with self.session_scope() as s:
            return s.query(Simulation).filter(Simulation.sid == sim_id).one()

    def get_all_simulations(self):
        """
        Retrieve all simulations in a panda DataFrame
        :return: DataFrame
        """
        with self.session_scope() as s:
            query = s.query(Simulation)
            return pd.read_sql(query.statement, query.session.bind)

    def init_animal(self, sim_id: int, current_turn: int, animal_type: Animal, coordinate: SquareGridCoordinate,
                    last_fed: Optional[int] = 0, last_breed: Optional[int] = 0):
        """
        use for single animal init
        :return:
        """

        with self.session_scope() as s:
            try:
                simulation = s.query(Simulation).filter(Simulation.sid == sim_id).one()
                s.flush()
            except NoResultFound:
                _logger.debug("Simulation {} doesn't exist!".format(sim_id))
                raise ValueError("Simulation {} doesn't exist!".format(sim_id))
            # Check coordinate match with the grid
            square_grid_valid(grid_size=simulation.grid_size, coordinates=coordinate)
            # check if coordinate is free
            if self.coordinate_is_occupied(sim_id=sim_id, coordinate=coordinate):
                raise NonEmptyCoordinate('Coordinate {} is occupied'.format(coordinate))
            new_animal = Animals(sim_id=simulation.sid, animal_type=animal_type, spawn_turn=current_turn,
                                 breed_count=0, last_breed=last_breed, alive=True, last_fed=last_fed,
                                 coord_x=coordinate.x, coord_y=coordinate.y)
            s.add(new_animal)
        return new_animal.oid

    def coordinate_is_occupied(self, sim_id: int, coordinate: SquareGridCoordinate) -> bool:
        """
        Check if coordinate is free for this epoch
        :param sim_id:
        :param coordinate:
        :return:
        """
        with self.session_scope() as s:
            query = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.coord_x == coordinate.x,
                                            Animals.coord_y == coordinate.y, Animals.alive)
            return s.query(query.exists()).scalar()

    def get_animal(self, sim_id: int, animal_id: int) -> Animal:
        """
        Retrieve a single animal
        :param sim_id:
        :param animal_id:
        :return:
        """
        with self.session_scope() as s:
            q = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.oid == animal_id)
            return q.one()

    def get_animal_in_position(self, sim_id, coordinate: SquareGridCoordinate, live_only: bool = True):
        """

        :param sim_id:
        :param coordinate:
        :param live_only:
        :return:
        """
        with self.session_scope() as s:
            query = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.coord_x == coordinate.x,
                                            Animals.coord_y == coordinate.y)
            if live_only:
                query = query.filter(Animals.alive)
            return query.all()

    def get_animals_by_type(self, sim_id: int, animal_type: Animal) -> pd.DataFrame:
        """

        :param sim_id:
        :param animal_type:
        :return:
        """
        with self.session_scope() as s:
            q = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.alive, Animals.animal_type == animal_type)
            return pd.read_sql(q.statement, q.session.bind)

    def get_animals_df(self, sim_id: int):
        """
        Load all live animals from grid into a dataframe
        :param sim_id:
        :return:
        """
        with self.session_scope() as s:
            q = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.alive)
            return pd.read_sql(q.statement, q.session.bind)

    def has_fish_in_square(self, sim_id: int, coordinates: List[SquareGridCoordinate]) -> List[SquareGridCoordinate]:
        """
        Return a list of coordinate where fish are present
        :param sim_id:
        :param coordinates:
        :return:
        """
        fish_df = self.get_animals_by_type(sim_id=sim_id, animal_type=Animal.Fish)
        has_fish = []
        for coord in coordinates:
            fta = fish_df[(fish_df.coord_x == coord.x) & (fish_df.coord_y == coord.y)]
            if len(fta) > 0:
                has_fish.append(SquareGridCoordinate(int(fta.iloc[0].coord_x), int(fta.iloc[0].coord_y)))
        return has_fish

    def update_animals(self, sim_id: int, update_dict: Dict):
        """
        Update some animal attribute Only for
        - breed_count
        - last_breed
        - last_fed
        :param sim_id:
        :param update_dict:
        :return:
        """
        scope = list(update_dict.keys())
        with self.session_scope() as s:
            animal_list = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.alive).all()
            for animal in animal_list:
                if animal.oid in scope:
                    for k, v in update_dict[animal.oid].items():
                        if k in ['breed_count', 'last_breed', 'last_fed']:
                            setattr(animal, k, v)
                        else:
                            _logger.error('Cannot update {} property with this method'.format(k))
            s.flush()
        return

    def kill_animal(self, sim_id: int, animal_ids: List[int]):
        """
        Set alive property to False
        :param sim_id:
        :param animal_ids:
        :return:
        """
        with self.session_scope() as s:
            animal_list = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.alive).all()
            for animal in animal_list:
                if animal.oid in animal_ids:
                    animal.alive = False
            s.flush()
        return

    def eat_animal_in_square(self, sim_id: int, coordinate: SquareGridCoordinate):
        """
        Kill the animal in this square (after eating it)
        :param sim_id:
        :param coordinate:
        :return:
        """
        with self.session_scope() as s:
            try:
                eaten_animal = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.alive,
                                                       Animals.animal_type == Animal.Fish,
                                                       Animals.coord_x == coordinate.x,
                                                       Animals.coord_y == coordinate.y).one()
                eaten_animal.alive = False
                return True
            except NoResultFound:
                _logger.warning('No Fish to eat in {}'.format(coordinate))
                return False

    def move_animal(self, sim_id: int, animal_id: int, new_position: SquareGridCoordinate):
        """

        :param sim_id:
        :param animal_id:
        :param new_position:
        :return:
        """
        if self.coordinate_is_occupied(sim_id=sim_id, coordinate=new_position):
            raise NonEmptyCoordinate('Cannot move, coordinate {} is occupied'.format(new_position))

        with self.session_scope() as s:
            simulation = s.query(Simulation).filter(Simulation.sid == sim_id).one()
            # Check coordinate match with the grid
            square_grid_valid(grid_size=simulation.grid_size, coordinates=new_position)
            a_ = s.query(Animals).filter(Animals.sim_id == sim_id, Animals.oid == animal_id).one()
            if a_.alive:
                a_.coord_x = new_position.x
                a_.coord_y = new_position.y
            else:
                raise ImpossibleAction('Attempting to move a dead animal: {}'.format(a_))
