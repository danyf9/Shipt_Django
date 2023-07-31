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
        for p in pairs:
            k_v = p.split("=")
            if k_v[0] == 'room':
                room = k_v[1]
            if k_v[0] == 'user':
                user_name = k_v[1]

        room = room if room else "global"
        user_name = user_name if user_name else "anonymous"
        self.user_name = user_name
        self.group_name = f"room_{room}"

        # accept connection
        self.accept()

        # this will be sent only to the current user
        # self.send(text_data=json.dumps({'message': "Welcome to chat room.  \
        #                                 please keep rules and respect bla bla.."}))

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name)

        # let everyone know that a new user entered
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'type': 'global_handler',  # this is a function
                'message': f"user {user_name} entered the chat",
                'event_type': 'info'  # optional extra info
            }
        )

    def receive(self, text_data):
        text_data = json.loads(text_data)

        # send feedback only to the sender
        # self.send(text_data=json.dumps({'message': f"new message '{text_data}' received"}))

        # forward message to all
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'message': f'{self.user_name}: {text_data["message"]}',
                'type': 'global_handler',  # this is a function
            }
        )

    def global_handler(self, event):
        """ This function will be run by each channel """

        self.send(text_data=json.dumps(
            {'message': event['message']}))

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'message': f'{self.user_name} left the chat',
                'type': 'global_handler',  # this is a function
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        self.close(code)
