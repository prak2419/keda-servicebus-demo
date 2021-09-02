# AKS - Autoscale pods using KEDA

[KEDA Documentation](https://keda.sh/)
- [KEDA - Azure ServiceBus Integration](https://keda.sh/docs/2.4/scalers/azure-service-bus/)
- [KEDA - AWS SQS Integration](https://keda.sh/docs/2.4/scalers/aws-sqs/)

[Integration with ServiceBus queue through its connection string](#integration-with-servicebus-queue-through-its-connection-string)
  - [Pre-requisites](#pre-requisites)
  - [Installing KEDA](#installing-keda)
  - [Containerize the code](#containerize-the-code)
  - [Deploy the application](#deploy-the-application)

## Integration with ServiceBus queue through its connection string

The purpose of this POC is to scale the pods based on the number of active messages in a service bus queue. KEDA handles bringing up the required pods to process the messages based on metrics from the ServiceBus queue. Once, the execution is completed it can automatically scale in the pods as well.

### Pre-requisites
The following pre-requisites have to be met,
- Helm to add and install the KEDA repo.
- Separate namespace for KEDA to decouple its components from the application namespace.
- Shared access policy on the queue.
- To implement the container presented in the demo, `azure-servicebus` (v7.3.2) module is required.

### Installing KEDA

Deploying KEDA with Helm:

1. Add Helm repo

    ```bash

    helm repo add kedacore https://kedacore.github.io/charts

    ```

2. Update Helm repo

    ```bash

    helm repo update

    ```

3. Create a namespace for KEDA and Install keda Helm chart

    ```bash

    kubectl create namespace keda

    helm install keda kedacore/keda --namespace keda

    ```

### Containerize the code

1. Use Docker build to build the container image from the repo folder,

    ```bash

    docker build -f Dockerfile -t pysbdemo:1.4.11 .

    ```

2. Tag the image to ACR, assuming you are already authenticated to ACR

    ```bash

    docker tag pysbdemo:1.4.11 mydemoacr002.azurecr.io:1.4.11

    ```

3. Push the image to ACR

    ```bash

    docker push mydemoacr002.azurecr.io:1.4.11

    ```

### Deploy the application
We need two queues for this demo. One queue will be used to receive the message for processing and the other will be used to send the queue details with the processing pod name for debugging. This can be used in the retry logic to re-process the messages in case of a failure.

1. Modify the `secret.yml` manifest to deploy secrets that will be used by the container to mount connection strings and queue names as environment variables
    * Update the queue's connection string for both the queues in a base64 encoded format.
  
       ```bash

       echo "<conn_string>" | openssl base64 -A

       ```

    * Update the queue's name for the queues in a base64 encoded format.
       
       ```bash

       echo "<queue_name>" | openssl base64 -A

       ```

2. Set the context of kubectl to your application namespace

    ```bash

    kubectl config set-context --current --namespace=<app_namespace>

    ```

3. If the scaling has to be handled as a deployment, we need to perform the following steps,
    
    * Modify the values of Azure Container Registry on the `deployment.yml` file.
    * Apply the deployment to the cluster, assuming the user is already authenticated to AKS cluster

       ```bash

       kubectl apply -f deployment.yml

       ```

    * Update the `scale_deployment.yml` file with the value of your queue name.
    * Deploy the `ScaledObject` to the cluster

       ```bash

       kubectl apply -f scale_deployment.yml

       ```

    * Send a few messages to the queue to look at how the deployment scales. The scaled out pods will automatically be terminated after a default time of 5 minutes by KEDA. **More investigation is required to find how long can this scale back time be extended**.
    * You can check the second queue to see if the messages were sent during processing.

4. If the scaling has to be deployed as jobs, we need to perform the following steps,
   
    * Update the `scale_job.yml` with appropriate job related configuration and also change the ACR/queue names.
    * Deploy the `ScaledJob` to the cluster

       ```bash

       kubectl apply -f scale_job.yml

       ```

    * Send a few messages to the queue to look at the job scaling in action. Based on the value set for the `successfulJobsHistoryLimit` spec in the manifest, the job history will be shown. Also, if the `activeDeadlineSeconds` spec is set to a value lower than the time it takes to complete the job, the job will automatically terminated once the time window expires.