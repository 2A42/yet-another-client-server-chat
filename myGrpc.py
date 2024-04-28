import grpc
import grpc_tools.protoc
from services import call_createTSV

def createPyFromProto():
    # generate service_pb2 (for proto messages) and 
    # service_pb2_grpc (for RPCs) stubs
    grpc_tools.protoc.main([
        'grpc_tools.protoc',
        '-I{}'.format("./Protos/."),
        '--python_out=.',
        '--grpc_python_out=.',
        './Protos/greet.proto'
    ])

def send_file(Name, _HOST, _PORT, in_file):
    call_createTSV(in_file)
    createPyFromProto()
    # create pb2-files
    import greet_pb2
    import greet_pb2_grpc

    channel = grpc.insecure_channel(_HOST + ':' + _PORT)
    helloStub = greet_pb2_grpc.HelloStub(channel)
    response = helloStub.SayHello(greet_pb2.HelloRequest(name=Name))
    print(response.msg) 
    input("Press any key to send file . . .")
    result = ''
    try:
        # Создаем потоковый запрос
        with open(in_file, "r") as fi:
            streamStub = greet_pb2_grpc.StreamStub(channel)
            request_iterator = (greet_pb2.StreamRequest(data=line) for line in fi)

            streaming_call = streamStub.ProcessStream(request_iterator)

            result = streaming_call

    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    return result