from collections import deque


def sort_tuples(tuples_array, matrix):
    tuples_list = [(coordinate, matrix[coordinate[0]][coordinate[1]]) for coordinate in tuples_array]
    list_ordered_tuples = sorted(tuples_list, key = lambda x: x[1])
    return [tupla[0] for tupla in list_ordered_tuples]


def dfs(graph, current, visited):
    if graph[current][2] == 1 and graph[current][1] == True:
        return True
    
    routes = graph[current][0]
    visited.append(current)
    for route in routes:
        if route not in visited and graph[route][1] != False:
            visited.append(route)
            partial_route = dfs(graph, route, visited)
            if partial_route is True:
                return partial_route
    
    return False


def who_is_tapping_me(original_matrix, weighted_matrix, parkings_coordinates):
    dictionary = {}
    for parking in parkings_coordinates:
        if weighted_matrix[parking[0]][parking[1]] == 1:
            dictionary[parking] = ([], True, 1)
            continue

        visiteds = []
        travel_queue = deque()
        dictionary[parking] = ([], True, weighted_matrix[parking[0]][parking[1]])
        visiteds.append(parking)
        following = adjacents(parking, len(weighted_matrix), len(weighted_matrix[0]))
        for element in following:
            travel_queue.append(element)
        
        while len(travel_queue) > 0:
            current = travel_queue.pop()                    
            if original_matrix[current[0]][current[1]] == -1 and weighted_matrix[current[0]][current[1]] > 0:
                following = adjacents(current, len(weighted_matrix), len(weighted_matrix[0]))
                visiteds.append(current)
                for element in following:
                    if element not in visiteds and element not in travel_queue:
                        travel_queue.append(element)

            if original_matrix[current[0]][current[1]] not in (0, -1, 127, 128) and current not in visiteds:
                aux = dictionary[parking]
                arr = aux[0]
                grade = aux[2]
                arr.append((current[0], current[1]))
                dictionary[parking] = (arr, aux[1], grade)
                visiteds.append(current)
        
        sorted = sort_tuples(dictionary[parking][0], weighted_matrix) 
        tmp = dictionary[parking][2]
        dictionary[parking] = (sorted, True, tmp)

    return dictionary


def adjacents(coordinates, row_max, column_max):
    mov_columns = [-1, 0, 1, 0]
    mov_rows = [0, 1, 0, -1]
    neighbors = []
    coordinate_x, coordinate_y = coordinates
    for i in range(4):
        adj_x = coordinate_x + mov_columns[i]
        adj_y = coordinate_y + mov_rows[i]
        if 0 <= adj_x < row_max and 0 <= adj_y < column_max:
            neighbors.append((adj_x, adj_y))

    return neighbors


def weight_matrix(weighted_matrix, landing_spaces):
    available = 0
    parkings = []
    processed_coordinates = deque(landing_spaces)

    while processed_coordinates:
        coordinates = processed_coordinates.popleft()
        neighbors = adjacents(coordinates, len(weighted_matrix), len(weighted_matrix[0]))
        for neighbor in neighbors:
            if weighted_matrix[neighbor[0]][neighbor[1]] == -1:
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]]
                processed_coordinates.appendleft((neighbor[0], neighbor[1]))
            elif weighted_matrix[neighbor[0]][neighbor[1]] == 128:
                parkings.append((neighbor[0], neighbor[1]))
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]] + 1
                available += 1
                processed_coordinates.append((neighbor[0], neighbor[1]))

    return (weighted_matrix, parkings)  


def backtracking(graph, original_matrix, events, parking_info, parkings):
    if len(events) == 0:
        return True
        
    event = events.popleft()
    if event < 0:
        parked_airplane = abs(event)
        coordinate = parking_info[parked_airplane][0]
        if graph[coordinate][2]== 1:
            aux = graph[coordinate][0]
            tmp = graph[coordinate][2]
            graph[coordinate] = (aux, True, tmp)
            partial_solution = backtracking(graph, original_matrix, events, parking_info, parkings)
            if partial_solution:
                return True
            else:
                aux = graph[coordinate][0]
                tmp = graph[coordinate][2]
                graph[coordinate] = (aux, False, tmp)
                events.appendleft(event)
                return False
        
        visited = []
        flag = dfs(graph, coordinate, visited)
        if flag:
            aux = graph[coordinate][0]
            tmp = graph[coordinate][2]
            graph[coordinate] = (aux, True, tmp)
            partial_solution = backtracking(graph, original_matrix, events, parking_info, parkings)
            if partial_solution:
                return True
            
        aux = graph[coordinate][0]
        tmp = graph[coordinate][2]
        graph[coordinate] = (aux, False, tmp)
        events.appendleft(event)
        return False

    else:
        for parking in parkings:
            if graph[parking][1] is not False:
                visited = []
                flag = dfs(graph, parking, visited)
                if flag:
                    parking_info[event] = (parking, original_matrix[parking[0]][parking[1]])
                    aux = graph[parking][0]
                    tmp = graph[parking][2]
                    graph[parking] = (aux, False, tmp)
                    partial_solution = backtracking(graph, original_matrix, events, parking_info, parkings)
                    if partial_solution:
                        return True
                    else:
                        aux = graph[parking][0]
                        tmp = graph[parking][2]
                        graph[parking] = (aux, True, tmp)
                        del(parking_info[event])

        events.appendleft(event)
        return False


def main():
    n = 1
    while n < 22:
        first_line = input().split()
        if len(first_line) < 3:
            break

        rows = int(first_line[1])
        colums = int(first_line[2])
        original_matrix, weighted_original_matrix = []*colums, []*colums
        landing_spaces = deque()
        for i in range(rows):
            row_original, row_weighted = []*rows, []*rows
            j = 0
            for element in input().split():
                if element == '..':
                    row_original.append(-1)
                    row_weighted.append(-1)
                elif element == '==':
                    landing_spaces.appendleft((i, j))
                    row_weighted.append(0)
                    row_original.append(0)
                elif element == '##':
                    row_weighted.append(127)
                    row_original.append(127)
                else:
                    row_weighted.append(128)
                    row_original.append(int(element))
                j += 1

            original_matrix.append(row_original)
            weighted_original_matrix.append(row_weighted)

        events = deque(map(int, input().split()))
        parking_info = {}
        weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
        graph = who_is_tapping_me(original_matrix, weighted_matrix, parkings)
        solution = backtracking(graph, original_matrix, events, parking_info, parkings)
        if solution == False:
            print(f'Case {n}: No')
            print('\n')
        else:
            print(f'Case {n}: Yes')
            i = 1
            while i <= len(parking_info):
                assigned_parking = str(parking_info[i][1])
                if len(assigned_parking) == 1:
                    assigned_parking = '0' + assigned_parking

                print(assigned_parking, end=' ')
                i += 1

            print('\n')

        n += 1
        

if __name__ == '__main__':
    main()