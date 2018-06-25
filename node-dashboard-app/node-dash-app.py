import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    client.subscribe("mine")


def on_message(client, userdata, msg):
    mine_flag = msg.payload #TODO what to do with mining flag?
    print('Mine status changed to: {}'.format(str(mine_flag, 'utf-8')))


def node_app():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect('localhost', 1883, 60)

    client.loop_forever()


if __name__ == '__main__':
    node_app()