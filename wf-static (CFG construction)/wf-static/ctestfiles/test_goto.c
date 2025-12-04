int main() {
    int x = 5;
    x = x - 1;
    start:
    int y = 3;
    printf("print");

    if (x > 0 ) {
        goto start;
    }
}