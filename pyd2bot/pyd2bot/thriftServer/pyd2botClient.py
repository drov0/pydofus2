from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService


if __name__ == '__main__':
    transport = TSocket.TSocket('127.0.0.1', 9999)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Pyd2botService.Client(protocol)
    transport.open()
    recv = client.fetchAccountCharacters('aloone-100', 'rmrtxha1', '126200687', '7f5bc8707c07b2d86303c608c6b80c5abd7c64df2f26e11569c51b9bc9094f45')
    print(recv)
    transport.close()