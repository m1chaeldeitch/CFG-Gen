void main() {
    int var = 1;

    if (var == 1) {
        print("Var is 1");
    }

       // Switch statement
       switch (var) {
       case 10:
           int newvar = var = 1;
           switch (newvar) {
           case 11:
                printf("nested1");
                return;
           case 12:
                printf("nested2");
                return;
           case 13:
                printf("nested3");
           default:
                printf("nestedDefault");
                break;
           }
           return;
       case 20:
           printf("print_2");

       default:
           printf("print_3");

       case 30:
           printf("print_4");

       case 40:
           printf("print_5");
           return;
       }
}


void other_function() {
    int x = 0;

    if (x == 4) {
        printf("X was 4");
    } else {
        printf("X was not 4");
    }

    x = x + 1;
    printf("X was incremented");

}
