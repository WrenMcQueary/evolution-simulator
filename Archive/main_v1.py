"""First draft of an evolution simulator code for KID Museum.

Generates zorks (winged giraffe-like animals) with random traits.  Grades each zork's survivability based on its
traits.  Culls zorks that fall below a certain threshold.  Zorks mate in random pairs to create new zorks
"""

# Imports
import random
import statistics
from matplotlib import pyplot as plt

# Todos
    # Within the scope of KID Museum:
        # TODO: Simplify code using list comprehension?
        # TODO: Figure out how kids can interact with it.  Is it a black box where they get to control parameters, and thus gain intuition about evolution?
        # TODO: Draw zorks graphically?
    # Beyond the scope of KID Museum:
        # TODO: Let culling decision be based on not only survivability rating, but also random chance.  It shouldn't be fully predetermined whether a zork survives based on their traits.
        # TODO: Let culling threshold be based on current population, to mimic environmental capacity.
        # TODO: Let the population change from generation to generation dynamically, instead of holding it constant.


# Zork class, including attributes and methods
class Zork:
    """A goofy animal with some traits."""

    def __init__(self, vitals, mutation_percentage, parent1=None, parent2=None, leg_length=None, fur_length=None, wingspan=None, final_survivability=None):
        """Vitals is a string: either "alive", "failed", or "retired".
        parent1 and parent2 are each tuples of integers (a, b), where a is the generation of the parent, and b is that
        parent's index in the generation.
        leg_length is a float.
        fur_length is a float.
        wingspan is a float.
        spectrum values represent the difference between the minimum and maximum possible values for a trait.
        final_survivability is a float.
        """
        self.vitals = vitals
        self.mutation_percentage = mutation_percentage
        self.parent1 = parent1
        self.parent2 = parent2
        self.boundaries_leg_length = (1.2, 2.5)         # Meters
        self.spectrum_leg_length = abs(self.boundaries_leg_length[1] - self.boundaries_leg_length[0])
        self.boundaries_fur_length = (0.0064, 0.0508)   # Meters
        self.spectrum_fur_length = abs(self.boundaries_fur_length[1] - self.boundaries_fur_length[0])
        self.boundaries_wingspan = (28, 38)             # Meters
        self.spectrum_wingspan = abs(self.boundaries_wingspan[1] - self.boundaries_wingspan[0])
        self.leg_length = leg_length
        self.fur_length = fur_length
        self.wingspan = wingspan
        self.final_survivability = final_survivability

    def set_traits(self):
        """Sets traits for this particular zork.  If this is a generation 0 zork, traits are completely random.
        Else, traits are based on the traits of parents, with some random noise thrown in.
        """
        if self.parent1 is None and self.parent2 is None:     # No parents; generate from random parameters.
            self.leg_length = random.uniform(self.boundaries_leg_length[0], self.boundaries_leg_length[1])
            self.fur_length = random.uniform(self.boundaries_fur_length[0], self.boundaries_fur_length[1])
            self.wingspan = random.uniform(self.boundaries_wingspan[0], self.boundaries_wingspan[1])
        else:   # This zork has parents; generate from average of parents' paremeters ± mutation * spectrum, then limit the trait to the boundaries if that trait exceeded the boundaries.
            self.leg_length = statistics.mean([self.parent1.leg_length, self.parent2.leg_length]) + random.uniform(-self.mutation_percentage, self.mutation_percentage) * self.spectrum_leg_length
            if self.leg_length < self.boundaries_leg_length[0]:
                self.leg_length = self.boundaries_leg_length[0]
            elif self.leg_length > self.boundaries_leg_length[1]:
                self.leg_length = self.boundaries_leg_length[1]

            self.fur_length = statistics.mean([self.parent1.fur_length, self.parent2.fur_length]) + random.uniform(-self.mutation_percentage, self.mutation_percentage) * self.spectrum_fur_length
            if self.fur_length < self.boundaries_fur_length[0]:
                self.fur_length = self.boundaries_fur_length[0]
            elif self.fur_length > self.boundaries_fur_length[1]:
                self.fur_length = self.boundaries_fur_length[1]

            self.wingspan = statistics.mean([self.parent1.wingspan, self.parent2.wingspan]) + random.uniform(-self.mutation_percentage, self.mutation_percentage) * self.spectrum_wingspan
            if self.wingspan < self.boundaries_wingspan[0]:
                self.wingspan = self.boundaries_wingspan[0]
            elif self.wingspan > self.boundaries_wingspan[1]:
                self.wingspan = self.boundaries_wingspan[1]

    def grade_survivability(self):
        """Outputs a survivability rating for this particular zork.
        Each trait results in a specific survivability rating, between -3 (extremely detrimental) and +3 (extremely
        beneficial).  Less important traits have smaller ranges in survivability ratings.

        legs of middle length are preferred; short legs make it hard for the zork to reach food, while excessively long legs cause blood pressure issues.  A negative quadratic function converts length to survivability_leg_length.
        short fur is slightly preferred; zorks live in a hot environment.  A linear function converts fur length to survivability_fur_length.
        long wingspan is preferred; zorks can only fly at all if their wingspan is 32 m or greater.  Else, wings are detrimental dead weight  A piecewise linear function converts wingspan to survivability_wingspan.


        final_survivability is the average of all other survivability ratings.
        """
        survivability_leg_length = -((6 ** 0.5 / 0.65) * (self.leg_length - 1.85)) ** 2 + 3
        survivability_fur_length = 45.045 * self.fur_length - 1.288
        if self.wingspan < 32:
            survivability_wingspan = -2
        else:
            survivability_wingspan = 0.5 * self.wingspan - 16

        self.final_survivability = statistics.mean([survivability_leg_length, survivability_fur_length, survivability_wingspan])
        return self.final_survivability


