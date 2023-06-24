import socketio
import os

# standard Python
sio = socketio.Client()


class TargetNamespace(socketio.ClientNamespace) :
    def on_connect(self):
        print(f"I'm connected with id {sio.namespaces['/target']}")

    def on_testing(self,data):
        print("In testing event")
        print(data)


    def on_send_target_msg(self,data):
        print("In send target msg")
        cwd = os.getcwd()
        self.emit("send_user_msg",{"message":"cwd","cwd":cwd})
        print(data)

    def on_create_file(self,data):
        print(data)
        location = os.getcwd()
        path = os.path.join(location,data['filename'])
        file = open(data['filename'],'w')
        file.close()

    def on_delete_file(self,data):
        print(data)
        location = os.getcwd()
        path = os.path.join(location,data['filename'])
        os.remove(path)

    def on_connect_error(self,data):
        print("The connection failed!")

    def on_disconnect(self):
        print("I'm disconnected!")

    def on_disconnect_self(self,data):
        print(data)
        sio.disconnect()
        exit(0)


sio.register_namespace(TargetNamespace("/target"))


@sio.event
def connect():
    print(f"I'm connected with id {sio.get_sid()}")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")
    
@sio.on("testing")
def testing(data):
    print(data)

@sio.on("send_target_msg")
def send_target_msg(data):
    print(data)

@sio.on("disconnect_self")
def disconnect_self(data):
    print(data)
    sio.disconnect()
    exit(0)

sio.connect("http://localhost:5000",namespaces=['/target'])