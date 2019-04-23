from channels.generic.websocket import AsyncWebsocketConsumer
from pysnmp.hlapi.asyncio import *
import json

class SnmpConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass
        
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        snmpEngine = SnmpEngine()
        iterator = getCmd(
            snmpEngine,
            CommunityData('public', mpModel=0),
            UdpTransportTarget((message, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.33.1.1.1.0'))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = await next(iterator)

        snmpEngine.transportDispatcher.closeDispatcher()

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
            )
                  )
        else:
            oid,value = varBinds[0]
            message = str(value)
        print(message)
            
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))