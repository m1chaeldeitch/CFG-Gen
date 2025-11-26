void main() {
    int var = 1;

    // Switch statement
    switch (var) {
    case 1: // TODO -- handle switch cases (maybe transform to an if statement, maybe just deal with the logic)
        for (int z = 0; z < 5; z++) {
            printf("Case 1 is Matched.");
        }
        break;
    case 2:
        printf("Case 2 is Matched.");
        break;
    case 3:
        printf("Case 3 is Matched.");
        break;
    default:
        printf("Default case is Matched.");
        break;
    }

}