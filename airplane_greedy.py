from collections import deque

# Evita que al recorrer los vecinos de una casilla cualquiera en la matriz se salga de esta. 
# Tiene como paramétros las coordenadas (tupla) de la casilla que quiero validar si se encuentra en el rango o no, y las dimensiones máximas de la matriz
# Retorna True en caso de que la coordenada no exceda las dimensiones de la matriz
def isValid(coordinates, row_max, column_max):
    return 0 <= coordinates[0] < row_max and 0 <= coordinates[1] < column_max 

# Ayuda a encontrar las casillas adyacentes a una casilla (en coordenadas) dada
# Sus parametros son las coordenadas de una casilla (tupla) y la matriz ponderada
# Retorna un arreglo donde están todos los vecinos válidos (que respeten los límites de la matriz y no sean bloqueos) a una coordenada
def adjacents(coordinates, weighted_matrix):
    mov_columns = [-1, 0, 1, 0]
    mov_rows = [0, 1, 0, -1]

    neighbors = []
    coordinate_x, coordinate_y = coordinates

    for i in range(4):
        adj_x = coordinate_x + mov_columns[i]
        adj_y = coordinate_y + mov_rows[i]
        if isValid((adj_x, adj_y), len(weighted_matrix), len(weighted_matrix[0])) and weighted_matrix[adj_x][adj_y] != 127:
            neighbors.append((adj_x, adj_y))

    return neighbors

#Se encarga de devolver la matriz ponderada. Recibe la matriz que fue ponderada originalmente y un deque en el que se almacenan las coordenadas de los lugares de aterrizaje y despegue
def weight_matrix(original_weighted_matrix, landing_spaces):
    weighted_matrix = [row[:] for row in original_weighted_matrix]
    parkings = []
    processed_coordinates = deque(landing_spaces)

    while processed_coordinates:
        coordinates = processed_coordinates.popleft()
        neighbors = adjacents(coordinates, weighted_matrix)
        for neighbor in neighbors:
            if weighted_matrix[neighbor[0]][neighbor[1]] == -1:
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]]
                processed_coordinates.appendleft((neighbor[0], neighbor[1]))
            elif weighted_matrix[neighbor[0]][neighbor[1]] == 128:
                parkings.append((neighbor[0], neighbor[1]))
                weighted_matrix[neighbor[0]][neighbor[1]] = weighted_matrix[coordinates[0]][coordinates[1]] + 1
                processed_coordinates.append((neighbor[0], neighbor[1]))

    return (weighted_matrix , parkings[::-1])

# Se encarga de parquear el evento en la casilla (parqueadero) correspondiente
def parking(parkings, parking_info, weighted_original_matrix, event, original_matrix):
    parking = parkings.pop(0);
    i, j = parking
    parking_info[event] = ((i, j), original_matrix[i][j])
    weighted_original_matrix[i][j] = 127

# Se encarga de sacar el evento, en caso de que no pueda, retorna False para que el evento sea guardado en lista de espera
def taking_off(coordinates, weighted_matrix, parking_info, weighted_original_matrix, original_matrix, event):
    neighbor_available = adjacents(coordinates, weighted_matrix)
    if neighbor_available:
        original_matrix[coordinates[0]][coordinates[1]] = parking_info[abs(event)][1]
        weighted_original_matrix[coordinates[0]][coordinates[1]] = 128
        return True
    return False

# Recorre la lista de eventos, procesa el evento según sea el caso. Si uno de estos eventos no pudo ser procesado, simplemente lo almacena en una nueva lista, para que en el momento en que pueda procesar el evento lo haga con éxito
def greedy(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, landing_spaces, new_order):
    if not parkings or not landing_spaces:
        return False

    wait_list = []

    while len(events) > 0 or len(wait_list) > 0:
        if len(events) > 0:
            event = events.popleft()
            if event < 0:
                if abs(event) in parking_info.keys() and taking_off(parking_info[abs(event)][0], weighted_matrix, parking_info, weighted_original_matrix, original_matrix, event):
                    weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
                    new_order.append(event)
                else:
                    wait_list.append(event)
            else:
                if len(parkings) > 0:
                    parking(parkings, parking_info, weighted_original_matrix, event, original_matrix)
                    weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
                    new_order.append(event)
                else:
                    wait_list.append(event)
        
        if len(wait_list) > 0:
            for event in wait_list:
                if event < 0:
                    if abs(event) in parking_info.keys() and taking_off(parking_info[abs(event)][0], weighted_matrix, parking_info, weighted_original_matrix, original_matrix, event):
                        weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
                        wait_list.remove(event)
                        new_order.append(event)
                else:
                    if len(parkings) > 0:
                        parking(parkings, parking_info, weighted_original_matrix, event, original_matrix)
                        weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
                        wait_list.remove(event)
                        new_order.append(event)

# Se encarga de leer el input, hacer la primera limpieza de la matriz y llamar a las funciones que en conjunto entregan una solución
def main():
    n = 1
    while n < 22:
        first_line = input().split()
        
        if len(first_line) < 3:
            break

        rows = int(first_line[1])
        original_matrix, weighted_original_matrix = [], []
        landing_spaces = deque()

        for i in range(rows):
            row_original, row_weighted = [], []
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

        parking_info, new_order = {}, []
        weighted_matrix, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
        solution = greedy(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, landing_spaces, new_order)

        if solution == False:
            print(f'Case {n}: No')
        else:
            print(f'Case {n}: Yes')
            print('\nThe final list of events was:')
            for element in new_order:
                if element > 0:
                    print('+' + str(element), end=' ')
                else:
                    print(element, end=' ')
            print('\nThe parking order was:')
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