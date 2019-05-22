#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <mongoc/mongoc.h>
#include <bson.h>
#include <time.h>

/*
 * gcc -o mongocpath mongocpath.c $(pkg-config --cflags --libs libmongoc-1.0 libbson-1.0)     //to compile
 * /bin/joy firstcapture.pcap | ./mongocpath                        //to run
*/

int main() { 
    
    char *line = NULL;
    size_t size;
    char *version = "version";
    
    //initialize mongodb
    mongoc_client_t *client;
    mongoc_collection_t *collection;
    //bson_t *data;
    bson_error_t error;
    
    
    //use below to test for a file
    //FILE *fp;
    //fp = fopen("mediacomjoy.txt", "r");
    
    
    int line_count = 0;
    float linepersec = 0.0;
    double sec_t = 0.0;
    double finalLPS = 0.0;
    
    clock_t init_time;
    clock_t total_t;
    clock_t last_time;
    mongoc_init();
    
    client = mongoc_client_new("mongodb://localhost:27017/?appname=flowanalyzer");
    collection = mongoc_client_get_collection(client, "flowdb", "flowcoll");
    
    
    //pointer to any minus signs in string
    char * minusp = NULL;
    bson_t *data;
    
    init_time = clock();
    last_time = clock();
    for(;;){
        
        //if (getline(&line, &size, fp) == -1) {
        
        if (getline(&line, &size, stdin) == -1) {
            
            printf("Finished \n");
            //printf(line);
            break;
            //continue;
        } else {
            //check for first line:
            line_count++;
            if (strstr(line, version) != NULL){
                //skip
                //printf(line);
                continue;
            } else {
                //send to mongo db
                
                minusp = strstr(line, "-");
                while(minusp != NULL) {
                    *minusp = '0';
                    minusp = strstr(line, "-");
                    
                }
                data = bson_new_from_json( (const uint8_t *) line, -1, &error);
                
                if(!mongoc_collection_insert(collection, MONGOC_INSERT_NONE, data, NULL, &error)) {
                    fprintf(stderr, "%s\n", error.message);
                }
                
                /*if(line_count % 10000 == 0) {
                    printf("lines processed: %d \n", 10000);
                    sec_t = ((double) clock() - last_time)/CLOCKS_PER_SEC;
                    finalLPS = 10000/sec_t;
                    printf("line per second: %f \n", finalLPS);
                    last_time = clock();
                    
                }*/
                //*line = NULL;
                //size = NULL;
                bson_destroy(data);
                
            }
            
            
                
        }
    }
    //bson_destroy(data);
    total_t = clock() - init_time;
    sec_t = total_t /CLOCKS_PER_SEC;
    finalLPS = line_count/sec_t;
    printf("final line per second: %f \n", finalLPS);
    mongoc_collection_destroy(collection);
    mongoc_client_destroy(client);
    mongoc_cleanup();
    
        
    
}
