#include <iostream>

#include "hole_merger.hpp"
#include "parser.hpp"

int main() {
    int T;
    std::cin >> T;
    
    while(T--){
        Face* gallery = parseSingleGallery();
        mergeHoles(gallery);
        
        
    }

    return 0;
}
