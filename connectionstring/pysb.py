import os
import time
from azure.servicebus import ServiceBusClient, ServiceBusMessage
CONNECTION_STR = os.getenv('KEDA_SERVICEBUS_QUEUE_CONNECTIONSTRING')
POD_NAME = os.getenv('MY_POD_NAME')
conn_properties = [s.split("=", 1) for s in CONNECTION_STR.strip().rstrip(";").split(";")]
QUEUE_NAME = conn_properties[3][1]
print(QUEUE_NAME)
print(CONNECTION_STR)
print(POD_NAME)
print("nothing")
CONNECTION_STR_REC = os.getenv('KEDA_SERVICEBUS_QUEUE_CONNECTIONSTRING_REC')
conn_properties_rec = [s.split("=", 1) for s in CONNECTION_STR_REC.strip().rstrip(";").split(";")]
QUEUE_NAME_REC = conn_properties_rec[3][1]

def send_single_message(sender):
    msg = "Message processed by pod: {}".format(POD_NAME)
    message = ServiceBusMessage(msg)
    sender.send_messages(message)
    print("Sent a single message")

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
servicebus_client_rec = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR_REC, logging_enable=True)


with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=25)
    with receiver:
        received_message_array = receiver.receive_messages(max_wait_time=10, max_message_count=1)
        if (received_message_array):
            print("Received: " + str(received_message_array[0]))
            receiver.complete_message(received_message_array[0])

with servicebus_client_rec:
    sender = servicebus_client_rec.get_queue_sender(queue_name=QUEUE_NAME_REC)
    print("sending a message to {}".format(QUEUE_NAME_REC))
    with sender:
        send_single_message(sender)