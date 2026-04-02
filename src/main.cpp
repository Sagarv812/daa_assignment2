#include <iostream>

#include "hole_merger.hpp"
#include "parser.hpp"
#include "triangulation.hpp"

int main() {
    int T;
    std::cin >> T;
    
    while(T--){
        Face* gallery = parseSingleGallery();
        mergeHoles(gallery);
        std::vector<Triangle> triangles = triangulateGallery(gallery);
        printTriangles(triangles, std::cout);
    }

    return 0;
}
