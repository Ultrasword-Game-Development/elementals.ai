
import pygame
import neat

from engine import io
from engine import utils

from engine.handler import component
from engine.handler import aspect

# ---------------------------- #
# constants

COMPONENT_NAME = "NeuralNetComponent"

POP_OBJ = 0
POP_COMP_LIST = 1
POP_RESET = 2
POP_SIZE = 3
POP_REPRODUCE = 4


# ---------------------------- #
# component

class NeuralNetComponent(component.Component):
    def __init__(self, population_name: str, fitness_func: callable):
        super().__init__()

        self._pop_name = population_name
        self._pop = None

        self._genome = None
        self._network = None

        self._fitness_func = fitness_func

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)

        # get population
        self._pop = self._parent_aspect.get_population(self._pop_name)[0]
        self._parent_aspect.add_neuralnet(self._pop_name, self)

    # ---------------------------- #
    # logic
    
    def reset_network(self, genome: "Genome"):
        """ Reset the network """
        self._genome = genome
        self._genome.fitness = 0
        self._network = neat.nn.FeedForwardNetwork.create(genome, self._pop.config)

# ---------------------------- #
# aspect

class NeuralNetAspect(aspect.Aspect):
    def __init__(self, config_path: str):
        super().__init__(target_component_classes=[NeuralNetComponent])

        # load neural net
        self._config_path = config_path
        self._config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self._config_path
        )

        self._populations = {}
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """

        # update the population
        for _population in self._populations:
            _data = self._populations[_population]
            _comp_list = _data[POP_COMP_LIST]

            new_pop_flag = False
            if _data[POP_RESET]:
                # generate new networks
                _data[POP_RESET] = False
                _data[POP_OBJ].population = _data[POP_OBJ].reproduction.create_new(
                    _data[POP_OBJ].config.genome_type,
                    _data[POP_OBJ].config.genome_config,
                    _data[POP_SIZE]
                )
                # create all new neural networks
                i = 0
                # print(_data[POP_OBJ].population.items())
                for _, val in sorted(_data[POP_OBJ].population.items())[:2]:
                    _data[POP_OBJ].population[_].fitness = 0
                for _, val in sorted(_data[POP_OBJ].population.items())[2:]:
                    _comp_list[i].reset_network(_data[POP_OBJ].population[_])
                    i += 1
                
                # set flag
                new_pop_flag = True
            elif _data[POP_REPRODUCE]:
                _data[POP_REPRODUCE] = False

                # reproduce
                _data[POP_OBJ].population = _data[POP_OBJ].reproduction.reproduce(
                    _data[POP_OBJ].config,
                    _data[POP_OBJ].species,
                    _data[POP_SIZE],
                    _data[POP_OBJ].generation
                )
                # create all new neural networks
                i = 0
                for _, val in sorted(_data[POP_OBJ].population.items())[2:]:
                    _comp_list[i].reset_network(_data[POP_OBJ].population[_])
                    i += 1

                # split new population into species
                _data[POP_OBJ].species.speciate(
                    _data[POP_OBJ].config,
                    _data[POP_OBJ].population,
                    _data[POP_OBJ].generation
                )

                _data[POP_OBJ].reporters.end_generation(
                    _data[POP_OBJ].config,
                    _data[POP_OBJ].population,
                    _data[POP_OBJ].species
                )

                _data[POP_OBJ].generation += 1

                # set flag
                new_pop_flag = True
            
            # if new pop was created
            if new_pop_flag:
                # update reporters
                _pop = _data[POP_OBJ]

                _pop.reporters.start_generation(_pop.generation)
                # gather stats
                best = None
                for g in utils.itervalues(_pop.population):
                    if best is None or g.fitness > best.fitness:
                        best = g
                _pop.reporters.post_evaluate(_pop.config, _pop.population, _pop.species, best)

                # track best genome
                if _pop.best_genome is None or best.fitness > _pop.best_genome.fitness:
                    _pop.best_genome = best

                if not _pop.config.no_fitness_termination:
                    # end if fitness threshold is reached
                    fv = _pop.fitness_criterion(g.fitness for g in utils.itervalues(_pop.population))
                    if fv >= _pop.config.fitness_threshold:
                        _pop.reporters.found_solution(_pop.config, _pop.generation, best)
                        break
                
                # then create new generation

                # check for complete extinction
                if not _pop.species.species:
                    _pop.reporters.complete_extinction()

                    # if requested by user, create new population
                    if _pop.config.reset_on_extinction:
                        _pop.population = _pop.reproduction.create_new(
                            _pop.config.genome_type,
                            _pop.config.genome_config,
                            _pop.config.pop_size
                        )
                    else:
                        raise CompleteExtinctionException()


            for _comp in _comp_list:
                _comp._fitness_func(_comp)
            
            # check if population should be reset???
    
    def get_population(self, name: str):
        """ 
        
        Get the population 
        
        As per the settings inside of the config file (default file) located at:
        - assets/default-genome-config.txt

        The initial population size = 0.

        Programmers must manually create new genomes and add them to the population.

        """
        if name not in self._populations:
            self._populations[name] = [
                neat.Population(self._config),
                [],     # list of components
                True,   # determins if needs to start/reset
                2,      # size of the population
                False,  # if needs to reproduce
            ]
            # self._populations[name].add_reporter(neat.StdOutReporter(True))
            # self._populations[name].add_reporter(neat.StatisticsReporter())
        return self._populations[name]
    
    def add_neuralnet(self, population_name: str, neuralnet_comp: "NeuralNetComponent"):
        """ Add a genome to the population """
        _pop = self.get_population(population_name)
        _pop[POP_COMP_LIST].append(neuralnet_comp)
        _pop[POP_SIZE] += 1

    def remove_neuralnet(self, neuralnet_comp: "NeuralNetComponent"):
        """ Remove a genome from the population """
        if not neuralnet_comp._pop_name in self._populations:
            return
        
        _pop = self._populations[neuralnet_comp._pop_name]
        _pop[1].remove(neuralnet_comp)
    
    def reset_population(self, population_name: str):
        """ Reset the population """
        self._populations[population_name] = None
        return self.get_population(population_name)



# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(NeuralNetComponent)
