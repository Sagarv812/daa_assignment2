#pragma once

#include <algorithm>
#include <vector>

#include "dcel.hpp"

void addVertices(HalfEdge* startEdge, std::vector<Vertex*>& vertices);
std::vector<Vertex*> getMergedPolygonVertices(Face* gallery);
std::vector<Vertex*> getTopmostVertices(Face* gallery);
std::size_t getTotalVertexCount(Face* gallery);

template <typename CompareFunc>
std::vector<Vertex*> getVerticesSorted(Face* gallery, CompareFunc comp) {
    std::vector<Vertex*> allVertices;

    // Safety check to make sure gallery has edges
    if(gallery->boundaryEdge != nullptr){
        // Adding outer vertices
        HalfEdge* startEdge = gallery->boundaryEdge;
        addVertices(startEdge, allVertices);
    }

    // Okay now adding the vertices of the inner holes
    for(HalfEdge* holeEdgeStart : gallery->InnerComponents){
        addVertices(holeEdgeStart, allVertices);
    }
    // Sorting vertices with custom lambda
    std::sort(allVertices.begin(), allVertices.end(), comp);
    return allVertices;
}
