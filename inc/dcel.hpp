#pragma once

#include <vector>

struct HalfEdge;

struct Vertex{
    double x, y;
    HalfEdge* originatingEdge;
}; // Store just one edge counter clockwise one for Outer Polygon and Clockwise Edge for hole 

struct Face{
    HalfEdge* boundaryEdge;
    //Choose a random edge of the outer boundary (which we can traverse to get polygon)
    std::vector<HalfEdge*> InnerComponents;
    // Similarly store all the inner holes as well
};

struct HalfEdge{
    Vertex* origin;// We consider directed edge
    Face* boundaryFace;// Inner Face
    HalfEdge* nextEdge;// Next edge in polygon
    HalfEdge* prevEdge;// Prev edge in polygon
    HalfEdge* twin; // Same Vertices Opposite direction we will be using for Bridges 
};
