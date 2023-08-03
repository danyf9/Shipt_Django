from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class MyConsumer(WebsocketConsumer):

    def connect(self):

        # parse parameters to get chat-room and user-name
        q_params_str = self.scope['query_string'].decode()
        pairs = q_params_str.split("&")
        room = None
        user_name = None
        staff = None
        for p in pairs:
            k_v = p.split("=")
            if k_v[0] == 'room':
                room = k_v[1]
            if k_v[0] == 'user':
                user_name = k_v[1]
            if k_v[0] == 'staff':
                staff = k_v[1]

        room = room if room else "global"
        user_name = user_name if user_name else "anonymous"
        staff = staff if staff else False
        self.user_name = user_name
        self.group_name = f"room_{room}"
        self.staff = staff

        # accept connection
        self.accept()

        # this will be sent only to the current user
        # self.send(text_data=json.dumps({'message': "Welcome to chat room.  \
        #                                 please keep rules and respect bla bla.."}))

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name)
        if staff:
            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {
                    'message': {'message': f'Staff {user_name} is here to help',
                                'user': self.user_name, 'msg_type': 'j'},
                    'type': 'global_handler',  # this is a function
                }
            )


    def receive(self, text_data):
        text_data = json.loads(text_data)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'message': {'message': text_data["message"], 'user': self.user_name, 'msg_type': 'm'},
                'type': 'global_handler',  # this is a function
            }
        )

    def global_handler(self, event):
        """ This function will be run by each channel """

        self.send(text_data=json.dumps(
            {'message': event['message']}))

    def disconnect(self, code):
        msg = f'Staff {self.user_name} left the chat' if self.staff else f'Costumer {self.user_name} left the chat'
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'message': {'message': msg,
                            'user': self.user_name, 'msg_type': 'l'},
                'type': 'global_handler',  # this is a function
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        self.close(code)
