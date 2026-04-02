#include "polygon_utils.hpp"

#include <cassert>

using std::sort;

void addVertices(HalfEdge* startEdge, std::vector<Vertex*>& vertices){
        HalfEdge* currEdge = startEdge;
        // pushing first edge's origin
        vertices.push_back(currEdge->origin);
        currEdge = currEdge->nextEdge;

        // Adding all other edges cyclically
        while(currEdge != startEdge && currEdge != nullptr){
            vertices.push_back(currEdge->origin);
            currEdge = currEdge->nextEdge;
        }
        //Safety check that it's a polygon
        assert(currEdge != nullptr);
}

std::vector<Vertex*> getMergedPolygonVertices(Face* gallery){
    std::vector<Vertex*> mergedPolygonVertices;
    // Safety check to make sure gallery has edges
    if(gallery->boundaryEdge != nullptr){
        // Adding the final merged polygon vertices
        HalfEdge* startEdge = gallery->boundaryEdge;
        addVertices(startEdge, mergedPolygonVertices);
    }

    return mergedPolygonVertices;
}

std::vector<Vertex*> getTopmostVertices(Face* gallery){
    std::vector<Vertex*> topmostVertices;
    // Iterating through all the Holes
    for(HalfEdge* startingEdge : gallery->InnerComponents){
        // Setting max as initial edge
        double maxY = startingEdge->origin->y;
        Vertex* topMost = startingEdge->origin;
        // Traversing through all the edges (and in turn the vertices)
        HalfEdge* curr = startingEdge->nextEdge;
        while(curr != startingEdge && curr != nullptr){
            if(curr->origin->y > maxY){
                // Updating the max
                maxY = curr->origin->y;
                topMost = curr->origin;
            }
            curr  = curr->nextEdge;
        }
        // Safety Check that polygon was complete
        assert(curr != nullptr);
        topmostVertices.push_back(topMost);
    }
    // Sorting the vertices
    sort(topmostVertices.begin(), topmostVertices.end(), [](Vertex* a, Vertex* b){
        if(a->y != b->y){
            return a->y > b->y;
        }else{
            return a->x < b->x;
        }
    });

    return topmostVertices;
}
