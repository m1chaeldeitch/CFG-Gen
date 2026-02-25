#include "Image.h"

void call1();

void call1() {
    call_pthread_create();
}

int main() {
    call1();
}

