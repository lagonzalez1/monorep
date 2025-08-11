import asyncio
import grpc
import service_pb2 as pb
import service_pb2_grpc as rpc
from verse.common import get_memory_usage
from grpc_reflection.v1alpha import reflection


class ServerThree(rpc.VerseServiceServicer):
    async def Echo(self, request, context):
        return pb.EchoReply(msg=request.msg)

    async def GetMemory(self, request, context):
        return pb.MemReply( usage=get_memory_usage() )
    

async def serve():
    server = grpc.aio.server()
    rpc.add_VerseServiceServicer_to_server(ServerThree(), server)

    SERVICE_NAMES = (
        'demo.v1.VerseService',
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server=server)

    server.add_insecure_port("0.0.0.0:5000")
    await server.start()
    print("gRPC server running on port 5000")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())


