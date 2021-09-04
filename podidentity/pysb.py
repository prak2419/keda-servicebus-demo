import os
import time
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential
#CONNECTION_STR = os.getenv('KEDA_SERVICEBUS_QUEUE_CONNECTIONSTRING')
POD_NAME = os.getenv('MY_POD_NAME')
#conn_properties = [s.split("=", 1) for s in CONNECTION_STR.strip().rstrip(";").split(";")]
#QUEUE_NAME = conn_properties[3][1]
QUEUE_NAME = os.getenv('QUEUE_NAME')
QUEUE_NAME_REC = os.getenv('QUEUE_NAME_REC')
print(POD_NAME)
#CONNECTION_STR_REC = os.getenv('KEDA_SERVICEBUS_QUEUE_CONNECTIONSTRING_REC')
#conn_properties_rec = [s.split("=", 1) for s in CONNECTION_STR_REC.strip().rstrip(";").split(";")]
#QUEUE_NAME_REC = conn_properties_rec[3][1]
SB_HOSTNAME = "kedademosb.servicebus.windows.net"

credential = DefaultAzureCredential()

def send_single_message(sender, messageRec):
    msg = "Message processed by pod: {} - {}".format(POD_NAME, messageRec)
    message = ServiceBusMessage(msg)
    sender.send_messages(message)
    print("Sent a single message")

#servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
#servicebus_client_rec = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR_REC, logging_enable=True)
servicebus_client = ServiceBusClient(SB_HOSTNAME, credential=credential)

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=25)
    with receiver:
        received_message_array = receiver.receive_messages(max_wait_time=10, max_message_count=1)
        if (received_message_array):
            print("Received: " + str(received_message_array[0]))
            sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME_REC)
            print("sending a message to {}".format(QUEUE_NAME_REC))
            with sender:
                send_single_message(sender, received_message_array[0])
            receiver.complete_message(received_message_array[0])


servicebus_client.close()