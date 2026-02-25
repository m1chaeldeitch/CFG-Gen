#include <pthread.h>
void runner1();
void runner2();
void runner3();
void runner4();
void runner5();
void runner6();

void runner1() {
    for (int i = 0; i < 5; i++) {
        int s = pthread_create(0, NULL, NULL, NULL);
    }
}

void runner2() {
    runner1();
}

void runner3() {
    runner2();
}

void runner4() {
    runner3();
}

void runner5() {
    runner4();
}

void runner6() {
    runner5();
}

int main() {
    int x = 5;
    x = x - 1;

    runner6();

}