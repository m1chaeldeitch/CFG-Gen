//Include files
#include <stdio.h>
#include <stdlib.h>

//Data structures
struct process {
    int pid;
    int* taos;        //used to be a pointer, but probably not necessary
    int* actual_t;
    double alpha;
};

//Pre-declarations
void populate_processes(FILE* file, struct process* all_processes, int ticks, int num_processes);
int get_tick_count(FILE * file);
int get_process_count(FILE* file);
void shortest_job_first_dead(FILE* file, int ticks, int processes, struct process* all_processes);
void shortest_job_first_live(FILE* file, int ticks, int processes, struct process* all_processes);

//Main
int main(int argc, char *argv[]) {
    FILE* input_file = fopen(argv[1], "r");

    if (input_file == NULL) {
        printf("File could not be opened. Terminating.");
        return -1;
    }

    int ticks = get_tick_count(input_file);
    int process_count = get_process_count(input_file);
    struct process* all_processes = malloc(sizeof(struct process) * process_count);
    populate_processes(input_file, all_processes, ticks, process_count);

    shortest_job_first_dead(input_file, ticks, process_count, all_processes);
    printf("\n\n");
    shortest_job_first_live(input_file, ticks, process_count, all_processes);


    //Cleanup
    for (int i = 0; i < process_count; i++) {
        free(all_processes[i].taos);
        free(all_processes[i].actual_t);
    }
    free(all_processes);
    fclose(input_file);

    return 0;
}


//Helpers

void populate_processes(FILE* file, struct process* all_processes, int ticks, int num_processes) {
    for (int i = 0; i < num_processes; i++) {
        //  for each process there is:
        //      a) PID
        //      b) tau
        //      c) alpha
        //      d) tick # of actual_t's


        char buffer[256];

        // (a)
        fgets(buffer, 256, file);
        all_processes[i].pid = atoi(buffer);

        // (b)
        fgets(buffer, 256, file);
        all_processes[i].taos = malloc(sizeof(int) * ticks);
        all_processes[i].taos[0] = atoi(buffer);

        // (c)
        fgets(buffer, 256, file);
        all_processes[i].alpha = atof(buffer);

        // (d)
        all_processes[i].actual_t = malloc(sizeof(int) * ticks);
        for (int j = 0; j < ticks; j++) {
            fgets(buffer, 256, file);
            all_processes[i].actual_t[j] = atoi(buffer);
        }
    }
}

int get_tick_count(FILE * file) {
    char buffer[256];
    fgets(buffer, 256, file);
    return atoi(buffer);
}

int get_process_count(FILE* file) {
    char buffer[256];
    fgets(buffer, 256, file);
    return atoi(buffer);
}

void shortest_job_first_dead(FILE* file, int ticks, int processes, struct process* all_processes) {
    int turnaround_t = 0;
    int waiting_t = 0;
    int elapsed_time = 0;
    for (int currTick = 0; currTick < ticks; currTick++) {
        // for each tick...
        printf("Simulating %dth tick of processes @ time = %d\n", currTick, elapsed_time);

        struct process sorted_processes[processes];
        int num_sorted = 0;

        for (int j = 0; j < processes; j++) {
            if (num_sorted == 0) {
                sorted_processes[num_sorted++] = all_processes[j];
            } else {
                //add to the end
                sorted_processes[num_sorted] = all_processes[j];
                //swap until it is in the correct spot
                for (int start = num_sorted; start > 0; start--) {
                    if (sorted_processes[start].actual_t[currTick] < sorted_processes[start - 1].actual_t[currTick]) {
                        struct process copy = sorted_processes[start];                   // potential scope issues
                        sorted_processes[start] = sorted_processes[start -1];
                        sorted_processes[start - 1] = copy;
                    }
                }
                num_sorted++;
            }
        }

        for (int j = 0; j < processes; j++) {
            elapsed_time += sorted_processes[j].actual_t[currTick];
            if (j == 0) {
                waiting_t += sorted_processes[j].actual_t[currTick];
            }
            turnaround_t += sorted_processes[j].actual_t[currTick];

            printf("Process %d took %d.\n", sorted_processes[j].pid, sorted_processes[j].actual_t[currTick]);
            // make sure to keep track of the other stats that need to be kept track of (turnaround and waiting time)
        }
    }
    printf("Turnaround time: %d\n", elapsed_time + waiting_t);
    printf("Waiting time: %d", waiting_t);
}

void shortest_job_first_live(FILE* file, int ticks, int processes, struct process* all_processes) {
    int turnaround_t = 0;
    int waiting_t = 0;
    int elapsed_time = 0;
    int error = 0;
    for (int currTick = 0; currTick < ticks; currTick++) {
        // for each tick...
        printf("Simulating %dth tick of processes @ time = %d\n", currTick, elapsed_time);

        //create tao estimate for each process within the tick
        for (int p = 0; p < processes; p++) {
            if (currTick != 0) {
                double alpha = all_processes[p].alpha;
                int previous_t = all_processes[p].actual_t[currTick - 1];
                int previous_estimate = all_processes[p].taos[currTick - 1];

                all_processes[p].taos[currTick] = (alpha * previous_t) + ( (1.0 - alpha) * previous_estimate);
            }
        }

        //sort the jobs based on _tao_ estimate
        struct process sorted_processes[processes];
        int num_sorted = 0;

        for (int j = 0; j < processes; j++) {
            if (num_sorted == 0) {
                sorted_processes[num_sorted++] = all_processes[j];
            } else {
                //add to the end
                sorted_processes[num_sorted] = all_processes[j];
                //swap until it is in the correct spot
                for (int start = num_sorted; start > 0; start--) {
                    if (sorted_processes[start].taos[currTick] < sorted_processes[start - 1].taos[currTick]) {
                        struct process copy = sorted_processes[start];                   // potential scope issues
                        sorted_processes[start] = sorted_processes[start -1];
                        sorted_processes[start - 1] = copy;
                    }
                }
                num_sorted++;
            }
        }

        for (int j = 0; j < processes; j++) {
            elapsed_time += sorted_processes[j].actual_t[currTick];
            if (j == 0) {
                waiting_t += sorted_processes[j].actual_t[currTick];
            }
            turnaround_t += sorted_processes[j].actual_t[currTick];

            printf("Process %d was estimated for %d and took %d.\n", sorted_processes[j].pid, sorted_processes[j].taos[currTick], sorted_processes[j].actual_t[currTick]);
            // make sure to keep track of the other stats that need to be kept track of (turnaround and waiting time)
            error += abs(sorted_processes[j].taos[currTick] - sorted_processes[j].actual_t[currTick]);
        }
    }
    printf("Turnaround time: %d\n", elapsed_time + waiting_t);
    printf("Waiting time: %d\n", waiting_t);
    printf("Estimation Error: %d\n", error);
}