#include "guards.hpp"

#include <array>
#include <cassert>
#include <iostream>
#include <queue>
#include <set>
#include <unordered_map>
#include <utility>
#include <vector>

namespace {

using EdgeKey = std::array<int, 2>;

struct EdgeKeyHash {
    std::size_t operator()(const EdgeKey& edge) const {
        return std::hash<int>{}(edge[0]) ^ (std::hash<int>{}(edge[1]) << 1U);
    }
};

EdgeKey makeEdgeKey(int a, int b) {
    if (a < b) {
        return {a, b};
    }
    return {b, a};
}

int remainingColor(int first, int second) {
    for (int color = 0; color < 3; ++color) {
        if (color != first && color != second) {
            return color;
        }
    }
    return 0;
}

}  // namespace

GuardSolution computeGuards(const TriangulationResult& triangulation, int totalVertices, int holeCount) {
    GuardSolution solution;
    solution.theoreticalBound = (totalVertices + holeCount) / 3;

    if (triangulation.triangleIndices.empty()) {
        return solution;
    }

    std::vector<int> color(triangulation.occurrenceVertices.size(), -1);
    std::vector<std::vector<int>> triangleNeighbors(triangulation.triangleIndices.size());
    std::unordered_map<EdgeKey, std::vector<int>, EdgeKeyHash> trianglesByEdge;

    for (int i = 0; i < static_cast<int>(triangulation.triangleIndices.size()); ++i) {
        const TriangleIndices& triangle = triangulation.triangleIndices[i];
        trianglesByEdge[makeEdgeKey(triangle[0], triangle[1])].push_back(i);
        trianglesByEdge[makeEdgeKey(triangle[1], triangle[2])].push_back(i);
        trianglesByEdge[makeEdgeKey(triangle[2], triangle[0])].push_back(i);
    }

    for (const auto& edgeEntry : trianglesByEdge) {
        const std::vector<int>& sharingTriangles = edgeEntry.second;
        for (int i = 0; i < static_cast<int>(sharingTriangles.size()); ++i) {
            for (int j = i + 1; j < static_cast<int>(sharingTriangles.size()); ++j) {
                triangleNeighbors[sharingTriangles[i]].push_back(sharingTriangles[j]);
                triangleNeighbors[sharingTriangles[j]].push_back(sharingTriangles[i]);
            }
        }
    }

    std::vector<bool> triangleVisited(triangulation.triangleIndices.size(), false);
    for (int startTriangle = 0; startTriangle < static_cast<int>(triangulation.triangleIndices.size()); ++startTriangle) {
        if (triangleVisited[startTriangle]) {
            continue;
        }

        const TriangleIndices& seed = triangulation.triangleIndices[startTriangle];
        color[seed[0]] = 0;
        color[seed[1]] = 1;
        color[seed[2]] = 2;

        std::queue<int> queue;
        queue.push(startTriangle);
        triangleVisited[startTriangle] = true;

        while (!queue.empty()) {
            int triangleIndex = queue.front();
            queue.pop();

            const TriangleIndices& triangle = triangulation.triangleIndices[triangleIndex];
            for (int neighborIndex : triangleNeighbors[triangleIndex]) {
                if (triangleVisited[neighborIndex]) {
                    continue;
                }

                const TriangleIndices& neighbor = triangulation.triangleIndices[neighborIndex];
                std::vector<int> sharedVertices;
                int thirdVertex = -1;

                for (int neighborVertex : neighbor) {
                    bool found = false;
                    for (int triangleVertex : triangle) {
                        if (neighborVertex == triangleVertex) {
                            found = true;
                            sharedVertices.push_back(neighborVertex);
                            break;
                        }
                    }

                    if (!found) {
                        thirdVertex = neighborVertex;
                    }
                }

                assert(sharedVertices.size() == 2);
                assert(thirdVertex != -1);

                int firstColor = color[sharedVertices[0]];
                int secondColor = color[sharedVertices[1]];
                assert(firstColor != -1 && secondColor != -1 && firstColor != secondColor);

                int expectedColor = remainingColor(firstColor, secondColor);

                if (color[thirdVertex] == -1) {
                    color[thirdVertex] = expectedColor;
                } else {
                    assert(color[thirdVertex] == expectedColor);
                }

                triangleVisited[neighborIndex] = true;
                queue.push(neighborIndex);
            }
        }
    }

    std::array<std::set<Vertex*>, 3> colorClasses;
    for (int occurrence = 0; occurrence < static_cast<int>(triangulation.occurrenceVertices.size()); ++occurrence) {
        int assignedColor = color[occurrence];
        if (assignedColor == -1) {
            assignedColor = 0;
        }
        colorClasses[assignedColor].insert(triangulation.occurrenceVertices[occurrence]);
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
