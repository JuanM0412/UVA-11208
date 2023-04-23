#include <algorithm>
#include <deque>
#include <iostream>
#include <map>
#include <tuple>
#include <vector>

using namespace std;

pair<vector<vector<int>>, vector<pair<int, int>>> weight_matrix(vector<vector<int>> original_weighted_matrix, deque<pair<int,int>> landing_spaces) {
    vector<vector<int>> weighted_matrix = original_weighted_matrix;
    int available = 0;
    vector<pair<int,int>> parkings;
    deque<pair<int,int>> processed_coordinates = landing_spaces;

    while (!processed_coordinates.empty()) {
        pair<int,int> coordinates = processed_coordinates.front();
        processed_coordinates.pop_front();
        vector<pair<int,int>> neighbors;
        if (coordinates.first > 0) neighbors.emplace_back(coordinates.first - 1, coordinates.second);
        if (coordinates.first < weighted_matrix.size() - 1) neighbors.emplace_back(coordinates.first + 1, coordinates.second);
        if (coordinates.second > 0) neighbors.emplace_back(coordinates.first, coordinates.second - 1);
        if (coordinates.second < weighted_matrix[0].size() - 1) neighbors.emplace_back(coordinates.first, coordinates.second + 1);

        for (auto neighbor : neighbors) {
            if (weighted_matrix[neighbor.first][neighbor.second] == -1) {
                weighted_matrix[neighbor.first][neighbor.second] = weighted_matrix[coordinates.first][coordinates.second];
                processed_coordinates.push_front(neighbor);
            }
            else if (weighted_matrix[neighbor.first][neighbor.second] == 128) {
                parkings.push_back(neighbor);
                weighted_matrix[neighbor.first][neighbor.second] = weighted_matrix[coordinates.first][coordinates.second] + 1;
                available++;
                processed_coordinates.push_back(neighbor);
            }
        }
    }

    return make_pair(weighted_matrix, parkings);
}

bool dfs(map<pair<int, int>, pair<vector<pair<int, int>>, bool>> &graph, vector<vector<int>> &weighted_matrix, pair<int, int> current, vector<pair<int, int>> &visited) {
  if (weighted_matrix[current.first][current.second] == 1 &&
      graph[current].second == true) {
    return true;
  }

  auto routes = graph[current].first;
  visited.push_back(current);

  for (auto &route : routes) {
    if (find(visited.begin(), visited.end(), route) == visited.end() && graph[route].second != false) {
      visited.push_back(route);
      bool partial_route = dfs(graph, weighted_matrix, route, visited);
      if (partial_route == true) {
        return partial_route;
      }
    }
  }

  return false;
}


bool isValid(pair<int, int> coordinates, int row_max, int column_max) {
  return (coordinates.first >= 0 && coordinates.first < row_max && coordinates.second >= 0 && coordinates.second < column_max);
}


vector<pair<int, int>> adjacents(pair<int, int> coordinates, vector<vector<int>> weighted_matrix) {
  int mov_columns[] = {-1, 0, 1, 0};
  int mov_rows[] = {0, 1, 0, -1};
  vector<pair<int, int>> neighbors;
  int coordinate_x = coordinates.first;
  int coordinate_y = coordinates.second;
  for (int i = 0; i < 4; i++) {
    int adj_x = coordinate_x + mov_columns[i];
    int adj_y = coordinate_y + mov_rows[i];
    if (isValid(make_pair(adj_x, adj_y), weighted_matrix.size(),
                weighted_matrix[0].size())) {
      neighbors.push_back(make_pair(adj_x, adj_y));
    }
  }
  return neighbors;
}

vector<pair<int, int>> sort_tuples(vector<pair<int, int>> pairs_array, vector<vector<int>> matrix) {
  vector<pair<pair<int, int>, int>> pairs_list;
  for (auto &coordinate : pairs_array) {
    pairs_list.push_back({coordinate, matrix[coordinate.first][coordinate.second]});
  }

  sort(pairs_list.begin(), pairs_list.end(), [](const auto &lhs, const auto &rhs) { return lhs.second < rhs.second; });

  vector<pair<int, int>> sorted_pairs;
  for (auto &pair : pairs_list) {
    sorted_pairs.push_back(pair.first);
  }

  return sorted_pairs;
}


map<pair<int, int>, pair<vector<pair<int, int>>, bool>> who_is_tapping_me( vector<vector<int>> original_matrix, vector<vector<int>> weighted_matrix, vector<pair<int, int>> parkings_coordinates) {
  map<pair<int, int>, pair<vector<pair<int, int>>, bool>> dictionary;
  for (auto parking : parkings_coordinates) {
    if (weighted_matrix[parking.first][parking.second] == 1) {
      dictionary[parking] = make_pair(vector<pair<int, int>>(), true);
      continue;
    }

    vector<pair<int, int>> visiteds;
    deque<pair<int, int>> travel_queue;
    dictionary[parking] = make_pair(vector<pair<int, int>>(), true);
    visiteds.push_back(parking);

    vector<pair<int, int>> following = adjacents(parking, weighted_matrix);
    for (auto element : following) {
      travel_queue.push_back(element);
    }

    while (!travel_queue.empty()) {
      pair<int, int> current = travel_queue.back();
      travel_queue.pop_back();

      if (original_matrix[current.first][current.second] == -1 &&
          weighted_matrix[current.first][current.second] > 0) {
        vector<pair<int, int>> following = adjacents(current, weighted_matrix);
        visiteds.push_back(current);

        for (auto element : following) {
          if (find(visiteds.begin(), visiteds.end(), element) ==
                  visiteds.end() &&
              find(travel_queue.begin(), travel_queue.end(), element) ==
                  travel_queue.end()) {
            travel_queue.push_back(element);
          }
        }
      }

      if (original_matrix[current.first][current.second] != 0 &&
          original_matrix[current.first][current.second] != -1 &&
          original_matrix[current.first][current.second] != 127 &&
          original_matrix[current.first][current.second] != 128 &&
          find(visiteds.begin(), visiteds.end(), current) == visiteds.end()) {
        auto aux = dictionary[parking];
        auto arr = aux.first;
        arr.push_back(make_pair(current.first, current.second));
        dictionary[parking] = make_pair(arr, aux.second);
        visiteds.push_back(current);
      }
    }

    auto sorted = sort_tuples(dictionary[parking].first, weighted_matrix);
    dictionary[parking] = make_pair(sorted, true);
  }

  return dictionary;
}


