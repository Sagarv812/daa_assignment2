#include "polygon_utils.hpp"

#include <cassert>

namespace {

std::size_t countVerticesOnCycle(HalfEdge* startEdge) {
    std::size_t count = 0;
    HalfEdge* currEdge = startEdge;

    do {
        ++count;
        currEdge = currEdge->nextEdge;
    } while (currEdge != startEdge && currEdge != nullptr);

    assert(currEdge != nullptr);
    return count;
}

bool higherThenLeft(Vertex* a, Vertex* b) {
    if (a->y != b->y) {
        return a->y > b->y;
    }
    return a->x < b->x;
}

Vertex* findTopmostVertexOnCycle(HalfEdge* startEdge) {
    Vertex* topMost = startEdge->origin;
    HalfEdge* currEdge = startEdge->nextEdge;

    while (currEdge != startEdge && currEdge != nullptr) {
        if (higherThenLeft(currEdge->origin, topMost)) {
            topMost = currEdge->origin;
        }
        currEdge = currEdge->nextEdge;
    }

    assert(currEdge != nullptr);
    return topMost;
}

}  // namespace

void addVertices(HalfEdge* startEdge, std::vector<Vertex*>& vertices) {
    HalfEdge* currEdge = startEdge;

    do {
        vertices.push_back(currEdge->origin);
        currEdge = currEdge->nextEdge;
    } while (currEdge != startEdge && currEdge != nullptr);

    assert(currEdge != nullptr);
}

std::vector<Vertex*> getMergedPolygonVertices(Face* gallery) {
    std::vector<Vertex*> mergedPolygonVertices;
    if (gallery->boundaryEdge != nullptr) {
        addVertices(gallery->boundaryEdge, mergedPolygonVertices);
    }

    return mergedPolygonVertices;
}

std::vector<Vertex*> getTopmostVertices(Face* gallery) {
    std::vector<Vertex*> topmostVertices;
    topmostVertices.reserve(gallery->InnerComponents.size());

    for (HalfEdge* startingEdge : gallery->InnerComponents) {
        topmostVertices.push_back(findTopmostVertexOnCycle(startingEdge));
    }

    std::sort(topmostVertices.begin(), topmostVertices.end(), higherThenLeft);

    return topmostVertices;
}

std::size_t getTotalVertexCount(Face* gallery) {
    std::size_t totalVertices = 0;

    if (gallery->boundaryEdge != nullptr) {
        totalVertices += countVerticesOnCycle(gallery->boundaryEdge);
    }

    for (HalfEdge* holeEdgeStart : gallery->InnerComponents) {
        totalVertices += countVerticesOnCycle(holeEdgeStart);
    }

    return totalVertices;
}
