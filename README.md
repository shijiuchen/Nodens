# Nodens
This repository contains codes for a research paper that was submitted for publication at the [2023 USENIX Annual Technical Conference (ATC23)](https://www.usenix.org/conference/atc23).

## What is Nodens
The microservice application often meets with load and call graph dynamics. When these dynamics happen, the QoS can be violated due to the inappropriate resource allocation for microservices. Current microservice systems are hard to deel with these dynamics in both a fast and resource-efficient way, and thus lead to long QoS recovery time. Therefore, we propose Nodens to quickly allocate enough (or a little excessive) resources for microservices based on the dependencies among them, which can enable fast QoS recovery while maintaining the resource efficiency.

## Environment Preparation
- Hardware requirement
    - A cluster with 8 CPU servers or more
    - CPU: Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz
    - DRAM: 256 GB

- Software requirement
    - Ubuntu 20.04.2 LTS with kernel 5.11.0-34-generic
    - Docker (version 20.10.8) is installed for each server
    - Kubernetes (version v1.20.4) is deployed for the 8-server cluster
    - Python GPRC (version latest)

## Getting Started
1. To deploy the benchmark based on Kubernetes, you can use the yaml files we provide. 
    ```
    cd benchmarks/hotelReservation
    kubectl apply -f /k8s-yaml/
    ```
    More information about the benchmark can be seen in `benchmarks/hotelReservation/README.md`.

2. Start the GRPC server which in charge of getting network traffic and adjusting resources for microservices on each work server.
    ```
    cd workerServer
    python3 server.py
    ```

3. We implement an asynchronous load generator to send different loads and call graphs to the microservice application.
    ```
    cd LoadGenerator
    python3 LoadGenerator-dis-hr.py -t 2 -q 2000 -d 30
    ```
    You can change QPS, test duration and other options in the file.

4. For offline profiling, use the GRPC servers to get network traffic and CPUs for microservices. You can refer to the profile example. 
    ```
    python3 profile_example.py
    ```
    We also provide the script to get network traffic of microservices.
    ```
    cd NetTrafficMonitor/
    python3 NetworkTrafficMonitor_temp.py
    ```
    Then, use above data to fit linear regression prediction models for different microservices.

5. Replace the slope and intercept values into `./ResPredictor/Predictor.py` for microservices with above results.

6. For testing each dynamic scenario, first replace values in `testRes.py` to set the just-enough/over-provisioned resources for the initial state.

7. Then, you can run the testing case: 
    - Start the load generator with loads and call graphs. For example: 
    ```
    cd LoadGenerator
    python3 LoadGenerator-dis-hr.py -t 1 -q 2000 -d 60
    ```
    - Start the agent on the coordinator server to manage the resources of microservices. For example, 
    ```
    python3 Agent.py
    ```

8. After the testing, you can obtain latencies from jaeger.
    ```
    python3 getLatencyRes.py
    ```




