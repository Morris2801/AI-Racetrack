import turtle
import random

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

class Route:
  def __init__(self, start_point, end_point):
    self.start_point = start_point
    self.end_point = end_point

class Turtle:
  def __init__(self, route):
    self.route = route
    self.x = 0
    self.y = 0

    self.heading = random.randint(0, 360)

  def move(self):
    self.x = turtle.xcor()
    self.y = turtle.ycor()
    turtle.setheading(self.heading)
    turtle.forward(10)
    if self.x < self.route.start_point.x or self.x > self.route.end_point.x or self.y < self.route.start_point.y or self.y > self.route.end_point.y:
      #return to start
      self.x = 150
      self.y = 37.5
      turtle.goto(self.x, self.y)

def generate_route():
  width = 100
  height = 50

  # Start and end points of inner rectangle
  start_point = Point(75, 75)
  end_point = Point(225, 225)

  return Route(start_point, end_point)

def draw_racetrack():
  # Size of the largest rectangle
  width = 300
  height = 300

  # Size of the inner rectangle
  inner_width = 150
  inner_height = 150

  start_x = 150
  start_y = 37.5

    # outer rect
  turtle.forward(width)
  turtle.left(90)
  turtle.forward(height)
  turtle.left(90)
  turtle.forward(width)
  turtle.left(90)
  turtle.forward(height)
  turtle.left(90)

    # inner rect
  turtle.penup()
  turtle.goto(75, 75)
  turtle.pendown()
  turtle.forward(inner_width)
  turtle.left(90)
  turtle.forward(inner_height)
  turtle.left(90)
  turtle.forward(inner_width)
  turtle.left(90)
  turtle.forward(inner_height)
  turtle.left(90)
  turtle.penup()

  turtle.goto(start_x,start_y)

def test_route(route):
  time = 0

  t = Turtle(route)

  # Move 
  while t.x != route.end_point.x or t.y != route.end_point.y:
    t.move()
    time += 1

  return time

def main():
  turtle.setup(600, 600)

  draw_racetrack()

  route = generate_route()

  turtle.pendown()
  time = test_route(route)
  print(f'Time to complete the route: {time}')

main()
