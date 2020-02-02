from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from .models import Message

User  = get_user_model()

class ChatConsumer(WebsocketConsumer):
    """This is a synchronous WebSocket consumer that: 
        accepts all connections, 
        receives messages from its client, 
        and echos those messages back to the same client. 
    Inorder to broadcast messages to other clients in the same room:
        When a user posts a message, a JavaScript function will transmit 
        the message over `WebSocket` to a `ChatConsumer`. 
        The `ChatConsumer` will receive that message and forward it to the `group` 
        corresponding to the `room name`. Every ChatConsumer in the same group 
        (and thus in the same room) will then receive the message from the group
        and forward it over WebSocket back to JavaScript, where it will be appended to the chat log
    """
    def fetch_messages(self, data):
        """ Fetches messages from the Database and passes them into the webSocket """
        messages = Message.last_10_messages()
        # serialize the messages from the database
        content = {
            # 'command': 'messages',
            "messages": self.serialize_messages_to_json(messages)
        }
        # send those 10 serialized messages to the websocket
        self.send_chat_message(content)

    def new_message(self, data):
        """Needs the author as well as content"""
        author = data['from']   # this will hold the user in the template
        author_user = User.objects.filter(username__iexact=author)[0]
        # create the message instance in the database
        message_instance = Message(
                                author=author_user,
                                content=data['message']
                                    )
        message_instance.save()
        # pass the message to the websocket
        content = {
            "command": "new_message",
            "message": self.serialize_message_to_json(message_instance)
        }
        return self.send_chat_message(content)

    def serialize_messages_to_json(self, messages):
        """
            changes from model instance to json objects
            From this you should have a list of json objects
        """
        outcome = []
        for message in messages:
            # grab hold of the fields per instance
            outcome.append(self.serialize_message_to_json(message))
        return outcome

    def serialize_message_to_json(self, message):
        """
            changes individual model instance to json objects
            From this you should have a list of json objects
        """
        return {
            "author": message.author.username,
            "content": message.content,
            "created_at": str(message.created_at)
        }

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add) (
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard) (
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        # get the command. if either one or the other: redirect to respective method which will use send_chat_message() inside it
        self.commands[ data['command'] ](self, data) # (self, data) are the arguments for method called

    def send_chat_message(self, message):
        """
        Send the message acquired from "receive()" => "commands" => "fetch_messages/new_message" Back to the specified room
        """
        async_to_sync(self.channel_layer.group_send) (
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        """Use it in fetch_messages() uptop"""
        self.send(text_data=json.dumps(message))


    # Receive message from room group
    def chat_message(self, event):
        """grabs the message from the event then Sends the message to WebSocket"""
        message = event['message']
        self.send(text_data=json.dumps(message)) # was this earlier: json.dumps({'message': message}) but since we serialized it up-top