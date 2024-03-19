"""
a_star_kshitij_abhishek.py

@breif:     This module implements A-star algorithm for finding the shortest path in a graph.
@author:    Kshitij Karnawat, Abhishekh Reddy
@date:      19th March 2024
@version:   2.0
"""

import numpy as np
import cv2 as cv
import time


class NewNode:
    """Class to represent a node in the graph
    """
    def __init__(self, coord, parent, cost_to_go, cost_to_come):
        """Initializes the node with its coordinates, parent and cost

        Args:
            coord (tuple): Coordinates of the node along with the angle
            parent (NewNode): Parent node of the current node
            cost_to_go (float): Cost to reach the current node
            cost_to_come (float): A-Star Hueristic for the current node (Eucledian Distance)
        """
        self.coord = coord
        self.parent = parent
        self.cost_to_go = cost_to_go
        self.cost_to_come = cost_to_come
        self.total_cost = cost_to_come + cost_to_go

# Reused from Previous Assignment
def create_map():
    """Generates the game map

    Returns:
        numpy array: A 2D array representing the game map
    """
    # Create map
    game_map = np.zeros((500, 1200, 3), dtype=np.uint8)
    game_map.fill(255)

    # Create obstacles
    ### Refer https://docs.opencv.org/3.4/dc/da5/tutorial_py_drawing_functions.html on how to draw Polygons

    # Define rectangle vertices
    rectange_1 = np.array([[175, 100],
                           [175, 500],
                           [100, 500],
                           [100, 100]], dtype=np.int32)

    rectangle_2 = np.array([[350, 0],
                           [350, 400],
                           [275, 400],
                           [275, 0]], dtype=np.int32)

    # Define hexagon vertices
    side_length = 150
    hexagon_center = (650, 250)
    hexagon_vertices = []
    for i in range(6):
        angle_rad = np.deg2rad(90) + np.deg2rad(60 * i)  # Angle in radians for each vertex + 90 for rotating the hexagon
        x = int(hexagon_center[0] + side_length * np.cos(angle_rad))
        y = int(hexagon_center[1] - side_length * np.sin(angle_rad))
        hexagon_vertices.append([x, y])

    hexagon = np.array(hexagon_vertices, dtype=np.int32)

    # Define arch vertices
    arch = np.array([[1100, 50],
                     [1100, 450],
                     [900, 450],
                     [900, 375],
                     [1020, 375],
                     [1020, 125],
                     [900, 125],
                     [900,50]], dtype=np.int32)

    game_map = cv.fillPoly(game_map, [rectange_1, rectangle_2, hexagon, arch], (0, 0, 0))

    game_map = cv.flip(game_map, 0)

    return game_map

# Reused from Previous Assignment
def in_obstacles(coord):
    """Checks if the given coordinates are in obstacles

    Args:
        coord (tuple): Coordinates to check

    Returns:
        bool: True if the coordinates are in obstacles, False otherwise
    """
    # Set Max and Min values for x and y
    x_max, y_max = 1200, 500
    x_min, y_min = 0, 0

    x, y = coord

    bloat = 5
    vertical_shift = 440 # needed as hexagon center is made on x = 0

    if (x < x_min + bloat) or (x > x_max - bloat) or (y < y_min + bloat) or (y > y_max - bloat):
        # print("Out of bounds")
        return True

    # Rectangle 1
    elif (x >= 100 - bloat and x <= 175 + bloat) and (y >= 100 - bloat and y <= 500):
        # print("In rectangle 1")
        return True

    # Rectangle 2
    elif (x >= 275 - bloat and x <= 350 + bloat) and (y >= 0 and y <= 400 + bloat):
        # print("In rectangle 2")
        return True

    # Hexagon
    elif (x >= 520 - bloat) and (x <= 780 + bloat) and ((x  + 1.7333 * y) <= 930 - (2 * bloat) + vertical_shift ) and ((x - 1.7333 * y) >= 370 + (2 * bloat) - vertical_shift) and ((x - 1.7333 * y) <= 930 + bloat - vertical_shift ) and ((x  + 1.7333 * y) >= 370 - bloat + vertical_shift):
        # print("In hexagon")
        return True

    # Arch
    # Divide the arch into 3 parts and check for each part

    # Part 1
    elif (x >= 1020 - bloat and x <= 1100 + bloat) and (y >= 50 + bloat and y <= 450 - bloat):
        # print("In arch part 1")
        return True

    # Part 2
    elif (x >= 900 - bloat and x <= 1100 + bloat) and (y >= 375 - bloat and y <= 450 + bloat):
        # print("In arch part 2")
        return True

    # Part 3
    elif (x >= 900 - bloat and x <= 1100 + bloat) and (y >= 50 - bloat and y <= 125 + bloat):
        # print("In arch part 3")
        return True

    # elif (x < 785 and):
        # return True

    return False


