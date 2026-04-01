#include "parser.hpp"

#include <iostream>
#include <vector>

void parsePolygonEdges(Face* gallery, bool isOuter){
    int v0;
    std::cin >> v0;
    
    std::vector<HalfEdge*> polyEdges;
    // Adding all the vertices and corresponding originating Half edges
    // Assuming Counter clockwise input for the Outer Polygon
    // And assuming Clockwise input for inner holes
    // (The gallery will be same as the direction of input is being adjusted)
    for(int i = 0; i < v0; i++){
        double x, y;
        std::cin >> x >> y;

        Vertex* v = new Vertex{x, y, nullptr};
        HalfEdge* e = new HalfEdge{v, gallery, nullptr, nullptr, nullptr};
        
        v->originatingEdge = e;

        polyEdges.push_back(e);
    }

    for(int i = 0 ; i < v0; i++){
        int next = (i+1)%v0;
        int prev = (i+v0-1)%v0;
        // Setting next and previous edges accordingly
        polyEdges[i]->nextEdge = polyEdges[next];
        polyEdges[i]->prevEdge = polyEdges[prev];
        // We are not going to be using the twin edge in this scenario
    }

    // Adding them to the gallery according to if they are outer / hole edges
    if(isOuter)
        gallery->boundaryEdge = polyEdges[0];
    else
        gallery->InnerComponents.push_back(polyEdges[0]);
}

Face* parseSingleGallery(){
    Face* gallery = new Face();

    parsePolygonEdges(gallery, true);

    // Parsing the inner holes 
    int h;
    std::cin >> h;

    // Assuming clockwise vertex input for the inner holes 
    for(int i = 0; i < h; i++){
        parsePolygonEdges(gallery, false);
    }

    return gallery;
}
