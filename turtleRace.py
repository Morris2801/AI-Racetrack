import turtle
import random
import math
import time

# Screen setup
screen = turtle.Screen()
screen.bgcolor("green")
screen.title("AI Racing Track")
screen.setup(1200, 800)
screen.tracer(0)

# Global speed control
simulation_speed = 1

# Speed slider setup
def setup_speed_slider():
    slider = turtle.Turtle()
    slider.shape("square")
    slider.color("blue")
    slider.penup()
    slider.goto(450, 350)
    slider.write("Speed: 1x", font=("Arial", 12, "normal"))
    slider.hideturtle()
    
    def speed_up():
        global simulation_speed
        simulation_speed = min(10, simulation_speed + 1)
        update_speed_display()
    
    def speed_down():
        global simulation_speed
        simulation_speed = max(1, simulation_speed - 1)
        update_speed_display()
    
    def update_speed_display():
        slider.clear()
        slider.write(f"Speed: {simulation_speed}x", font=("Arial", 12, "normal"))
    
    screen.onkey(speed_up, "Up")
    screen.onkey(speed_down, "Down")
    screen.listen()
    
    info = turtle.Turtle()
    info.penup()
    info.goto(450, 300)
    info.write("Up/Down arrows\nto change speed", font=("Arial", 10, "normal"))
    info.hideturtle()

# Track setup
def draw_track():
    track = turtle.Turtle()
    track.speed(0)
    track.color("black")
    track.pensize(5)
    
    # Outer track boundary
    track.penup()
    track.goto(-400, 300)
    track.pendown()
    track.goto(400, 300)
    track.goto(400, -300)
    track.goto(-400, -300)
    track.goto(-400, 300)
    
    # Inner track boundary
    track.penup()
    track.goto(-300, 200)
    track.pendown()
    track.goto(300, 200)
    track.goto(300, -200)
    track.goto(-300, -200)
    track.goto(-300, 200)
    
    # Start/finish line
    track.color("white")
    track.pensize(3)
    track.penup()
    track.goto(-400, 250)
    track.pendown()
    track.goto(-300, 250)
    
    # Draw LARGER checkpoints for better detection
    track.color("yellow")
    track.pensize(4)
    
    # Checkpoint 1 - First corner (BIGGER area)
    track.penup()
    track.goto(300, 300)
    track.pendown()
    track.goto(400, 200)
    track.write("1", font=("Arial", 16, "bold"))
    
    # Checkpoint 2 - Second corner (BIGGER area)
    track.penup()
    track.goto(300, -200)
    track.pendown()
    track.goto(400, -300)
    track.write("2", font=("Arial", 16, "bold"))
    
    # Checkpoint 3 - Third corner (BIGGER area)
    track.penup()
    track.goto(-300, -300)
    track.pendown()
    track.goto(-400, -200)
    track.write("3", font=("Arial", 16, "bold"))
    
    track.hideturtle()

