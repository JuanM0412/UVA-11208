from collections import deque


def sort_tuples(tuples_array, matrix):
    # Creamos una lista de tuplas, donde cada tupla contiene la coordenada y el valor correspondiente en la matriz.
    tuples_list = [(coordinate, matrix[coordinate[0]][coordinate[1]]) for coordinate in tuples_array]
    # Ordenamos la lista de tuplas según el valor correspondiente en la matriz.
    list_ordered_tuples = sorted(tuples_list, key = lambda x: x[1])
    # Devolvemos un arreglo de tuplas ordenado.
    return [tupla[0] for tupla in list_ordered_tuples]


def dfs(graph, weighted_matrix, current, visited):
    if weighted_matrix[current[0]][current[1]] == 1 and graph[current][1] == True:
        return True
    
    routes = graph[current][0]
    visited.add(current)
    for route in routes:
        if route not in visited and graph[route][1] != False:
            visited.add(route)
            partial_route = dfs(graph, weighted_matrix, route, visited)
            if partial_route is True:
                return True
    
    return False


def who_is_tapping_me(original_matrix, weighted_matrix, parkings_coordinates):
    dictionary = {}
    for parking in parkings_coordinates:
        dictionary[parking] = ([], True)
        if weighted_matrix[parking[0]][parking[1]] == 1:
            continue

        visiteds = set()
        travel_queue = deque()
        visiteds.add(parking)
        following = adjacents(parking, len(weighted_matrix), len(weighted_matrix[0]))
        for element in following:
            travel_queue.append(element)
        
        while len(travel_queue) > 0:
            current = travel_queue.pop()                    
            if original_matrix[current[0]][current[1]] == -1 and weighted_matrix[current[0]][current[1]] > 0:
                following = adjacents(current, len(weighted_matrix), len(weighted_matrix[0]))
                visiteds.add(current)
                for element in following:
                    if element not in visiteds and element not in travel_queue:
                        travel_queue.append(element)

            if original_matrix[current[0]][current[1]] not in (0, -1, 127) and current not in visiteds and weighted_matrix[current[0]][current[1]] != 128:
                aux = dictionary[parking][0]
                aux.append((current[0], current[1]))
                dictionary[parking] = (aux, True)
                visiteds.add(current)
        
        sorted = sort_tuples(dictionary[parking][0], weighted_matrix) 
        dictionary[parking] = (sorted, True)   

    return dictionary


# Ayuda a encontrar las casillas adyacentes a una casilla (en coordenadas) dada
# Sus parametros son las coordenadas de una casilla (tupla) y la matriz ponderada
# Retorna un arreglo donde están todos los vecinos válidos (que respeten los límites de la matriz y no sean bloqueos) a una coordenada
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


#Se encarga de devolver la matriz ponderada. Recibe la matriz que fue ponderada originalmente y un deque en el que se almacenan las coordenadas de los lugares de aterrizaje y despegue
def weight_matrix(weighted_matrix, landing_spaces):
    available = 0
    parkings = []
    processed_coordinates = deque(landing_spaces)

    while processed_coordinates:
        coordinates = processed_coordinates.popleft()
        neighbors = adjacents(coordinates, len(weighted_matrix), len(weighted_matrix[0]))
        for neighbor in neighbors:
            if weighted_matrix[neighbor[0]][neighbor[1]] == -1 and weighted_matrix[neighbor[0]][neighbor[1]] != 127:
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]]
                processed_coordinates.appendleft((neighbor[0], neighbor[1]))
            elif weighted_matrix[neighbor[0]][neighbor[1]] == 128 and weighted_matrix[neighbor[0]][neighbor[1]] != 127:
                parkings.append((neighbor[0], neighbor[1]))
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]] + 1
                available += 1
                processed_coordinates.append((neighbor[0], neighbor[1]))

    return (weighted_matrix, parkings)  


# En caso de que exista solución la encuentra y retorna un arreglo lleno de parking, cada uno corresponde a un avión (en orden de llegada)
# En caso de que la solución no exista retorna falso
# Como parametros recibe la matriz ponderada, la matriz original, la lista de eventos (entradas y salidas), un arreglo donde va ir almacenando cada parqueadero y un diccionario, donde el Key corresponde a un avión parqueado y en sus Values tiene 1) Las coordenadas de donde se parqueó el avión y 2) El peso que tenía esa coordenada antes de ser ocupada
def backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings):
    if len(events) == 0:
        return True
        
    event = events.popleft()
    if event < 0:
        parked_airplane = abs(event)
        coordinate = parking_info[parked_airplane][0]
        if weighted_matrix[coordinate[0]][coordinate[1]] == 1:
            aux = graph[coordinate][0]
            graph[coordinate] = (aux, True)
            partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings)
            if partial_solution:
                return True
            else:
                aux = graph[coordinate][0]
                graph[coordinate] = (aux, False)
                events.appendleft(event)
                return False
        
        visited = set()
        flag = dfs(graph, weighted_matrix, coordinate, visited)
        if flag:
            aux = graph[coordinate][0]
            graph[coordinate] = (aux, True)
            partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings)
            if partial_solution:
                return True
            
        aux = graph[coordinate][0]
        graph[coordinate] = (aux, False)
        events.appendleft(event)
        return False

    else:
        for parking in parkings:
            if graph[parking][1] is not False:
                visited = set()
                flag = dfs(graph, weighted_matrix, parking, visited)
                if flag:
                    parking_info[event] = (parking, original_matrix[parking[0]][parking[1]])
                    aux = graph[parking][0]
                    graph[parking] = (aux, False)
                    partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings)
                    if partial_solution:
                        return True
                    else:
                        aux = graph[parking][0]
                        graph[parking] = (aux, True)
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
        original_matrix, weighted_matrix = []*colums, []*colums
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
            weighted_matrix.append(row_weighted)

        events = deque(map(int, input().split()))
        parking_info = {}
        weighted_matrix, parkings = weight_matrix(weighted_matrix, landing_spaces)
        graph = who_is_tapping_me(original_matrix, weighted_matrix, parkings)
        solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings)
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