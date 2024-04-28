import pika
from services import getDataFromJSON

config = getDataFromJSON('config')
in_file = config['IN_FILE']
queue = 'TSV_test1'
routing_key = 'TSV_test1'
exchange = 'oss_TSV_test1'

credentials = pika.PlainCredentials(config['R_USER'], config['R_PASS'])
parameters = pika.ConnectionParameters(host=config['IP'], port=config['R_PORT'], virtual_host='/', credentials=credentials)

def queue_send(data):
    connection = pika.BlockingConnection(parameters)
    
    # Создать канал
    channel = connection.channel()
    # Создать брокера
    channel.exchange_declare(exchange=exchange)
    # Объявляя очередь, и производители, и потребители должны объявлять одну и ту же очередь, чтобы одна сторона не зависала, а другая сторона работала нормально.
    channel.queue_declare(queue=queue)
    # Привязать очередь к посреднику
    channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
    # Отправить данные в очередь
    channel.basic_publish(exchange=exchange,
                          routing_key=routing_key, #маршрут - наша очередь
                          body=str(data).encode()) #сообщение

    connection.close()

def queue_consume(clearChat):
    result = ['']
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue=queue)

    for method_frame, properties, body in channel.consume(queue, auto_ack=clearChat, inactivity_timeout=0.95):
        if body is not None: result.append(body.decode('UTF-8'))
        else:   break

    # Cancel the consumer
    requeued_messages = channel.cancel()

    channel.close()
    connection.close()
    return result