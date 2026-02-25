void call_pthread_create() {
    int s = pthread_create(0, NULL, NULL, NULL);
}

// The statement within this function should never be a node
// that is returned by graph_utils.find_pthread_create()
// This is because it is defined, but is 1) not accessible to main and 2) never called.
void call_pthread_unused() {
    int s = pthread_create(0, NULL, NULL, NULL);
}