# Car class
class Car:
    def __init__(self, x, y):
        self.turtle = turtle.Turtle()
        self.turtle.shape("turtle")
        self.turtle.color("red")
        self.turtle.penup()
        self.turtle.goto(x, y)
        self.turtle.speed(0)
        self.turtle.setheading(0)
        
        # AI brain
        self.weights = []
        for i in range(12):
            self.weights.append(random.uniform(-1, 1))
        
        # Performance tracking
        self.fitness = 0
        self.time_alive = 0
        self.distance_traveled = 0
        self.crashed = False
        self.start_x = x
        self.start_y = y
        
        # Enhanced checkpoint tracking
        self.checkpoint1_passed = False
        self.checkpoint2_passed = False
        self.checkpoint3_passed = False
        self.lap_completed = False
        
        # Track progress for better rewards
        self.max_x = x  # Furthest right reached
        self.min_y = y  # Furthest down reached
        self.min_x = x  # Furthest left reached
        
        # Movement
        self.speed = 1
        self.max_speed = 4
        
    def reset_position(self):
        self.turtle.goto(self.start_x, self.start_y)
        self.turtle.setheading(0)
        self.turtle.color("red")
        self.speed = 1
        self.fitness = 0
        self.time_alive = 0
        self.distance_traveled = 0
        self.crashed = False
        
        # Reset progress tracking
        self.checkpoint1_passed = False
        self.checkpoint2_passed = False
        self.checkpoint3_passed = False
        self.lap_completed = False
        self.max_x = self.start_x
        self.min_y = self.start_y
        self.min_x = self.start_x
        
    def get_sensors(self):
        sensors = []
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        heading = self.turtle.heading()
        
        sensor_angles = [-90, -45, 0, 45, 90]
        
        for angle_offset in sensor_angles:
            actual_angle = heading + angle_offset
            distance = self.check_distance(x, y, actual_angle)
            sensors.append(distance / 100.0)
        
        return sensors
    
    def check_distance(self, x, y, angle):
        test_x = x
        test_y = y
        distance = 0
        
        while distance < 100:
            test_x += math.cos(math.radians(angle)) * 2
            test_y += math.sin(math.radians(angle)) * 2
            distance += 2
            
            if test_x > 395 or test_x < -395 or test_y > 295 or test_y < -295:
                return distance
            
            if -295 < test_x < 295 and -195 < test_y < 195:
                return distance
                
        return 100
    
    def think(self, sensors):
        # BETTER: Let AI learn with minimal rule interference
        left_sensor = sensors[0]
        front_left = sensors[1]
        front_sensor = sensors[2]
        front_right = sensors[3]
        right_sensor = sensors[4]
        
        # Calculate AI decision
        turn_decision = 0
        for i in range(5):
            turn_decision += sensors[i] * self.weights[i]
        
        # Speed decision
        speed_decision = 0
        for i in range(5):
            if i + 5 < len(self.weights):
                speed_decision += sensors[i] * self.weights[i + 5]
        
        # ONLY use rules for emergency crash prevention
        emergency_turn = 0
        if front_sensor < 0.2:  # Very close to wall ahead
            if left_sensor > right_sensor:  # More space left
                emergency_turn = -1
            else:  # More space right
                emergency_turn = 1
        
        # Apply decisions
        if emergency_turn != 0:  # Emergency override
            if emergency_turn < 0:
                self.turtle.left(15)  # Strong emergency turn
            else:
                self.turtle.right(15)
        else:  # Normal AI control
            turn_strength = max(-10, min(10, turn_decision * 8))  # Limit turn
            if turn_strength > 1:
                self.turtle.right(turn_strength)
            elif turn_strength < -1:
                self.turtle.left(abs(turn_strength))
        
        # Speed control
        if front_sensor < 0.3:  # Slow down near walls
            self.speed = max(0.5, self.speed - 0.1)
        elif speed_decision > 0 and self.speed < self.max_speed:
            self.speed += 0.05
        elif speed_decision < 0 and self.speed > 0.5:
            self.speed -= 0.05
    
    def move(self):
        if not self.crashed:
            old_x = self.turtle.xcor()
            old_y = self.turtle.ycor()
            
            self.turtle.forward(self.speed)
            
            new_x = self.turtle.xcor()
            new_y = self.turtle.ycor()
            
            # Track progress for fitness
            self.max_x = max(self.max_x, new_x)
            self.min_y = min(self.min_y, new_y)
            self.min_x = min(self.min_x, new_x)
            
            # Calculate distance traveled
            dist = math.sqrt((new_x - old_x)**2 + (new_y - old_y)**2)
            self.distance_traveled += dist
            
            self.time_alive += 1
            
            self.check_checkpoints()
            
    def check_checkpoints(self):
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        
        # BIGGER checkpoint areas for better detection
        # Checkpoint 1: First corner (top right) - MUCH BIGGER
        if not self.checkpoint1_passed and x > 280 and 180 < y < 320:
            self.checkpoint1_passed = True
            self.turtle.color("orange")
            print(f"Car reached checkpoint 1! x={x:.1f}, y={y:.1f}")
        
        # Checkpoint 2: Second corner (bottom right) - BIGGER
        elif not self.checkpoint2_passed and self.checkpoint1_passed and x > 280 and -320 < y < -180:
            self.checkpoint2_passed = True
            self.turtle.color("yellow")
            print(f"Car reached checkpoint 2! x={x:.1f}, y={y:.1f}")
        
        # Checkpoint 3: Third corner (bottom left) - BIGGER
        elif not self.checkpoint3_passed and self.checkpoint2_passed and x < -280 and -320 < y < -180:
            self.checkpoint3_passed = True
            self.turtle.color("green")
            print(f"Car reached checkpoint 3! x={x:.1f}, y={y:.1f}")
        
        # Lap completed: Back to start area - BIGGER
        elif not self.lap_completed and self.checkpoint3_passed and x < -280 and 180 < y < 320:
            self.lap_completed = True
            self.turtle.color("gold")
            print(f"Car completed lap! x={x:.1f}, y={y:.1f}")
            
    def check_crash(self):
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        
        if x > 395 or x < -395 or y > 295 or y < -295:
            self.crashed = True
            self.turtle.color("gray")
            return True
            
        if -295 < x < 295 and -195 < y < 195:
            self.crashed = True
            self.turtle.color("gray")
            return True
            
        return False
    
    def calculate_fitness(self):
        # MUCH BETTER fitness calculation
        base_fitness = self.distance_traveled + (self.time_alive * 0.05)
        
        # Progressive movement rewards (reward partial progress)
        progress_bonus = 0
        
        # Reward moving right (toward first corner)
        progress_bonus += max(0, (self.max_x - self.start_x) * 5)
        
        # Reward moving down (toward second corner)
        if self.max_x > 200:  # If made it far right
            progress_bonus += max(0, (self.start_y - self.min_y) * 5)
        
        # Reward moving left (toward third corner)
        if self.min_y < -100:  # If made it far down
            progress_bonus += max(0, (self.max_x - self.min_x) * 5)
        
        # BIG checkpoint bonuses
        checkpoint_bonus = 0
        if self.checkpoint1_passed:
            checkpoint_bonus += 2000
        if self.checkpoint2_passed:
            checkpoint_bonus += 4000  
        if self.checkpoint3_passed:
            checkpoint_bonus += 6000
        
        # HUGE lap bonus
        lap_bonus = 15000 if self.lap_completed else 0
        
        # Time bonus (reward faster completion)
        time_bonus = 0
        if self.lap_completed:
            time_bonus = max(0, 1000 - self.time_alive)
        
        self.fitness = base_fitness + progress_bonus + checkpoint_bonus + lap_bonus + time_bonus
        
        return self.fitness

