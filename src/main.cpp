#include <iostream>

#include "hole_merger.hpp"
#include "parser.hpp"
#include "polygon_utils.hpp"

int main() {
    int T;
    std::cin >> T;
    
    while(T--){
        Face* gallery = parseSingleGallery();
        mergeHoles(gallery);
        std::vector<Vertex*> mergedPolygonVertices = getMergedPolygonVertices(gallery);

        if(mergedPolygonVertices.size() == 0) continue;
        
        
    }

    return 0;
}
