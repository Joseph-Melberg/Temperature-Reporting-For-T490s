import datetime
import subprocess
import pika

def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()

printout = str(system_call("sensors ")).split('\\n')

print("houd")
printout = printout[24:-23]
result = []
for i in printout:
    result.append(i.split('\\x')[0].split('+')[1])
print(result)
temps = []
spots = ["Package Id 0","Core 0","Core 1","Core 2","Core 3"]
for i in range(len(spots)):
    entry = {}
    entry["Temperature"] = float(result[i])
    entry["PartName"] = spots[i]
    temps.append(entry)
outbound = {}
outbound["HostName"] = "yoltvo"
outbound["Timestamp"] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
outbound["Temperatures"] = temps
print(outbound)
credentials = pika.PlainCredentials('tempy','celsius')
connection = pika.BlockingConnection(pika.ConnectionParameters('rancher.centurionx.net',5672,'/',credentials))
channel = connection.channel()
channel.exchange_declare(exchange='InterTopic',exchange_type='topic',durable=True)
channel.queue_bind(exchange='InterTopic',queue='Temperature',routing_key='temperature.*')
channel.basic_publish(exchange='InterTopic',
                      routing_key='temperature.standard',
                      body=str(outbound))
connection.close()
