int fib(int m);

int fib(int m) {
    int f0 = 0
    int f1 = 1
    int f2;
    int i;

    if (m <= 1) {
        return m;
    } else {
         i = 2
        while i <= m:
            f2 = f0 + f1
            f0 = f1
            f1 = f2
            i = i + 1

        return f2
    }
}

int main() {
    int output = fib(5);
    printf(output);
}
