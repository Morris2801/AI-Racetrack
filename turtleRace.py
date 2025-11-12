import turtle
import random
import math
import time
import os

# Screen setup
screen = turtle.Screen()
screen.bgcolor("green")
screen.title("AI Racing Track - Sensor-Based Learning")
screen.setup(1200, 800)
screen.tracer(0)

# Global speed control
simulation_speed = 1

# UI Elements
ui_generation = None
ui_stats = None

def setup_ui():
    global ui_generation, ui_stats
    
    # Generation counter
    ui_generation = turtle.Turtle()
    ui_generation.hideturtle()
    ui_generation.penup()
    ui_generation.goto(-580, 360)
    ui_generation.color("white")
    
    # Stats display
    ui_stats = turtle.Turtle()
    ui_stats.hideturtle()
    ui_stats.penup()
    ui_stats.goto(-580, 320)
    ui_stats.color("white")
    
    # Speed control info
    speed_info = turtle.Turtle()
    speed_info.hideturtle()
    speed_info.penup()
    speed_info.goto(450, 360)
    speed_info.color("white")
    speed_info.write("Speed Controls:\n↑ Up: Increase\n↓ Down: Decrease", 
                     font=("Arial", 10, "bold"))

def update_ui(gen, best_fitness, best_lap, checkpoints):
    ui_generation.clear()
    ui_generation.write(f"Generation: {gen}", font=("Arial", 16, "bold"))
    
    ui_stats.clear()
    stats_text = f"\nBest Fitness: {best_fitness:.0f}\n"
    stats_text += f"\nCheckpoints: {checkpoints}/8\n"
    if best_lap < float('inf'):
        stats_text += f"Best Lap: {best_lap} steps"
    ui_stats.write(stats_text, font=("Arial", 12, "normal"))

def setup_speed_slider():
    slider = turtle.Turtle()
    slider.hideturtle()
    slider.penup()
    slider.goto(450, 320)
    slider.color("white")
    
    def speed_up():
        global simulation_speed
        simulation_speed = min(20, simulation_speed + 1)
        slider.clear()
        slider.write(f"Speed: {simulation_speed}x", font=("Arial", 14, "bold"))
    
    def speed_down():
        global simulation_speed
        simulation_speed = max(1, simulation_speed - 1)
        slider.clear()
        slider.write(f"Speed: {simulation_speed}x", font=("Arial", 14, "bold"))
    
    slider.write(f"Speed: {simulation_speed}x", font=("Arial", 14, "bold"))
    
    screen.onkey(speed_up, "Up")
    screen.onkey(speed_down, "Down")
    screen.listen()

def draw_track():
    track = turtle.Turtle()
    track.speed(0)
    track.hideturtle()
    track.penup()
    
    # Outer boundary
    track.goto(-400, 300)
    track.pendown()
    track.pensize(5)
    track.color("black")
    for pos in [(400, 300), (400, -300), (-400, -300), (-400, 300)]:
        track.goto(pos)
    
    # Inner boundary
    track.penup()
    track.goto(-300, 200)
    track.pendown()
    for pos in [(300, 200), (300, -200), (-300, -200), (-300, 200)]:
        track.goto(pos)
    
    # Finish line
    track.penup()
    track.goto(-400, 200)
    track.pendown()
    track.pensize(3)
    track.color("black")
    track.goto(-300, 200)
    track.penup()
    track.goto(-350, 210)
    track.write("Finish Line", font=("Arial", 8, "bold"), align="center")
    
    # Checkpoints
    track.color("yellow")
    track.pensize(2)
    
    checkpoints_pos = [
        (-100, 250, "1"), (200, 250, "2"), (340, 100, "3"), (340, -100, "4"),
        (200, -250, "5"), (-100, -250, "6"), (-340, -100, "7"), (-340, 100, "8")
    ]
    
    for x, y, label in checkpoints_pos:
        track.penup()
        track.goto(x-5, y)
        track.pendown()
        track.circle(12)
        track.write(f"  {label}", font=("Arial", 10, "bold"))

def get_gen_color(gen):
    colors = ["red", "orange", "yellow", "lime", "cyan", "blue", "purple", "magenta", "pink", "white"]
    return colors[gen % len(colors)]

