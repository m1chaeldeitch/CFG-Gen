struct combinedData {
    int a;
    double b;
    char* c;
};

typedef struct combinedData combinedData;

enum item{
    PRODUCT, SERVICE
};


void main() {
    ;
    _Alignas(16) int q[4];
    static_assert(0, "assert1");
    2+2;

    enum item newItem = PRODUCT;

    int* pointer = (int*)malloc(sizeof(int));
    for (int i = 0; i < 101; i++) {
       break;
       continue;
       pointer = 3 + i;
       int x,y,z = 0;
       int j,k,n;
       &pointer = 3000;
       pointer = *pointer + i;
       int visible = 1;
       visible = 2;

       int* integer_array = {1,2,3};
       integer_array[1] = 0;

       int actualArray[5] = {0,1,2,3,4};
       array[5] = -9;


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


    int var = 1;

    // Switch statement
    switch (var) {
    case 10:
        k = 10;
        p = k + 1;
        return 10;
    case 20:
        switch (magic_value) {
            case 1:
            return 10;

            case 2:
            magic_value++;
            break;

            default:
            printf("Default");
        }
    case 30:
        return 20;
    default:
        break;
    }
}