# Genetic Algorithm (same structure, better parameters)
class Evolution:
    def __init__(self, population_size):
        self.population_size = population_size
        self.generation = 0
        self.cars = []
        
        for i in range(population_size):
            y_offset = (i - population_size//2) * 8  # Better spacing
            car = Car(-350, 250 + y_offset)
            self.cars.append(car)
    
    def run_generation(self):
        for car in self.cars:
            car.reset_position()
        
        for step in range(3000):  # More time for learning
            alive_cars = 0
            
            for car in self.cars:
                if not car.crashed:
                    sensors = car.get_sensors()
                    car.think(sensors)
                    car.move()
                    car.check_crash()
                    alive_cars += 1
            
            if step % simulation_speed == 0:
                screen.update()
            
            if alive_cars == 0:
                break
        
        for car in self.cars:
            car.calculate_fitness()
        
        self.cars.sort(key=lambda x: x.fitness, reverse=True)
        best_car = self.cars[0]
        
        print(f"Generation {self.generation} complete")
        print(f"Best fitness: {best_car.fitness:.2f}")
        print(f"Best progress: x={best_car.max_x:.1f}, min_y={best_car.min_y:.1f}")
        checkpoints = 0
        if best_car.checkpoint1_passed: checkpoints += 1
        if best_car.checkpoint2_passed: checkpoints += 1  
        if best_car.checkpoint3_passed: checkpoints += 1
        print(f"Best checkpoints: {checkpoints}/3")
        if best_car.lap_completed:
            print("LAP COMPLETED!")
        
    def evolve(self):
        # Keep top 30% for better diversity
        survivors = max(3, int(self.population_size * 0.3))
        new_population = []
        
        for i in range(survivors):
            survivor = Car(self.cars[i].start_x, self.cars[i].start_y)
            survivor.weights = self.cars[i].weights.copy()
            new_population.append(survivor)
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(self.cars[:survivors])
            parent2 = random.choice(self.cars[:survivors])
            child = self.create_child(parent1, parent2)
            new_population.append(child)
        
        self.cars = new_population
        self.generation += 1
    
    def create_child(self, parent1, parent2):
        child = Car(parent1.start_x, parent1.start_y)
        
        for i in range(len(child.weights)):
            if random.random() < 0.5:
                child.weights[i] = parent1.weights[i]
            else:
                child.weights[i] = parent2.weights[i]
            
            # Reduced mutation for more stable learning
            if random.random() < 0.15:  # 15% chance to mutate
                child.weights[i] += random.uniform(-0.2, 0.2)
                child.weights[i] = max(-2, min(2, child.weights[i]))  # Larger range
        
        return child

# Main program
def main():
    draw_track()
    setup_speed_slider()
    
    evolution = Evolution(20)  # More cars for better learning
    
    for gen in range(200):  # More generations
        print(f"\nStarting Generation {gen + 1}")
        evolution.run_generation()
        evolution.evolve()
        
        time.sleep(0.3 / simulation_speed)
    
    print("Evolution complete!")

if __name__ == "__main__":
    main()
    screen.exitonclick()