class Car:
    def __init__(self, x, y, generation=0):
        self.t = turtle.Turtle()
        self.t.shape("turtle")
        self.t.penup()
        self.t.goto(x, y)
        self.t.setheading(0)
        self.t.speed(0)
        
        self.gen = generation
        self.color = get_gen_color(generation)
        self.t.color(self.color)
        
        # Enable path drawing
        self.t.pendown()
        self.t.pensize(1)
        
        self.weights = []
        for _ in range(15):
            if _ < 10:
                self.weights.append(random.uniform(0, 0.4))
            else:
                self.weights.append(random.uniform(10, 35))
        
        self.start_x = x
        self.start_y = y
        self.fitness = 0
        self.crashed = False
        
        self.distance = 0
        self.checkpoints = [False] * 8
        self.lap = False
        self.steps = 0
        
        self.max_x = x
        self.min_y = y
        self.min_x = x
        
    def cleanup(self):
        self.t.clear()
        self.t.hideturtle()
        
    def reset(self):
        self.t.clear()
        self.t.showturtle()
        self.t.penup()
        self.t.goto(self.start_x, self.start_y)
        self.t.setheading(0)
        self.t.color(self.color)
        self.t.pendown()
        
        self.fitness = 0
        self.crashed = False
        self.distance = 0
        self.checkpoints = [False] * 8
        self.lap = False
        self.steps = 0
        
        self.max_x = self.start_x
        self.min_y = self.start_y
        self.min_x = self.start_x
    
    def get_sensors(self):
        sensors = []
        x = self.t.xcor()
        y = self.t.ycor()
        heading = self.t.heading()
        
        for angle_offset in [-90, -45, 0, 45, 90]:
            angle = heading + angle_offset
            dist = self.check_distance(x, y, angle)
            sensors.append(dist)
        
        return sensors
    
    def check_distance(self, x, y, angle):
        test_x = x
        test_y = y
        distance = 0
        
        while distance < 150:
            test_x += math.cos(math.radians(angle)) * 5
            test_y += math.sin(math.radians(angle)) * 5
            distance += 5
            
            if test_x > 395 or test_x < -395 or test_y > 295 or test_y < -295:
                return distance
            
            if -295 < test_x < 295 and -195 < test_y < 195:
                return distance
            
            if not all(self.checkpoints):
                if -400 < test_x < -300 and 195 < test_y < 205:
                    return distance
        
        return 150
        
    def move(self):
        if self.crashed or self.lap:
            return
            
        old_x = self.t.xcor()
        old_y = self.t.ycor()
        
        sensors = self.get_sensors()
        
        turn_left_total = 0
        turn_right_total = 0
        turn_angle_total = 0
        sensor_count = 0
        
        for i, sensor_dist in enumerate(sensors):
            if sensor_dist < 80:
                turn_left_total += self.weights[i]
                turn_right_total += self.weights[i + 5]
                turn_angle_total += self.weights[i + 10]
                sensor_count += 1
        
        exploration_rate = 0.15
        
        if random.random() < exploration_rate:
            rand = random.random()
            if rand < 0.33:
                self.t.left(random.uniform(5, 25))
            elif rand < 0.66:
                self.t.right(random.uniform(5, 25))
        elif sensor_count > 0:
            turn_angle_total /= sensor_count
            
            rand = random.random()
            total_turn_prob = turn_left_total + turn_right_total
            
            if total_turn_prob > 0:
                if rand < turn_left_total / (turn_left_total + turn_right_total):
                    self.t.left(random.uniform(5, turn_angle_total))
                else:
                    self.t.right(random.uniform(5, turn_angle_total))
        else:
            base_exploration = random.random()
            if base_exploration < self.weights[2]:
                self.t.left(random.uniform(2, 15))
            elif base_exploration < self.weights[2] + self.weights[7]:
                self.t.right(random.uniform(2, 15))
        
        self.t.forward(3)
        
        new_x = self.t.xcor()
        new_y = self.t.ycor()
        
        self.max_x = max(self.max_x, new_x)
        self.min_y = min(self.min_y, new_y)
        self.min_x = min(self.min_x, new_x)
        
        self.distance += math.sqrt((new_x - old_x)**2 + (new_y - old_y)**2)
        self.steps += 1
        
        x, y = new_x, new_y
        
        if not self.checkpoints[0] and -150 < x < -50 and 220 < y < 280:
            self.checkpoints[0] = True
        elif not self.checkpoints[1] and self.checkpoints[0] and 150 < x < 250 and 220 < y < 280:
            self.checkpoints[1] = True
        elif not self.checkpoints[2] and self.checkpoints[1] and 310 < x < 370 and 50 < y < 150:
            self.checkpoints[2] = True
        elif not self.checkpoints[3] and self.checkpoints[2] and 310 < x < 370 and -150 < y < -50:
            self.checkpoints[3] = True
        elif not self.checkpoints[4] and self.checkpoints[3] and 150 < x < 250 and -280 < y < -220:
            self.checkpoints[4] = True
        elif not self.checkpoints[5] and self.checkpoints[4] and -150 < x < -50 and -280 < y < -220:
            self.checkpoints[5] = True
        elif not self.checkpoints[6] and self.checkpoints[5] and -370 < x < -310 and -150 < y < -50:
            self.checkpoints[6] = True
        elif not self.checkpoints[7] and self.checkpoints[6] and -370 < x < -310 and 50 < y < 150:
            self.checkpoints[7] = True
            
    def check_crash(self):
        x = self.t.xcor()
        y = self.t.ycor()
        
        if -400 < x < -300 and 195 < y < 205:
            if all(self.checkpoints) and not self.lap:
                self.lap = True
                self.crashed = False
                self.t.color("gold")
                self.t.shape("circle")
                print(f"🏁 Gen {self.gen} completed lap in {self.steps} steps!")
                return False
            elif not all(self.checkpoints):
                self.crashed = True
                self.t.color("gray")
                return True
        
        if x > 395 or x < -395 or y > 295 or y < -295:
            self.crashed = True
            self.t.color("gray")
            return True
            
        if -295 < x < 295 and -195 < y < 195:
            self.crashed = True
            self.t.color("gray")
            return True
            
        return False
    
    def calc_fitness(self):
        fitness = self.distance * 4
        
        fitness += max(0, (self.max_x - self.start_x) * 6)
        
        if self.max_x > 150:
            fitness += max(0, (self.start_y - self.min_y) * 6)
        
        if self.min_y < -100:
            fitness += max(0, (self.max_x - self.min_x) * 6)
        
        if not all(self.checkpoints) and self.min_y < 200:
            penalty = (200 - self.min_y) * 50
            fitness -= penalty
        
        checkpoint_values = [1500, 3000, 5000, 7500, 10500, 14000, 18000, 23000]
        for i, passed in enumerate(self.checkpoints):
            if passed:
                fitness += checkpoint_values[i]
        
        if self.lap:
            fitness += 100000
            time_bonus = max(0, 20000 - self.steps * 5)
            fitness += time_bonus
        
        self.fitness = max(0, fitness)
        return self.fitness