def calc_manhattan_distance(current_coord, goal_coord):
    """Calculates manhattan distance between the current and goal nodes
       for estimating cost to go

    Args:
        current_node_coord (tuple): Current node coordinate
        goal_node_coord (tuple): Goal node coordinate

    Returns:
        Float: Manhattan distance which is cost to move to the goal node
    """

    return np.linalg.norm((current_coord[0] - goal_coord[0]) - (current_coord[1], goal_coord[1]))


def move_forward(L, node, goal_coord):
    x, y, theta = node.coord

    updated_x, updated_y = (x + (L * np.cos(np.deg2rad(0))), y + (L * np.sin(np.deg2rad(0))))

    cost_to_go = calc_manhattan_distance((updated_x, updated_y), goal_coord)

    child = NewNode((int(round(updated_x, 0)), int(round(updated_y, 0)), theta), node, node.cost_to_come + L,
                               node.cost_to_come + L + cost_to_go)

    return cost_to_go, child

def small_left_turn(L, node, goal_coord):
    x, y, theta = node.coord

    updated_x, updated_y = (x + (L * np.cos(np.deg2rad(30))), y + (L * np.sin(np.deg2rad(30))))

    cost_to_go = calc_manhattan_distance((updated_x, updated_y), goal_coord)

    child = NewNode((int(round(updated_x, 0)), int(round(updated_y, 0)), theta), node, node.cost_to_come + L,
                               node.cost_to_come + L + cost_to_go)

    return cost_to_go, child

def small_right_turn(L, node, goal_coord):
    x, y, theta = node.coord

    updated_x, updated_y = (x + (L * np.cos(np.deg2rad(-30))), y + (L * np.sin(np.deg2rad(-30))))

    cost_to_go = calc_manhattan_distance((updated_x, updated_y), goal_coord)

    child = NewNode((int(round(updated_x, 0)), int(round(updated_y, 0)), theta), node, node.cost_to_come + L,
                               node.cost_to_come + L + cost_to_go)

    return cost_to_go, child

def big_left_turn(L, node, goal_coord):
    x, y, theta = node.coord

    updated_x, updated_y = (x + (L * np.cos(np.deg2rad(60))), y + (L * np.sin(np.deg2rad(60))))

    cost_to_go = calc_manhattan_distance((updated_x, updated_y), goal_coord)

    child = NewNode((int(round(updated_x, 0)), int(round(updated_y, 0)), theta), node, node.cost_to_come + L,
                               node.cost_to_come + L + cost_to_go)

    return cost_to_go, child

def big_right_turn(L, node, goal_coord):
    x, y, theta = node.coord

    updated_x, updated_y = (x + (L * np.cos(np.deg2rad(-60))), y + (L * np.sin(np.deg2rad(-60))))

    cost_to_go = calc_manhattan_distance((updated_x, updated_y), goal_coord)

    child = NewNode((int(round(updated_x, 0)), int(round(updated_y, 0)), theta), node, node.cost_to_come + L,
                               node.cost_to_come + L + cost_to_go)

    return cost_to_go, child

