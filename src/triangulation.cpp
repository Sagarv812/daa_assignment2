#include "triangulation.hpp"

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#include "polygon_utils.hpp"

namespace {

constexpr double eps = 1e-9;

struct PolygonVertex {
    double x;
    double y;
    Vertex* original;
};

struct SweepEdge {
    double x1;
    double y1;
    double x2;
    double y2;
    int from;
    int to;
};

double ccw(const PolygonVertex& a, const PolygonVertex& b, const PolygonVertex& c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

bool samePoint(const PolygonVertex& a, const PolygonVertex& b) {
    return std::abs(a.x - b.x) <= eps && std::abs(a.y - b.y) <= eps;
}

double polygonArea(const std::vector<int>& indices, const std::vector<PolygonVertex>& polygon) {
    double area = 0.0;
    const int n = static_cast<int>(indices.size());
    for (int i = 0; i < n; ++i) {
        const PolygonVertex& a = polygon[indices[i]];
        const PolygonVertex& b = polygon[indices[(i + 1) % n]];
        area += a.x * b.y - b.x * a.y;
    }
    return area / 2.0;
}

double polygonArea(const std::vector<PolygonVertex>& polygon) {
    double area = 0.0;
    const int n = static_cast<int>(polygon.size());
    for (int i = 0; i < n; ++i) {
        const PolygonVertex& a = polygon[i];
        const PolygonVertex& b = polygon[(i + 1) % n];
        area += a.x * b.y - b.x * a.y;
    }
    return area / 2.0;
}

bool isBelow(const PolygonVertex& other, const PolygonVertex& pivot) {
    return (other.y < pivot.y) || (std::abs(other.y - pivot.y) <= eps && other.x > pivot.x);
}

bool isAbove(const PolygonVertex& other, const PolygonVertex& pivot) {
    return (other.y > pivot.y) || (std::abs(other.y - pivot.y) <= eps && other.x < pivot.x);
}

bool comesEarlierInSweepOrder(const PolygonVertex& a, const PolygonVertex& b) {
    if (std::abs(a.y - b.y) > eps) {
        return a.y > b.y;
    }
    return a.x < b.x;
}

std::vector<PolygonVertex> buildMergedPolygon(Face* gallery) {
    std::vector<Vertex*> vertices = getMergedPolygonVertices(gallery);
    std::vector<PolygonVertex> polygon;
    polygon.reserve(vertices.size());

    for (Vertex* vertex : vertices) {
        PolygonVertex occurrence{vertex->x, vertex->y, vertex};
        if (polygon.empty() || !samePoint(polygon.back(), occurrence)) {
            polygon.push_back(occurrence);
        }
    }

    if (polygon.size() > 1 && samePoint(polygon.front(), polygon.back())) {
        polygon.pop_back();
    }

    if (polygonArea(polygon) < 0.0) {
        std::reverse(polygon.begin(), polygon.end());
    }

    return polygon;
}

VertexType classifyVertex(const std::vector<PolygonVertex>& polygon, int idx) {
    const int n = static_cast<int>(polygon.size());
    const PolygonVertex& prev = polygon[(idx - 1 + n) % n];
    const PolygonVertex& curr = polygon[idx];
    const PolygonVertex& next = polygon[(idx + 1) % n];

    const bool prevBelow = isBelow(prev, curr);
    const bool nextBelow = isBelow(next, curr);
    const bool isConvex = ccw(prev, curr, next) > eps;

    if (prevBelow && nextBelow) {
        return isConvex ? VertexType::START : VertexType::SPLIT;
    }

    if (!prevBelow && !nextBelow) {
        return isConvex ? VertexType::END : VertexType::MERGE;
    }

    return isAbove(prev, curr) ? VertexType::REGULAR_LEFT : VertexType::REGULAR_RIGHT;
}

double xIntersectionAtY(const SweepEdge* edge, double y) {
    if (std::abs(edge->y1 - edge->y2) <= eps) {
        return std::min(edge->x1, edge->x2);
    }

    return edge->x1 + (edge->x2 - edge->x1) * (y - edge->y1) / (edge->y2 - edge->y1);
}

struct EdgeComparator {
    bool operator()(const SweepEdge* a, const SweepEdge* b) const {
        if (a == b) {
            return false;
        }

        const double minAY = std::min(a->y1, a->y2);
        const double minBY = std::min(b->y1, b->y2);
        const double maxAY = std::max(a->y1, a->y2);
        const double maxBY = std::max(b->y1, b->y2);

        double yRay = std::max(minAY, minBY);
        if (std::abs(yRay - maxAY) <= eps || std::abs(yRay - maxBY) <= eps) {
            yRay = (std::min(maxAY, maxBY) + yRay) / 2.0;
        }

        const double xA = xIntersectionAtY(a, yRay);
        const double xB = xIntersectionAtY(b, yRay);

        if (std::abs(xA - xB) > eps) {
            return xA < xB;
        }

        return a < b;
    }
};

using ActiveEdges = std::map<const SweepEdge*, int, EdgeComparator>;
using ActiveEdgeIterator = ActiveEdges::iterator;

ActiveEdgeIterator findClosestEdgeToLeft(const PolygonVertex& vertex, ActiveEdges& activeEdges) {
    SweepEdge dummy{
        vertex.x,
        vertex.y - 1.0,
        vertex.x,
        vertex.y + 1.0,
        -1,
        -1,
    };

    auto it = activeEdges.upper_bound(&dummy);
    if (it == activeEdges.begin()) {
        return activeEdges.end();
    }

    --it;
    return it;
}

std::uint64_t encodeUndirectedEdge(int u, int v) {
    if (u > v) {
        std::swap(u, v);
    }
    return (static_cast<std::uint64_t>(u) << 32) | static_cast<std::uint32_t>(v);
}

bool areAdjacent(int u, int v, int n) {
    return ((u + 1) % n == v) || ((v + 1) % n == u);
}

void addDiagonal(int u,
                 int v,
                 const std::vector<PolygonVertex>& polygon,
                 std::unordered_set<std::uint64_t>& seenDiagonals,
                 std::vector<std::pair<int, int>>& diagonals) {
    if (u == v) {
        return;
    }

    const int n = static_cast<int>(polygon.size());
    if (areAdjacent(u, v, n)) {
        return;
    }

    if (samePoint(polygon[u], polygon[v])) {
        return;
    }
    
    // REDUNDANCY PREVENTION: Reject diagonal if there is an existing polygon edge 
    int u_prev = (u - 1 + n) % n;
    int u_next = (u + 1) % n;
    if (samePoint(polygon[u_prev], polygon[v]) || samePoint(polygon[u_next], polygon[v])) {
        return;
    }

    int v_prev = (v - 1 + n) % n;
    int v_next = (v + 1) % n;
    if (samePoint(polygon[v_prev], polygon[u]) || samePoint(polygon[v_next], polygon[u])) {
        return;
    }

    const std::uint64_t key = encodeUndirectedEdge(u, v);
    if (seenDiagonals.insert(key).second) {
        diagonals.push_back({u, v});
    }
}

std::vector<std::pair<int, int>> makeMonotone(const std::vector<PolygonVertex>& polygon,
                                              const std::vector<VertexType>& categories) {
    std::vector<std::pair<int, int>> diagonals;
    const int n = static_cast<int>(polygon.size());

    std::vector<int> order(n);
    for (int i = 0; i < n; ++i) {
        order[i] = i;
    }

    std::sort(order.begin(), order.end(), [&polygon](int a, int b) {
        return comesEarlierInSweepOrder(polygon[a], polygon[b]);
    });

    std::vector<SweepEdge> edges(n);
    for (int i = 0; i < n; ++i) {
        const int next = (i + 1) % n;
        edges[i] = SweepEdge{
            polygon[i].x,
            polygon[i].y,
            polygon[next].x,
            polygon[next].y,
            i,
            next,
        };
    }

    ActiveEdges activeEdges;
    std::unordered_set<std::uint64_t> seenDiagonals;

    for (int idx : order) {
        const int prev = (idx - 1 + n) % n;
        const SweepEdge* incoming = &edges[prev];
        const SweepEdge* outgoing = &edges[idx];

        switch (categories[idx]) {
            case VertexType::START: {
                activeEdges[outgoing] = idx;
                break;
            }
            case VertexType::END: {
                auto inIt = activeEdges.find(incoming);
                if (inIt != activeEdges.end()) {
                    if (categories[inIt->second] == VertexType::MERGE) {
                        addDiagonal(idx, inIt->second, polygon, seenDiagonals, diagonals);
                    }
                    activeEdges.erase(inIt);
                }
                break;
            }
            case VertexType::SPLIT: {
                auto leftIt = findClosestEdgeToLeft(polygon[idx], activeEdges);
                if (leftIt != activeEdges.end()) {
                    addDiagonal(idx, leftIt->second, polygon, seenDiagonals, diagonals);
                    leftIt->second = idx;
                }
                activeEdges[outgoing] = idx;
                break;
            }
            case VertexType::MERGE: {
                auto inIt = activeEdges.find(incoming);
                if (inIt != activeEdges.end()) {
                    if (categories[inIt->second] == VertexType::MERGE) {
                        addDiagonal(idx, inIt->second, polygon, seenDiagonals, diagonals);
                    }
                    activeEdges.erase(inIt);
                }

                auto leftIt = findClosestEdgeToLeft(polygon[idx], activeEdges);
                if (leftIt != activeEdges.end()) {
                    if (categories[leftIt->second] == VertexType::MERGE) {
                        addDiagonal(idx, leftIt->second, polygon, seenDiagonals, diagonals);
                    }
                    leftIt->second = idx;
                }
                break;
            }
            case VertexType::REGULAR_LEFT: {
                auto inIt = activeEdges.find(incoming);
                if (inIt != activeEdges.end()) {
                    if (categories[inIt->second] == VertexType::MERGE) {
                        addDiagonal(idx, inIt->second, polygon, seenDiagonals, diagonals);
                    }
                    activeEdges.erase(inIt);
                }
                activeEdges[outgoing] = idx;
                break;
            }
            case VertexType::REGULAR_RIGHT: {
                auto leftIt = findClosestEdgeToLeft(polygon[idx], activeEdges);
                if (leftIt != activeEdges.end()) {
                    if (categories[leftIt->second] == VertexType::MERGE) {
                        addDiagonal(idx, leftIt->second, polygon, seenDiagonals, diagonals);
                    }
                    leftIt->second = idx;
                }
                break;
            }
        }
    }

    return diagonals;
}

std::vector<int> canonicalizeFace(std::vector<int> face, const std::vector<PolygonVertex>& polygon) {
    while (!face.empty() && samePoint(polygon[face.front()], polygon[face.back()])) {
        face.pop_back();
    }

    std::vector<int> filtered;
    filtered.reserve(face.size());
    for (int idx : face) {
        if (filtered.empty() || !samePoint(polygon[filtered.back()], polygon[idx])) {
            filtered.push_back(idx);
        }
    }

    if (filtered.size() > 1 && samePoint(polygon[filtered.front()], polygon[filtered.back()])) {
        filtered.pop_back();
    }

    return filtered;
}

std::vector<std::vector<int>> extractMonotoneFaces(const std::vector<PolygonVertex>& polygon,
                                                   const std::vector<std::pair<int, int>>& diagonals) {
    const int n = static_cast<int>(polygon.size());
    std::vector<std::vector<int>> adjacency(n);
    std::unordered_set<std::uint64_t> edgesSeen;

    const auto addUndirectedEdge = [&](int u, int v) {
        const std::uint64_t key = encodeUndirectedEdge(u, v);
        if (edgesSeen.insert(key).second) {
            adjacency[u].push_back(v);
            adjacency[v].push_back(u);
        }
    };

    for (int i = 0; i < n; ++i) {
        addUndirectedEdge(i, (i + 1) % n);
    }

    for (const auto& diagonal : diagonals) {
        addUndirectedEdge(diagonal.first, diagonal.second);
    }

    for (int u = 0; u < n; ++u) {
        std::sort(adjacency[u].begin(), adjacency[u].end(), [&polygon, u](int lhs, int rhs) {
            const double angleL = std::atan2(polygon[lhs].y - polygon[u].y, polygon[lhs].x - polygon[u].x);
            const double angleR = std::atan2(polygon[rhs].y - polygon[u].y, polygon[rhs].x - polygon[u].x);
            if (std::abs(angleL - angleR) > eps) {
                return angleL < angleR;
            }

            const double distL = (polygon[lhs].x - polygon[u].x) * (polygon[lhs].x - polygon[u].x) +
                                 (polygon[lhs].y - polygon[u].y) * (polygon[lhs].y - polygon[u].y);
            const double distR = (polygon[rhs].x - polygon[u].x) * (polygon[rhs].x - polygon[u].x) +
                                 (polygon[rhs].y - polygon[u].y) * (polygon[rhs].y - polygon[u].y);
            return distL < distR;
        });
    }

    std::vector<std::unordered_map<int, int>> position(n);
    for (int u = 0; u < n; ++u) {
        for (int i = 0; i < static_cast<int>(adjacency[u].size()); ++i) {
            position[u][adjacency[u][i]] = i;
        }
    }

    std::unordered_set<std::uint64_t> usedDirected;
    std::vector<std::vector<int>> faces;

    for (int u = 0; u < n; ++u) {
        for (int v : adjacency[u]) {
            const std::uint64_t startKey =
                (static_cast<std::uint64_t>(u) << 32) | static_cast<std::uint32_t>(v);
            if (usedDirected.count(startKey) != 0U) {
                continue;
            }

            std::vector<int> face;
            int a = u;
            int b = v;
            const int startA = u;
            const int startB = v;

            while (true) {
                face.push_back(a);
                usedDirected.insert((static_cast<std::uint64_t>(a) << 32) | static_cast<std::uint32_t>(b));

                auto posIt = position[b].find(a);
                assert(posIt != position[b].end());
                const int degree = static_cast<int>(adjacency[b].size());
                const int nextPos = (posIt->second - 1 + degree) % degree;
                const int c = adjacency[b][nextPos];

                a = b;
                b = c;

                if (a == startA && b == startB) {
                    break;
                }
            }

            face = canonicalizeFace(face, polygon);
            if (face.size() < 3) {
                continue;
            }

            const double area = polygonArea(face, polygon);
            if (area > eps) {
                faces.push_back(face);
            }
        }
    }

    return faces;
}

std::vector<int> simplifyFace(const std::vector<int>& face, const std::vector<PolygonVertex>& polygon) {
    std::vector<int> cleaned = canonicalizeFace(face, polygon);
    if (cleaned.size() < 3) {
        return cleaned;
    }

    bool changed = true;
    while (changed && cleaned.size() >= 3) {
        changed = false;
        std::vector<int> reduced;
        const int m = static_cast<int>(cleaned.size());
        reduced.reserve(m);

        for (int i = 0; i < m; ++i) {
            const int prev = cleaned[(i - 1 + m) % m];
            const int curr = cleaned[i];
            const int next = cleaned[(i + 1) % m];

            if (samePoint(polygon[prev], polygon[curr]) || samePoint(polygon[curr], polygon[next])) {
                changed = true;
                continue;
            }

            // Preserve genuine collinear occurrences so bridge endpoints from different
            // holes still have to appear as vertices in the final triangulation.
            reduced.push_back(curr);
        }

        cleaned.swap(reduced);
    }

    return cleaned;
}

std::vector<std::pair<int, int>> triangulateMonotoneFace(const std::vector<int>& rawFace,
                                                         const std::vector<PolygonVertex>& polygon) {
    std::vector<std::pair<int, int>> diagonals;
    std::vector<int> face = simplifyFace(rawFace, polygon);
    const int m = static_cast<int>(face.size());
    if (m < 3) {
        return diagonals;
    }

    int top = 0;
    int bottom = 0;
    for (int i = 1; i < m; ++i) {
        const PolygonVertex& vertex = polygon[face[i]];
        const PolygonVertex& topVertex = polygon[face[top]];
        const PolygonVertex& bottomVertex = polygon[face[bottom]];

        if (comesEarlierInSweepOrder(vertex, topVertex)) {
            top = i;
        }

        if (comesEarlierInSweepOrder(bottomVertex, vertex)) {
            bottom = i;
        }
    }

    std::vector<bool> isLeftChain(static_cast<std::size_t>(polygon.size()), false);
    int cursor = top;
    while (cursor != bottom) {
        isLeftChain[face[cursor]] = true;
        cursor = (cursor + 1) % m;
    }
    isLeftChain[face[bottom]] = true;

    std::vector<int> sorted = face;
    std::sort(sorted.begin(), sorted.end(), [&polygon](int lhs, int rhs) {
        return comesEarlierInSweepOrder(polygon[lhs], polygon[rhs]);
    });

    std::vector<int> stack;
    stack.push_back(sorted[0]);
    stack.push_back(sorted[1]);

    for (int j = 2; j < m - 1; ++j) {
        const int current = sorted[j];
        if (isLeftChain[current] != isLeftChain[stack.back()]) {
            while (stack.size() > 1) {
                const int topVertex = stack.back();
                stack.pop_back();
                if (!areAdjacent(current, topVertex, static_cast<int>(polygon.size()))) {
                    diagonals.push_back({current, topVertex});
                }
            }

            stack.pop_back();
            stack.push_back(sorted[j - 1]);
            stack.push_back(current);
        } else {
            int lastPopped = stack.back();
            stack.pop_back();

            while (!stack.empty()) {
                const int stackTop = stack.back();
                const double turn = ccw(polygon[current], polygon[lastPopped], polygon[stackTop]);
                const bool inside = isLeftChain[current] ? (turn < -eps) : (turn > eps);
                if (!inside) {
                    break;
                }

                if (!areAdjacent(current, stackTop, static_cast<int>(polygon.size()))) {
                    diagonals.push_back({current, stackTop});
                }
                lastPopped = stackTop;
                stack.pop_back();
            }

            stack.push_back(lastPopped);
            stack.push_back(current);
        }
    }

    const int last = sorted.back();
    if (!stack.empty()) {
        stack.pop_back();
    }

    while (stack.size() > 1) {
        const int topVertex = stack.back();
        if (!areAdjacent(last, topVertex, static_cast<int>(polygon.size()))) {
            diagonals.push_back({last, topVertex});
        }
        stack.pop_back();
    }

    return diagonals;
}

}  // namespace

TriangulationResult triangulateGallery(Face* gallery) {
    TriangulationResult result;
    std::vector<PolygonVertex> polygon = buildMergedPolygon(gallery);
    if (polygon.size() < 3) {
        return result;
    }

    result.occurrenceVertices.reserve(polygon.size());
    for (const PolygonVertex& occurrence : polygon) {
        result.occurrenceVertices.push_back(occurrence.original);
    }

    std::vector<VertexType> categories(polygon.size());
    for (int i = 0; i < static_cast<int>(polygon.size()); ++i) {
        categories[i] = classifyVertex(polygon, i);
    }

    std::vector<std::pair<int, int>> diagonals = makeMonotone(polygon, categories);
    const std::vector<std::vector<int>> monotoneFaces = extractMonotoneFaces(polygon, diagonals);

    for (const std::vector<int>& face : monotoneFaces) {
        std::vector<std::pair<int, int>> faceDiagonals = triangulateMonotoneFace(face, polygon);
        diagonals.insert(diagonals.end(), faceDiagonals.begin(), faceDiagonals.end());
    }

    const std::vector<std::vector<int>> triangularFaces = extractMonotoneFaces(polygon, diagonals);
    for (std::vector<int> face : triangularFaces) {
        face = simplifyFace(face, polygon);
        if (face.size() != 3) {
            continue;
        }

        const double area = ccw(polygon[face[0]], polygon[face[1]], polygon[face[2]]);
        if (std::abs(area) <= eps) {
            continue;
        }

        if (area > 0.0) {
            result.triangles.push_back({polygon[face[0]].original, polygon[face[1]].original, polygon[face[2]].original});
            result.triangleIndices.push_back({face[0], face[1], face[2]});
        } else {
            result.triangles.push_back({polygon[face[0]].original, polygon[face[2]].original, polygon[face[1]].original});
            result.triangleIndices.push_back({face[0], face[2], face[1]});
        }
    }

    return result;
}

void printTriangles(const std::vector<Triangle>& triangles) {
    if (triangles.empty()) return;
    std::cout << triangles.size() << '\n';
    for (const Triangle& triangle : triangles) {
        std::cout << triangle[0]->x << ' ' << triangle[0]->y << ' '
                  << triangle[1]->x << ' ' << triangle[1]->y << ' '
                  << triangle[2]->x << ' ' << triangle[2]->y << '\n';
    }
}
