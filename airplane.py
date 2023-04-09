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
    available = 0
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
                available += 1
                processed_coordinates.append((neighbor[0], neighbor[1]))

    return (weighted_matrix, available, parkings)

#Se le pasa una coordenada, y cuando alguno de los cuatro posibles vecinos sea valido, inmediatamente retorna verdadero y no valida los otros
def taking_off(coordinates, weighted_matrix):
    mov_columns = [-1, 0, 1, 0]
    mov_rows = [0, 1, 0, -1]
    coordinate_x, coordinate_y = coordinates

    for i in range(4):
        adj_x = coordinate_x + mov_columns[i]
        adj_y = coordinate_y + mov_rows[i]
        if isValid((adj_x, adj_y), len(weighted_matrix), len(weighted_matrix[0])) and weighted_matrix[adj_x][adj_y] not in (127, -1, 128):
            return True

    return False

# En caso de que exista solución la encuentra y retorna un arreglo lleno de parqueaderos, cada uno corresponde a un avión (en orden de llegada)
# En caso de que la solución no exista retorna falso
# Como parametros recibe la matriz ponderada, la matriz original, la lista de eventos (entradas y salidas), un arreglo donde va ir almacenando cada parqueadero y un diccionario, donde el Key corresponde a un avión parqueado y en sus Values tiene 1) Las coordenadas de donde se parqueó el avión y 2) El peso que tenía esa coordenada antes de ser ocupada
def backtracking(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, available, landing_spaces):
    if len(events) == 0:
        return True
    
    copia = events.copy()
    landings = 0
    evento = copia.popleft()

    while evento > 0:
        landings += 1
        evento = copia.popleft()
    
    if available < landings:
        return False
        
    event = events.popleft()

    if event < 0:
        parked_airplane = abs(event)
        coordinate_i, coordinate_j = parking_info[parked_airplane][0]
        neighbor_available = taking_off((coordinate_i, coordinate_j), weighted_matrix)
        if neighbor_available:
            original_matrix[coordinate_i][coordinate_j] = parking_info[abs(event)][1]
            weighted_original_matrix[coordinate_i][coordinate_j] = 128
            weighted_matrix, available, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
            partial_solution = backtracking(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, available, landing_spaces)
            if partial_solution:
                return True
        weighted_original_matrix[coordinate_i][coordinate_j] = 127
        weighted_matrix, available, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
        events.appendleft(event)
        return False

    else:
        for parking in parkings:
            i, j = parking
            temp = original_matrix[i][j]
            parking_info[event] = ((i, j), original_matrix[i][j])
            weighted_original_matrix[i][j] = 127
            weighted_matrix, available, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
            partial_solution = backtracking(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, available, landing_spaces)
            if partial_solution:
                return True
            else:
                original_matrix[i][j] = temp
                weighted_original_matrix[i][j] = 128
                weighted_matrix, available, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
                del(parking_info[event])
        events.appendleft(event)
        return False

# Se encarga de leer el input, hacer la primera limpieza de la matriz y llamar a las funciones que en conjunto entregan una solución
def main():
    n = 1
    while n < 2:
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

        parking_info = {}
        weighted_matrix, available, parkings = weight_matrix(weighted_original_matrix, landing_spaces)
        solution = backtracking(weighted_original_matrix, weighted_matrix, original_matrix, events, parking_info, parkings, available, landing_spaces)

        if solution == False:
            print(f'Case {n}: No')
            print('\n')
        else:
            print(f'Case {n}: Yes')
            i=1
            while i<= len(parking_info):
                assigned_parking = str(parking_info[i][1])
                if len(assigned_parking) == 1:
                    assigned_parking = '0' + assigned_parking
                print(assigned_parking, end=' ')
                i+=1
            print('\n')

        n += 1


if __name__ == '__main__':
    main()