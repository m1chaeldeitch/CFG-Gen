int add(int a, int b);

int add(int a, int b) {
    return a + b;
}

void main() {
    int var = 1;
    3 + 3;
    ;

    // Switch statement
    switch (var) {
    case 1: // TODO -- handle switch cases (maybe transform to an if statement, maybe just deal with the logic)
        for (int z = 0; z < 5; z++) {
            printf("Case 1 is Matched.");

            switch (z) {
            case 1:
                printf("Nested case1");
                if (z == 1) {
                    for (int l = 0; l < 5; l++) {
                        printf("Nested for loop");

                        while (true) {
                            for (int c = 0; c < 5; c++) {
                                switch (c) {
                                    case 1:
                                    printf("Very nested switch case");
                                    break;

                                }

                            }

                        }
                    }
                }
                break;
            default:
                printf("default case matched");
                break;
            }

        }
        break;
    case 2:
        printf("Case 2 is Matched.");
        int c = add(a, b) + 3;
        c = add(a, c) + 3;
        break;
    case 3:
        printf("Case 3 is Matched.");
        break;
    default:
        printf("Default case is Matched.");
        break;
    }

}