# Parameters
max_number_generations = 100    # Total number of generations to simulate.
threshold_to_survive = 0     # Minimum survivability rating that a zork needs not to fail.
zorks_per_generation = 100  # Number of zorks in each generation.
mutation_percentage = 0.05  # A child's trait will equal the average of their parents' traits plus or minus up to this percentage of the range for that trait.  0.05 is 5%.

# Set initial variables.
all_zorks = []  # List of lists.  Each list is a generation containing zorks_per_generation zorks.

# Main loop.
for generation in range(max_number_generations):
    # Create new zorks.
    zorks_this_generation = []
    if generation == 0:     # If this generation 0:
        for specimen in range(zorks_per_generation):
            zorks_this_generation.append(Zork("alive", mutation_percentage))
            zorks_this_generation[specimen].set_traits()
    else:   # If this isn't generation 0:
        # Retire all alive zorks from the last generation.
        for specimen in all_zorks[generation - 1]:
            if specimen.vitals == "alive":
                specimen.vitals = "retired"
        # Let surviving (and therefore now retired) zorks from generation-1 mate randomly to create a new generation of zorks_per_generation zorks.  For the new zorks, include setting parameters parent1 and parent2.  Zorks can self-reproduce on occasion.
        reproducing_zorks = [specimen for specimen in all_zorks[generation - 1] if specimen.vitals == "retired"]  # Create a list of retired zorks from the last generation.  All retired zorks have a chance to reproduce.
        for specimen in range(zorks_per_generation):
            zorks_this_generation.append(Zork("alive", mutation_percentage, parent1=random.choice(reproducing_zorks), parent2=random.choice(reproducing_zorks)))
            zorks_this_generation[specimen].set_traits()
        reproducing_zorks = []  # Empty list of reproducing_zorks to avoid confusion.

    all_zorks.append(zorks_this_generation)
    zorks_this_generation = []  # For clarity, because this list will now become outdated, empty it.

    # Grade each zork in this generation based on its traits, outputting a survivability rating.
    for specimen in all_zorks[generation]:
        specimen.grade_survivability()

    # Cull zorks in this generation whose survivability falls below a certain threshold.
    for specimen in all_zorks[generation]:
        if specimen.final_survivability < threshold_to_survive:
            specimen.vitals = "failed"

    # If this is the last generation, retire zorks in the final generation without them reproducing.
    if generation == max_number_generations - 1:
        for specimen in all_zorks[generation]:
            if specimen.vitals == "alive":
                specimen.vitals = "retired"



# Gather data to plot results
# Number of surviving zorks in each generation
group_survivors = []
for generation in all_zorks:
    survivors_this_generation = 0
    for zork in generation:
        if zork.vitals == "retired":
            survivors_this_generation = survivors_this_generation + 1
    group_survivors.append(survivors_this_generation)

# Average survivability in each generation
group_survivability = []
for generation in all_zorks:
    survivabilities_this_generation = []
    for zork in generation:
        survivabilities_this_generation.append(zork.final_survivability)
    group_survivability.append(statistics.mean(survivabilities_this_generation))

# Average traits and standard deviations within traits in each generation
group_leg_length = []
group_standard_deviation_leg_length = []
for generation in all_zorks:
    leg_length_this_generation = []
    for zork in generation:
        leg_length_this_generation.append(zork.leg_length)
    group_leg_length.append(statistics.mean(leg_length_this_generation))
    group_standard_deviation_leg_length.append(statistics.stdev(leg_length_this_generation))

group_fur_length = []
group_standard_deviation_fur_length = []
for generation in all_zorks:
    fur_length_this_generation = []
    for zork in generation:
        fur_length_this_generation.append(zork.fur_length)
    group_fur_length.append(statistics.mean(fur_length_this_generation))
    group_standard_deviation_fur_length.append(statistics.stdev(fur_length_this_generation))

group_wingspan = []
group_standard_deviation_wingspan = []
for generation in all_zorks:
    wingspan_this_generation = []
    for zork in generation:
        wingspan_this_generation.append(zork.wingspan)
    group_wingspan.append(statistics.mean(wingspan_this_generation))
    group_standard_deviation_wingspan.append(statistics.stdev(wingspan_this_generation))

# Plot results versus generation.
plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_survivors)
plt.title("Number of surviving animals")
plt.ylabel("Number of surviving animals")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_survivability)
plt.title("Average survivability rating")
plt.ylabel("Average survivability rating")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_leg_length)
plt.title("Average leg length")
plt.ylabel("Average leg length")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_fur_length)
plt.title("Average fur length")
plt.ylabel("Average fur length")
plt.xlabel("Generation")


plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_wingspan)
plt.title("Average wingspan")
plt.ylabel("Average wingspan")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_standard_deviation_leg_length)
plt.title("Standard deviation of leg length")
plt.ylabel("Standard deviation of leg length")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_standard_deviation_fur_length)
plt.title("Standard deviation of fur length")
plt.ylabel("Standard deviation of fur length")
plt.xlabel("Generation")

plt.figure()
plt.grid()
plt.plot(range(max_number_generations), group_standard_deviation_wingspan)
plt.title("Standard deviation of wingspan")
plt.ylabel("Standard deviation of wingspan")
plt.xlabel("Generation")

plt.show()
