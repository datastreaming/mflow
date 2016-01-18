import mflow
import signal

counter = 0
folder = None


def dump(receiver):
    receiver.next()
    while receiver.has_more():
        receiver.next()


def main():

    import time
    import argparse
    parser = argparse.ArgumentParser(description='Stream statistic utility')

    parser.add_argument('source', type=str, help='Source address - format "tcp://<address>:<port>"')

    arguments = parser.parse_args()

    address = arguments.source
    stream = mflow.connect(address)

    previous_time = 0

    # Signal handling
    global more
    more = True

    def stop(*arguments):
        global more
        more = False
        signal.siginterrupt()

    signal.signal(signal.SIGINT, stop)

    previous_time = time.time()
    previous_total_bytes_received = 0
    previous_messages_received = 0

    while more:
        message = stream.receive(handler=dump)

        now = time.time()
        delta_time = now - previous_time

        # Print every second
        # TODO Need to be done differently as at the end of a stream the last stats do not show up
        # Use threading.Timer(1, foo).start()
        # (http://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python)
        # As printing out every time a message is received will slow down the receive process
        if delta_time > 0.1:

            total_bytes_received = message.statistics.total_bytes_received
            messages_received = message.statistics.messages_received

            receive_rate = (total_bytes_received - previous_total_bytes_received) / delta_time
            message_rate = (messages_received - previous_messages_received) / delta_time

            previous_total_bytes_received = total_bytes_received
            previous_messages_received = messages_received
            previous_time = now

            print(chr(27) + "[2J")
            print("_"*60)
            print('Messages received: {}'.format(messages_received))
            print('Total bytes received: {} Mb'.format(total_bytes_received/1024.0/1024.0))

            print("Message rate: {} Hz".format(message_rate))
            print("Receive rate: {} Mbps".format(receive_rate/1024/1024*8))
            print("_"*60)
            print('')


if __name__ == '__main__':
    main()
