void main() {
    for (int i = 0; i < 101; i++) {
       int visible = 1;
       for (int j = 0; j < 100; j++) {
            printf("dog2\n");
       }
       printf("cat\n");
       printf("dog\n");
    }

    int j = 0;
    while (j < 101) {
        printf("cat\n");
        printf("dog\n");
        j++;

        for (int j = 0; j < 100; j++) {
            printf("dog2\n");

            while (true) {
                for (int p = 0; p < 5; p++) {
                    printf("cat\n");
                }
            }
       }
    }

    do {
        j--;
        printf("dog\n");
    } while (j > 50 && (true || false));


    int magic_value = 4;
    if (true) {
        for (int k = 0; k < 5; k++) {
            printf("dog\n");

            for (int k = 0; k < 5; k++) {
                printf("dog\n");
            }
        }
    } else if (magic_value < 3) {
        magic_value--;
        for (int k = 0; k < 5; k++) {
            printf("dog\n");
        }
    } else if (magic_value > 6) {
        magic_value = 0;
    } else {
        magic_value++;
    }
}

