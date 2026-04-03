#include "guards.hpp"

#include <array>
#include <iostream>
#include <queue>
#include <set>
#include <unordered_set>
#include <vector>

namespace {

void addAdjacencyEdge(std::vector<std::unordered_set<int>>& adjacency, int u, int v) {
    adjacency[u].insert(v);
    adjacency[v].insert(u);
}

std::vector<std::unordered_set<int>> buildAdjacency(const std::vector<TriangleIndices>& triangles,
                                                    int vertexCount) {
    std::vector<std::unordered_set<int>> adjacency(vertexCount);
    for (const TriangleIndices& triangle : triangles) {
        addAdjacencyEdge(adjacency, triangle[0], triangle[1]);
        addAdjacencyEdge(adjacency, triangle[0], triangle[2]);
        addAdjacencyEdge(adjacency, triangle[1], triangle[2]);
    }
    return adjacency;
}

bool colorGraph(const std::vector<TriangleIndices>& triangles,
                           int vertexCount,
                           std::vector<int>& color) {
    std::vector<std::unordered_set<int>> adjacency = buildAdjacency(triangles, vertexCount);
    std::vector<int> degree(vertexCount, 0);
    std::vector<bool> removed(vertexCount, false);
    std::vector<int> removalOrder;
    removalOrder.reserve(vertexCount);

    std::queue<int> queue;
    for (int vertex = 0; vertex < vertexCount; ++vertex) {
        degree[vertex] = static_cast<int>(adjacency[vertex].size());
        if (degree[vertex] <= 2) {
            queue.push(vertex);
        }
    }

    while (!queue.empty()) {
        const int vertex = queue.front();
        queue.pop();
        if (removed[vertex] || degree[vertex] > 2) {
            continue;
        }

        removed[vertex] = true;
        removalOrder.push_back(vertex);
        for (int neighbor : adjacency[vertex]) {
            if (removed[neighbor]) {
                continue;
            }
            --degree[neighbor];
            if (degree[neighbor] <= 2) {
                queue.push(neighbor);
            }
        }
    }

    if (static_cast<int>(removalOrder.size()) != vertexCount) {
        return false;
    }

    for (auto it = removalOrder.rbegin(); it != removalOrder.rend(); ++it) {
        const int vertex = *it;
        std::array<bool, 3> blocked = {false, false, false};
        for (int neighbor : adjacency[vertex]) {
            if (color[neighbor] != -1) {
                blocked[color[neighbor]] = true;
            }
        }

        int chosenColor = -1;
        for (int candidate = 0; candidate < 3; ++candidate) {
            if (!blocked[candidate]) {
                chosenColor = candidate;
                break;
            }
        }

        if (chosenColor == -1) {
            return false;
        }
        color[vertex] = chosenColor;
    }

    return true;
}

}  // namespace

GuardSolution computeGuards(const TriangulationResult& triangulation, int totalVertices, int holeCount) {
    GuardSolution solution;
    solution.theoreticalBound = (totalVertices + holeCount) / 3;

    if (triangulation.triangleIndices.empty()) {
        return solution;
    }

    std::vector<int> color(triangulation.occurrenceVertices.size(), -1);
    if (!colorGraph(triangulation.triangleIndices,
                               static_cast<int>(triangulation.occurrenceVertices.size()),
                               color)) {
        std::set<Vertex*> fallbackVertices(triangulation.occurrenceVertices.begin(),
                                           triangulation.occurrenceVertices.end());
        for (Vertex* vertex : fallbackVertices) {
            if (static_cast<int>(solution.guards.size()) == solution.theoreticalBound) {
                break;
            }
            solution.guards.push_back(vertex);
        }
        return solution;
    }

    std::array<std::set<Vertex*>, 3> colorClasses;
    for (int occurrence = 0; occurrence < static_cast<int>(triangulation.occurrenceVertices.size()); ++occurrence) {
        colorClasses[color[occurrence]].insert(triangulation.occurrenceVertices[occurrence]);
    }

    int bestColor = 0;
    for (int colorIdx = 1; colorIdx < 3; ++colorIdx) {
        if (colorClasses[colorIdx].size() < colorClasses[bestColor].size()) {
            bestColor = colorIdx;
        }
    }

    solution.guards.assign(colorClasses[bestColor].begin(), colorClasses[bestColor].end());
    return solution;
}

void printGuards(const GuardSolution& solution) {
    std::cout << solution.guards.size() << '\n';
    for (Vertex* guard : solution.guards) {
        std::cout << guard->x << ' ' << guard->y << '\n';
    }
}