# TODO: Modify as per the action space
def get_child_nodes(node, goal_coord):
    """Generates all possible child nodes for the given node

    Args:
        node (NewNode): Node to generate child nodes from
        goal_coord (tuple): Coordinates of the goal node

    Returns:
        list: List of child nodes and their costs
    """

    # Set Max and Min values for x and y
    x_max, y_max = 1200, 500
    x_min, y_min = 0, 0

    # Get the coordinates of the node
    x, y = node.coord

    # child nodes list
    child_nodes = []

    # Create all possible child nodes
    if x < x_max:
        child, child_cost = move_up(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if x > x_min:
        child, child_cost = move_down(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if y < y_max:
        child, child_cost = move_right(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if y > y_min:
        child, child_cost = move_left(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if x < x_max and y < y_max:
        child, child_cost = move_up_right(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if x < x_max and y > y_min:
        child, child_cost = move_up_left(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if x > x_min and y < y_max:
        child, child_cost = move_down_right(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    if x > x_min and y > y_min:
        child, child_cost = move_down_left(node, goal_coord)
        if not in_obstacles(child.coord):
            child_nodes.append((child, child_cost))
        else:
            del child

    return child_nodes


def astar(start, goal):
    """Finds the shortest path from start to goal using Dijkstra's algorithm

    Args:
        start (tuple): Start coordinates
        goal (tuple): Goal coordinates

    Returns:
        list: A list of explored nodes
        list: A list of coordinates representing the shortest path
    """
    # Initialize open and closed lists
    open_list = []
    open_list_info = {}
    closed_list = []
    closed_list_info = {}
    path = []
    explored_nodes = []

    # Create start node and add it to open list
    start_node = NewNode(start, None, calc_manhattan_distance(start, goal) ,0)
    open_list.append(start_node)
    open_list_info[start_node.coord] = start_node

    while open_list:

        # Get the node with the minimum total cost and add to closed list
        open_list.sort(key=lambda x: x[1]) # sort open list based on total cost
        node = open_list.pop(0)
        cost_to_come = node.cost_to_come
        open_list_info.pop(node.coord)
        closed_list.append(node)
        closed_list_info[node.coord] = node

        # Check if goal reached
        if node.coord == goal:
            path = backtrack_path(node)

            return explored_nodes, path

        else:
            children = get_child_nodes(node, goal)
            for child, child_cost in children:
                if child.coord in closed_list_info.keys():
                    del child
                    continue

                if child.coord in open_list_info.keys():
                    if child_cost + cost_to_come < open_list_info[child.coord].cost_to_come:
                        open_list_info[child.coord].cost_to_come = child_cost + cost_to_come
                        open_list_info[child.coord].total_cost = open_list_info[child.coord].cost_to_come + open_list_info[child.coord].cost_to_go
                        open_list_info[child.coord].parent = node
                else:
                    child.cost_to_come = child_cost + cost_to_come
                    child.total_cost = child.cost_to_come + child.cost_to_go
                    child.parent = node
                    open_list.append(child)
                    open_list_info[child.coord] = child

                    explored_nodes.append(child.coord)

    return explored_nodes, None

# Reused from Previous Assignment
def backtrack_path(goal_node):
    """Backtracking algorithm for Dijkstra's algorithm

    Args:
        goal_node (NewNode): Goal node

    Returns:
        list: A list of coordinates representing the shortest path
    """
    path = []
    parent = goal_node
    while parent!= None:
        path.append(parent.coord)
        parent = parent.parent
    return path[::-1]

# Reused from Previous Assignment
# TODO: Modify if required
def vizualize(game_map, start, goal, path, explored_nodes):
    """Vizualizes the path and explored nodes

    Args:
        game_map (numpy array): A 2D array representing the game map
        start (tuple): Start coordinates
        goal (tuple): Goal coordinates
        path (list): A list of coordinates representing the shortest path
        explored_nodes (list): A list of explored nodes
    """
    cv.circle(game_map, (start[0], game_map.shape[0] - start[1] - 1), 5, (0, 0, 255), -1)
    cv.circle(game_map, (goal[0], game_map.shape[0] - goal[1] - 1), 5, (0, 255, 0), -1)

    game_video = cv.VideoWriter('game_vizualization.avi', cv.VideoWriter_fourcc('M','J','P','G'), 60, (1200, 500))
    game_map_copy = game_map.copy()
    count = 0
    for coord in explored_nodes:
        game_map[game_map.shape[0] - coord[1] - 1, coord[0]] = [100, 255, 100]
        game_map_copy[game_map.shape[0] - coord[1] - 1, coord[0]] = [100, 255, 100]
        count += 1
        if count == 100:
            game_video.write(game_map.astype(np.uint8))
            count = 0

    for coord in path:
        # print(type(game_map))
        game_map[game_map.shape[0] - coord[1], coord[0]] = [0, 0, 0]
        game_map_copy[game_map.shape[0] - coord[1], coord[0]] = [0, 0, 0]
        game_video.write(game_map.astype(np.uint8))

    cv.circle(game_map_copy, (start[0], game_map.shape[0] - start[1] - 1), 5, (0, 0, 255), 2)
    cv.circle(game_map_copy, (goal[0], game_map.shape[0] - goal[1] - 1), 5, (0, 255, 0), 2)
    cv.imwrite('final_map.png', game_map_copy)
    game_video.release()



def main():
    game_map = create_map()

    # get start and end points from user
    start_point = (int(input("Enter x coordinate of start point: ")), int(input("Enter y coordinate of start point: ")))
    goal_point = (int(input("Enter x coordinate of goal point: ")), int(input("Enter y coordinate of goal point: ")))

    # Check if start and goal points are in obstacles
    if in_obstacles(start_point):
        print("Start point is in obstacle")
        return

    if in_obstacles(goal_point):
        print("Goal point is in obstacle")
        return

    # find shortest path
    explored_nodes, shortest_path = astar(start_point, goal_point)
    if shortest_path == None:
        print("No path found")

    # visualize path
    vizualize(game_map, start_point, goal_point, shortest_path, explored_nodes)

    # show map
    cv.imshow('Map', game_map)

    # wait for key press
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
