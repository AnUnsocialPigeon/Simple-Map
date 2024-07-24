import argparse
import random
from typing import List
from PIL import Image

width = 100
height = 100
destinations = 3
difficulty = 1
toFile = False
grid = False
show = True
points = []

def parseArgs() -> bool:
    """Handles arg parsing"""
    global width, height, destinations, difficulty, toFile, grid, show

    # Get the args
    parser = argparse.ArgumentParser(description="A mathematical problem generator")
    parser.add_argument('-x', type=int, default=100, help='The width of the map')
    parser.add_argument('-y', type=int, default=100, help='The height of the map')
    parser.add_argument('--destinations', type=int, default=3, help='The amount of destinations to generate')
    parser.add_argument('--difficulty', type=int, default=1, help='The challenge difficulty')
    parser.add_argument('--toFile', action='store_true', help='When set, will output to a file (output.txt)')
    parser.add_argument('--grid', action='store_true', help="When set, will make the map use grid-generation")
    parser.add_argument('--noShow', action='store_true', help="When set, will disable default image pop-up")

    # Parse out
    args = parser.parse_args()
    width = min(args.x, 2000)
    height = min(args.y, 2000)
    destinations = args.destinations
    difficulty = args.difficulty
    toFile = args.toFile
    grid = args.grid
    show = not args.noShow

    return width > 0 and height > 0 and difficulty <= 2 and difficulty > 0 and destinations < width * height and destinations > 1


def create_default_map() -> List[List[str]]:
    """Generates a default map"""
    return [["" for _ in range(width)] for _ in range(height)]


def generate_points() -> List[List[int]]:
    """Generates all the destination points (non-overlapping)"""
    global points
    points = []
    while len(points) < destinations:
        point = (random.randint(0, width - 1), random.randint(0, height - 1))
        if point not in points:
            points.append(point)
    return points


def generate1() -> None:
    """Generates difficulty 1"""
    map = create_default_map()
    for y in range(height):
        for x in range(width):
            if x % 2 == 1 and y % 2 == 1:
                continue
            map[y][x] += "RW"
            if x % 2 == 0 and y % 2 == 0:
                map[y][x] += "T"
    output(map)


def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])


def union(parent, rank, x, y):
    rootX = find(parent, x)
    rootY = find(parent, y)

    if rank[rootX] < rank[rootY]:
        parent[rootX] = rootY
    elif rank[rootX] > rank[rootY]:
        parent[rootY] = rootX
    else:
        parent[rootY] = rootX
        rank[rootX] += 1


def generate2() -> None:
    """Generates difficulty 2"""
    global points
    map = create_default_map()
    edges = []
    n = len(points)

    # Generate all possible edges
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]
            dist = (x1 - x2) ** 2 + (y1 - y2) ** 2  # Use squared distance to avoid yucky floating point
            edges.append((dist, i, j))

    # Kruskal's algorithm to find MST
    edges.sort()
    parent = list(range(n))
    rank = [0] * n

    mst_edges = []
    for edge in edges:
        dist, u, v = edge
        if find(parent, u) != find(parent, v):
            union(parent, rank, u, v)
            mst_edges.append((u, v))

    # Draw roads for MST
    for u, v in mst_edges:
        x1, y1 = points[u]
        x2, y2 = points[v]
        draw_road(map, x1, y1, x2, y2)

    # Add some random roads
    extra_edges = random.sample(edges, min(len(edges), len(mst_edges)))     # Divie len(mst_edges) by 2 to reduce extra road amount
    for _, u, v in extra_edges:
        x1, y1 = points[u]
        x2, y2 = points[v]
        draw_road(map, x1, y1, x2, y2)

    add_traffic_lights(map)

    output(map)


def draw_road(map: List[List[str]], x1: int, y1: int, x2: int, y2: int) -> None:
    """Draws a road between two points"""
    global grid

    if x1 == x2:
        # Vertical road
        for y in range(min(y1, y2), max(y1, y2) + 1):
            map[y][x1] = 'RW'
    elif y1 == y2:
        # Horizontal road
        for x in range(min(x1, x2), max(x1, x2) + 1):
            map[y1][x] = 'RW'
    else:
        # Staircase pattern for diagonal roads
        while x1 != x2 or y1 != y2:
            if not grid:    # Extremely lazy code lol
                if x1 != x2:
                    map[y1][x1] = 'RW'
                    if x1 < x2: x1 += 1
                    else: x1 -= 1
                if y1 != y2:
                    map[y1][x1] = 'RW'
                    if y1 < y2: y1 += 1
                    else: y1 -= 1
            else:
                if x1 != x2:
                    map[y1][x1] = 'RW'
                    if x1 < x2: x1 += 1
                    else: x1 -= 1
                elif y1 != y2:
                    map[y1][x1] = 'RW'
                    if y1 < y2: y1 += 1
                    else: y1 -= 1
        map[y2][x2] = 'RW'


def add_traffic_lights(map: List[List[str]]) -> None:
    """Add traffic lights to the map. A crude algorithm, idrc..."""
    for y in range(height):
        for x in range(width):
            if 'R' not in map[y][x]:
                continue
            if count_touching_roads(map, x, y) > 2:
                map[y][x] += 'T'


def count_touching_roads(map: List[List[str]], x: int, y: int) -> int:
    """Counts how many roads touch a specific point (x, y)"""
    touching_roads = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            if 'R' in map[ny][nx]:
                touching_roads += 1
                
    return touching_roads


def get_point_name(n: int) -> str:
    """Goes from an integer to alphabet, recursive length-ways"""
    label = ""
    while n >= 0:
        label = chr(n % 26 + 65) + label
        n = n // 26 - 1
    return label


def output(map: List[List[str]]) -> None:
    """Output either to screen or file"""
    global points

    buffer = ""
    n = 0
    for point in points:
        buffer += f"{get_point_name(n)}=({point[0]},{point[1]})\n"
        n += 1

    map.reverse()       # Reverse to move origin to bottom left
    for row in map:   
        buffer += '\n' + ','.join(row)

    generate_map_image(map, points)
    if toFile:
        with open('./output.txt', 'w') as file:
            file.write(buffer)
        print("Finished!")
        return
    for line in buffer.split('\n'):
        print(line)     # To output to buffer line at a time for line-based reading operations


def generate_map_image(map: List[List[str]], points: List[List[int]]) -> None:
    """Generate and save an image of the map"""
    map_height = len(map)
    map_width = len(map[0]) if map else 0
    cell_size = 2  # Size of each cell in pixels
    image = Image.new('RGB', (map_width * cell_size, map_height * cell_size), color='white')
    pixels = image.load()

    for y in range(map_height):
        for x in range(map_width):
            cell_value = map[y][x]
            if 'R' in cell_value or 'W' in cell_value or 'T' in cell_value:
                for i in range(cell_size):
                    for j in range(cell_size):
                        pixels[x * cell_size + i, y * cell_size + j] = (80, 75, 190)

    for (x, y) in points:
        for i in range(cell_size):
            for j in range(cell_size):
                pixels[x * cell_size + i, (map_height - 1 - y) * cell_size + j] = (223, 105, 180)

    image.save('map_image.png') 
    if show: image.show()


if __name__ == "__main__" and parseArgs():
    points = generate_points()
    if difficulty == 1:
        generate1()
    if difficulty == 2:
        generate2()