bool backtracking(map<pair<int, int>, pair<vector<pair<int, int>>, bool>>& graph, vector<vector<int>>& weighted_matrix, vector<vector<int>>& original_matrix, deque<int>& events, map<int, pair<pair<int, int>, int>>& parking_info, vector<pair<int, int>>& parkings) {
    if (events.empty()) {
        return true;
    }
    
    int event = events.front();
    events.pop_front();
    if (event < 0) {
        int parked_airplane = abs(event);
        pair<int, int> coordinate = parking_info[parked_airplane].first;
        if (weighted_matrix[coordinate.first][coordinate.second] == 1) {
            auto& aux = graph[coordinate].first;
            graph[coordinate] = {aux, true};
            bool partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings);
            if (partial_solution) {
                return true;
            } else {
                aux = graph[coordinate].first;
                graph[coordinate] = {aux, false};
                events.push_front(event);
                return false;
            }
        }
        
        vector<pair<int, int>> visited;
        bool flag = dfs(graph, weighted_matrix, coordinate, visited);
        if (flag) {
            auto& aux = graph[coordinate].first;
            graph[coordinate] = {aux, true};
            bool partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings);
            if (partial_solution) {
                return true;
            }
        }
        
        auto& aux = graph[coordinate].first;
        graph[coordinate] = {aux, false};
        events.push_front(event);
        return false;
    } else {
        for (auto parking : parkings) {
            if (graph[parking].second != false) {
                vector<pair<int, int>> visited;
                bool flag = dfs(graph, weighted_matrix, parking, visited);
                if (flag) {
                    parking_info[event] = {parking, original_matrix[parking.first][parking.second]};
                    auto& aux = graph[parking].first;
                    graph[parking] = {aux, false};
                    bool partial_solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings);
                    if (partial_solution) {
                        return true;
                    } else {
                        aux = graph[parking].first;
                        graph[parking] = {aux, true};
                        parking_info.erase(event);
                    }
                }
            }
        }
        
        events.push_front(event);
        return false;
    }
}


vector<string> split_string(string str) {
    vector<string> result;
    string current_word;
    for (char c : str) {
        if (c == ' ') {
            result.push_back(current_word);
            current_word = "";
        }
        else {
            current_word += c;
        }
    }
    result.push_back(current_word);
    return result;
}


int main() {
    int n = 1;
    while (n < 22) {
        string line;
        getline(cin, line);
        vector<string> first_line = split_string(line);
        deque<string> first_line_deque(first_line.begin(), first_line.end());
        if (first_line_deque.size() < 3) {
            break;
        }

        int rows = stoi(first_line_deque[1]);
        int columns = stoi(first_line_deque[2]);
        vector<vector<int>> original_matrix(rows, vector<int>(columns));
        vector<vector<int>> weighted_original_matrix(rows, vector<int>(columns));
        deque<pair<int, int>> landing_spaces;
        for (int i = 0; i < rows; i++) {
            getline(cin, line);
            vector<string> row_strings = split_string(line);
            vector<int> row_original(columns);
            vector<int> row_weighted(columns);
            for (int j = 0; j < columns; j++) {
                string element = row_strings[j];
                if (element == "..") {
                    row_original[j] = -1;
                    row_weighted[j] = -1;
                }
                else if (element == "==") {
                    landing_spaces.push_front({i, j});
                    row_weighted[j] = 0;
                    row_original[j] = 0;
                }
                else if (element == "##") {
                    row_weighted[j] = 127;
                    row_original[j] = 127;
                }
                else {
                    row_weighted[j] = 128;
                    row_original[j] = stoi(element);
                }
            }
            original_matrix[i] = row_original;
            weighted_original_matrix[i] = row_weighted;
        }

        getline(cin, line);
        vector<string> event_strings = split_string(line);
        deque<int> events;
        for (string event_string : event_strings) {
            int event = stoi(event_string);
            events.push_back(event);
        }

        map<int, pair<pair<int, int>, int>> parking_info;
        vector<vector<int>> weighted_matrix;
        vector<pair<int, int>> parkings;
        tie(weighted_matrix, parkings) = weight_matrix(weighted_original_matrix, landing_spaces);
        map<pair<int, int>, pair<vector<pair<int, int>>, bool>> graph = who_is_tapping_me(original_matrix, weighted_matrix, parkings);
        bool solution = backtracking(graph, weighted_matrix, original_matrix, events, parking_info, parkings);
        if (!solution) {
            cout << "Case " << n << ": No" << endl << endl;
        }
        else {
            cout << "Case " << n << ": Yes " << endl;
            for (int i = 1; i <= parking_info.size(); i++) {
                string assigned_parking = to_string(parking_info[i].second);
                if (assigned_parking.size() == 1) {
                    assigned_parking = "0" + assigned_parking;
                }
                cout << assigned_parking << " ";
            }
            cout << endl << endl;
        }

      n++;
    }

    return 0;
}