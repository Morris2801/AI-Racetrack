import turtle
import random

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Route:
    def __init__(self, outer_bounds, inner_bounds):
        self.outer_bounds = outer_bounds  # (min_x, max_x, min_y, max_y)
        self.inner_bounds = inner_bounds  # (min_x, max_x, min_y, max_y)
        self.start_point = Point(150, 37.5)
        self.end_point = Point(150, 37.5)  # Complete lap returns to start

class RacingTurtle:
    def __init__(self, route, dna=None):
        self.route = route
        self.x = route.start_point.x
        self.y = route.start_point.y
        self.moves = dna if dna else []
        self.current_move = 0
        self.fitness = 0
        self.completed = False
        self.crashed = False
        self.distance_traveled = 0
        
        # Create turtle graphics object
        self.turtle = turtle.Turtle()
        self.turtle.penup()
        self.turtle.goto(self.x, self.y)
        self.turtle.pendown()
        self.turtle.speed(0)
        self.turtle.shape("turtle")
        self.turtle.color(random.choice(['red', 'blue', 'green', 'orange', 'purple']))

    def move(self):
        if self.crashed or self.completed:
            return False
        
        old_x, old_y = self.x, self.y
        
        # Generate new random move if no DNA exists
        if self.current_move >= len(self.moves):
            direction = random.randint(1, 4)
            self.moves.append(direction)
        else:
            direction = self.moves[self.current_move]
        
        self.current_move += 1
        
        # Move in the chosen direction (smaller steps for smoother movement)
        step_size = 10
        if direction == 1:  # Right
            self.x += step_size
        elif direction == 2:  # Left
            self.x -= step_size
        elif direction == 3:  # Up
            self.y += step_size
        elif direction == 4:  # Down
            self.y -= step_size
        
        self.turtle.goto(self.x, self.y)
        
        # Calculate distance traveled
        self.distance_traveled += ((self.x - old_x)**2 + (self.y - old_y)**2)**0.5
        
        # Check if crashed (hit outer boundary or inner obstacle)
        if self.check_crash():
            self.crashed = True
            self.turtle.color('gray')
            self.fitness = self.calculate_fitness()
            return False
        
        # Check if completed lap (returned to start after traveling significant distance)
        if self.distance_traveled > 100 and abs(self.x - self.route.start_point.x) < 20 and abs(self.y - self.route.start_point.y) < 20:
            self.completed = True
            self.turtle.color('gold')
            self.fitness = self.calculate_fitness()
            return False
        
        return True

    def check_crash(self):
        outer = self.route.outer_bounds
        inner = self.route.inner_bounds
        
        # Check outer boundary collision
        if self.x < outer[0] or self.x > outer[1] or self.y < outer[2] or self.y > outer[3]:
            return True
        
        # Check inner obstacle collision
        if inner[0] < self.x < inner[1] and inner[2] < self.y < inner[3]:
            return True
        
        return False

    def calculate_fitness(self):
        # Fitness based on distance traveled and completion
        fitness = self.distance_traveled
        
        if self.completed:
            fitness += 10000  # Huge bonus for completing
            fitness -= len(self.moves) * 10  # Penalize longer routes
        
        return fitness

    def cleanup(self):
        self.turtle.hideturtle()
        self.turtle.clear()

class GeneticAlgorithm:
    def __init__(self, route, population_size=10):
        self.route = route
        self.population_size = population_size
        self.generation = 0
        self.best_fitness = 0
        self.best_dna = []
        
    def create_population(self, dna=None):
        population = []
        for i in range(self.population_size):
            if dna and i < 3:  # Keep top 3 from previous generation
                turtle_dna = dna.copy()
            else:
                turtle_dna = None
            population.append(RacingTurtle(self.route, turtle_dna))
        return population
    
    def evolve(self, population):
        # Sort by fitness
        population.sort(key=lambda t: t.fitness, reverse=True)
        
        best = population[0]
        if best.fitness > self.best_fitness:
            self.best_fitness = best.fitness
            self.best_dna = best.moves.copy()
            print(f"Generation {self.generation}: New best fitness = {best.fitness:.2f}, Moves = {len(best.moves)}, Completed = {best.completed}")
        
        # Create next generation with mutations
        next_gen_dna = []
        
        # Keep best DNA
        next_gen_dna.append(best.moves.copy())
        
        # Mutate best DNA for diversity
        for _ in range(self.population_size - 1):
            mutated = best.moves.copy()
            # Random mutations
            mutation_rate = 0.1
            for i in range(len(mutated)):
                if random.random() < mutation_rate:
                    mutated[i] = random.randint(1, 4)
            next_gen_dna.append(mutated)
        
        return next_gen_dna

def draw_racetrack():
    drawer = turtle.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    
    # Draw outer rectangle
    drawer.goto(-200, -200)
    drawer.pendown()
    drawer.pensize(3)
    for _ in range(4):
        drawer.forward(400)
        drawer.left(90)
    
    # Draw inner rectangle (obstacle)
    drawer.penup()
    drawer.goto(-100, -100)
    drawer.pendown()
    for _ in range(4):
        drawer.forward(200)
        drawer.left(90)
    
    drawer.penup()

def run_generation(ga, dna_list=None):
    population = []
    
    # Create population with DNA
    if dna_list:
        for dna in dna_list:
            population.append(RacingTurtle(ga.route, dna))
    else:
        population = ga.create_population()
    
    # Run simulation for max steps
    max_steps = 1000
    for step in range(max_steps):
        active = False
        for racer in population:
            if racer.move():
                active = True
        
        if not active:  # All turtles finished
            break
        
        turtle.update()
    
    # Clean up
    for racer in population:
        racer.cleanup()
    
    # Evolve
    next_gen_dna = ga.evolve(population)
    ga.generation += 1
    
    return next_gen_dna

def main():
    # Setup
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.title("Evolutionary Racing Turtles")
    screen.tracer(0)
    
    # Draw track
    draw_racetrack()
    
    # Create route with boundaries
    outer_bounds = (-200, 200, -200, 200)  # (min_x, max_x, min_y, max_y)
    inner_bounds = (-100, 100, -100, 100)  # Inner obstacle
    route = Route(outer_bounds, inner_bounds)
    
    # Create genetic algorithm
    ga = GeneticAlgorithm(route, population_size=10)
    
    # Run generations
    dna_list = None
    num_generations = 50
    
    print("Starting evolutionary training...")
    for gen in range(num_generations):
        dna_list = run_generation(ga, dna_list)
        screen.update()
    
    print(f"\nTraining complete!")
    print(f"Best fitness achieved: {ga.best_fitness:.2f}")
    print(f"Best route length: {len(ga.best_dna)} moves")
    
    turtle.done()

if __name__ == "__main__":
    main()