import socketio
import os

# standard Python
sio = socketio.Client()


class TargetNamespace(socketio.ClientNamespace) :
    
    # do not update this programatically
    __cwd = r'C:\Users\Sid\Desktop'
    
    # keep the state of all terminals in client's browser
    
    """
        terminals schema:- [terminal]
        terminal schema:-
        {
            cwd:string
            previous command:[]
            terminal_id:""
        }
    """
    __terminals = []
    
    #init function to ask user for credentials and then connect
    
    # helper functions
    
    def listItems(self,path):
        items = os.listdir(path)
        
        data={
            "FILES":[],
            "FOLDERS":[],
            }
        
        for f in items:
            itemData = {
                "path":(path+"/"+f),
                "name":f
            }
            if os.path.isfile(path+"/"+f) : 
                itemData["type"]="FILE"
                data["FILES"].append(itemData)
            else: 
                itemData["type"]="FOLDER"
                data["FOLDERS"].append(itemData)
            
            
        return data

    def isPathValid(self,path):
        if  os.path.exists(path): return True
        return False
    
    def uniquePath(self,path):
        newPath = path
        count = 1
        while os.path.exists(newPath):
            filePath,ext = os.path.splitext(path)
            newPath = filePath + "("+ str(count) + ")" + ext
            count+=1
        return newPath
        
    
    #add terminal to storage of terminals
    def addTerminal(self):
        self.__terminals.append({
            "cwd":self.__cwd,
            "previous_command":[],
        })
        length =  len(self.__terminals)
        terminal_id = id(self.__terminals[length-1])
        self.__terminals[length-1]["terminal_id"] = terminal_id
    
    def removeTerminal(self,terminal_id):
        i = 0
        index = -1
        for terminal in self.__terminals:
            if(terminal["terminal_id"] == terminal_id): 
                index = i
                break
            i+=1
    
        if index != -1:
            del self.__terminals[index]
    
    def is_cd_command(self,command):
        pass
    
    #end
    
    #------------------- events to be emmited by server -------------------#
    
    #------------------- authentication events -------------------#
    
    def on_ask_credentials(self,payload):
        
        # self.emit("login_request",{"username":username,"password":password})
        self.emit("login_request",{"username":"sidhraj","password":"1234"})
    
    def on_login_response(self,payload):
        if payload['success'] == False:
            print("Invalid credentails!")
            exit(0)
        else:
            print("Logged in!")
    
    
    #------------------- folder and its files events -------------------#
    
    """
        schema for request payload does not matter as it has to be desktop
        sechema for response payload of the function below:- 
        [ 
            {type:"FILE",path:"path",name:"name"},
        ]
    """
    def on_load_desktop_request(self,payload):
        print("server requested for desktop items")
        path = self.__cwd
        
        # get list of items in a path
        data = self.listItems(path)
        data["path"] = self.__cwd
                
        self.emit("load_desktop_response",{"data":data})
    
    """
        schema for request payload of the function below:-
        {
            path:""
        }
        sechema for response payload of the function below:- 
        [ 
            {type:"FILE",path:"path",name:"name"},
        ]
    """
    def on_load_dir_request(self,payload):
        
        print(f"server requested for {payload['path']} items")
        # get list of items in a path
        data = self.listItems(payload['path'])
                
        self.emit("load_dir_response",{"path":payload['path'],"status":True,"data":data})
    
    """
        schema for request payload of the function below:-
        {
            path:"path",
            isFile:boolean,
            name:"name"
        }
        schema for response payload of the function below:-
    """
    def on_add_item_to_path_request(self,payload):
        
        
        print(f"server requested to add { payload['name'] } items")
        
        if not self.isPathValid(payload["path"]):
            self.emit("load_dir_response",{"status":False,"data":None})
            return 
        
        newPath = os.path.join(payload["path"],payload["name"])
        newPath = self.uniquePath(newPath)
        
        if(payload["isFile"]):
            file = open(newPath,"w")
            file.close()
        else : 
            os.mkdir(newPath)
        
        # get list of items in a path
        data = self.listItems(payload["path"])
        
        self.emit("load_dir_response",{"path":payload['path'],"status":True,"data":data})
        return
        
    
    """
        schema for request payload of the function below:-
        {
            path:"path",
            isFile:boolean,
            name:"name"
        }
        schema for response payload of the function below:-
    """
    def on_remove_item_from_path_request(self,payload):
        
        print(f"server requested to add { payload['path'] } items")
        
        path = payload['path']
        
        if not self.isPathValid(path):
            self.emit('load_dir_response',{'status':False,'data':None})
            return
        os.remove(path)
        
        data = self.listItems(payload["path"])
        self.emit("load_dir_response",{"status":True,"data":data})
        
    
    #------------------- folder and its files events -END -------------------#
        
    #------------------- files and its data events -------------------#     
    
    """
        schema for request payload of the function below:-
        {
            path:"path",
            name:"name",
        }
        schema for response payload of the function below:-
        {
            path:"path",
            name:"name",
            data:"data"
        }
    """
    def on_get_data_from_file_request(self,payload):
        path = os.path.join(payload['path'],payload['name'])
        
        if not self.isPathValid(path):
            self.emit('get_data_from_file_response',{'status':False,'data':None})
            return
        
        file = open(path,"r")
        fileData = file.read()
        
        data = {
            'path':payload['path'],
            'name':payload['name'],
            'data':fileData,
        }
        self.emit("get_data_from_file_response",{'status':True,'data':data})


    """
        schema for request payload of the function below:-
        {
            path:"path",
            name:"name",
            data:"data",
        }
        schema for response payload of the function below:-
        {
            path:"path",
            name:"name",
            data:"data"
        }
    """
    def on_set_data_to_file_request(self,payload):
        path = os.path.join(payload['path'],payload['name'])
        
        if not self.isPathValid(path):
            self.emit('set_data_to_file_response',{'status':False,'data':None})
            return
        
        file = open(path,'w')
        file.write(payload['data'])
        file.close()
        
        newFile = open(path,'r')
        fileData = newFile.read()
        
        data = {
            'path':payload['path'],
            'name':payload['name'],
            'data':fileData
        }
        self.emit('get_data_from_file_response',{'status':False,'data':data})     
    
    #------------------- files and its data events -END-------------------#     
    
    #------------------- terminal and its events -------------------#   
    
    #terminal opened by user
    def on_terminal_open_request(self,payload):
        self.addTerminal()
        pass
    
    #terminal closed by user
    def on_terminal_closed_request(self,payload):
        self.removeTerminal(payload["terminal_id"])
    
    """
        schema for request payload of the function below:-
        {
            terminal_id:string,
            command:"string"
        }
        schema for response payload of the function below:-
        {
            terminal_id:string,
            result:string
        }
    """
    
    def on_execute_terminal_command_request(self,payload):
        
        
        
        pass
    
    
    #end
        
    def on_connect(self):
        print(f"connected with id {sio.namespaces['/target']} of namespace /target.")

    def on_connect_error(self,data):
        print("The connection failed!")

    def on_disconnect(self):
        print("Disconnected!")
        self.disconnect()
        SystemExit(0)


sio.register_namespace(TargetNamespace("/target"))


# username = input("username: ")
# password = input("password: ")

sio.connect("http://localhost:5000",namespaces=['/target'])