class Evolution:
    # DNA file in the race folder
    DNA_FILE = os.path.join(os.path.dirname(__file__), "best_dna.txt")
    
    def __init__(self, pop_size):
        self.pop_size = pop_size
        self.gen = 0
        self.cars = []
        self.best_fitness_ever = 0
        self.best_lap_time = float('inf')
        
        print(f"📁 DNA file location: {self.DNA_FILE}")
        
        # Try to load DNA from file
        best_dna = self.load_dna()
        
        for i in range(pop_size):
            y_offset = (i - pop_size//2) * 8
            car = Car(-350, 250 + y_offset, self.gen)
            
            # If we have saved DNA, use it for first car and mutate for others
            if best_dna is not None:
                if i == 0:
                    car.weights = best_dna.copy()
                else:
                    car.weights = best_dna.copy()
                    # Add mutations to create diversity
                    for j in range(len(car.weights)):
                        if random.random() < 0.5:
                            if j < 10:
                                car.weights[j] += random.uniform(-0.1, 0.1)
                                car.weights[j] = max(0, min(0.4, car.weights[j]))
                            else:
                                car.weights[j] += random.uniform(-8, 8)
                                car.weights[j] = max(10, min(35, car.weights[j]))
            
            self.cars.append(car)
        
        if best_dna is not None:
            print("✅ Loaded previous best DNA from file!")
        else:
            print("🆕 Starting fresh - no previous DNA found")
    
    def load_dna(self):
        """Load DNA from file if it exists"""
        if not os.path.exists(self.DNA_FILE):
            return None
        
        try:
            with open(self.DNA_FILE, 'r') as f:
                lines = f.readlines()
                if len(lines) < 2:
                    return None
                
                # Read metadata
                metadata = lines[0].strip().split(',')
                self.best_fitness_ever = float(metadata[0])
                if len(metadata) > 1 and metadata[1] != 'inf':
                    self.best_lap_time = int(metadata[1])
                
                # Read DNA weights
                dna = [float(x) for x in lines[1].strip().split(',')]
                if len(dna) == 15:
                    return dna
        except Exception as e:
            print(f"⚠️ Error loading DNA: {e}")
        
        return None
    
    def save_dna(self, car):
        """Save best DNA to file"""
        try:
            with open(self.DNA_FILE, 'w') as f:
                # Save metadata: fitness, lap_time
                lap_str = str(self.best_lap_time) if self.best_lap_time < float('inf') else 'inf'
                f.write(f"{self.best_fitness_ever},{lap_str}\n")
                
                # Save DNA weights
                dna_str = ','.join(str(w) for w in car.weights)
                f.write(dna_str + '\n')
            
            print(f"💾 Saved DNA to {self.DNA_FILE}")
        except Exception as e:
            print(f"⚠️ Error saving DNA: {e}")
    
    def run_generation(self):
        print(f"\n{'='*50}")
        print(f"Generation {self.gen}")
        print(f"{'='*50}")
        
        for car in self.cars:
            car.reset()
        
        for step in range(2000):
            for car in self.cars:
                if not car.crashed and not car.lap:
                    car.move()
                    car.check_crash()
            
            if step % max(1, simulation_speed) == 0:
                screen.update()
        
        for car in self.cars:
            car.calc_fitness()
        
        self.cars.sort(key=lambda c: c.fitness, reverse=True)
        
        best = self.cars[0]
        checkpoints_passed = sum(best.checkpoints)
        
        # Track and save best
        should_save = False
        
        if best.fitness > self.best_fitness_ever:
            self.best_fitness_ever = best.fitness
            should_save = True
            print(f"🌟 NEW BEST FITNESS! 🌟")
        
        if best.lap and best.steps < self.best_lap_time:
            self.best_lap_time = best.steps
            should_save = True
            print(f"⚡ NEW FASTEST LAP! ⚡")
        
        if should_save:
            self.save_dna(best)
        
        # Update UI
        update_ui(self.gen, self.best_fitness_ever, self.best_lap_time, checkpoints_passed)
        
        print(f"\n\nBest fitness: {best.fitness:.0f} (Record: {self.best_fitness_ever:.0f})")
        print(f"\nCheckpoints: {checkpoints_passed}/8")
        if best.lap:
            print(f"\n✅ BEST LAP THIS GEN: {best.steps} steps")
            print(f"\n🏆 FASTEST LAP EVER: {self.best_lap_time} steps")
        elif self.best_lap_time < float('inf'):
            print(f"\n🏆 FASTEST LAP EVER: {self.best_lap_time} steps")
        
        print(f"DNA (L=left prob, R=right prob):")
        sensors = ["Left", "F-Left", "Front", "F-Right", "Right"]
        for i in range(5):
            print(f"  {sensors[i]}: L={best.weights[i]:.2f}, R={best.weights[i+5]:.2f}, A={best.weights[i+10]:.0f}°")
        
    def evolve(self):
        for car in self.cars:
            car.cleanup()
        
        survivors = max(3, int(self.pop_size * 0.25))
        new_pop = []
        
        self.gen += 1
        
        for i in range(min(3, survivors)):
            elite = Car(self.cars[i].start_x, self.cars[i].start_y, self.gen)
            elite.weights = self.cars[i].weights.copy()
            new_pop.append(elite)
        
        while len(new_pop) < self.pop_size:
            p1 = self.tournament_select(survivors)
            p2 = self.tournament_select(survivors)
            
            child = Car(p1.start_x, p1.start_y, self.gen)
            
            for i in range(len(child.weights)):
                if random.random() < 0.5:
                    child.weights[i] = p1.weights[i]
                else:
                    child.weights[i] = p2.weights[i]
            
            for i in range(len(child.weights)):
                if random.random() < 0.3:
                    if i < 10:
                        child.weights[i] += random.uniform(-0.08, 0.08)
                        child.weights[i] = max(0, min(0.4, child.weights[i]))
                    else:
                        child.weights[i] += random.uniform(-6, 6)
                        child.weights[i] = max(10, min(35, child.weights[i]))
            
            new_pop.append(child)
        
        self.cars = new_pop
    
    def tournament_select(self, survivors):
        contestants = random.sample(self.cars[:survivors], min(3, survivors))
        return max(contestants, key=lambda c: c.fitness)

def main():
    draw_track()
    setup_ui()
    setup_speed_slider()
    
    evo = Evolution(20)
    
    try:
        for _ in range(500):
            evo.run_generation()
            evo.evolve()
            # Removed time.sleep - no delay between generations
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    print("\nEvolution complete!")

if __name__ == "__main__":
    main()
    screen.exitonclick()