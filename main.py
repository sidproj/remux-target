import socketio
import os
import subprocess

# standard Python
sio = socketio.Client()


class TargetNamespace(socketio.ClientNamespace) :
    
    # do not update this programatically
    __cwd = r'/home/ubuntu/Desktop'
    
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
    def addTerminal(self,terminal_id):
        for term in self.__terminals:
            if term["terminal_id"] == terminal_id:return
        
        self.__terminals.append({
            "cwd":self.__cwd,
            "previous_command":[],
            "terminal_id":terminal_id
        })
    
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
    
    def execute_command(self,id,command):

        if self.is_cd_command(command):
            return self.execute_cd(id,command)

        terminal = None

        for term in self.__terminals:
            if term['terminal_id'] == id:
                terminal=term
                break

        if terminal == None : return "Error"

        print(terminal['cwd'])
        os.chdir(terminal['cwd'])
        result = subprocess.check_output(command,shell=True,text=True)[:-1]
        return result
    
    def execute_cd(self,id,command):
        split = command.split(" ")
        split.pop(0)
        directory = " ".join(split)
        os.chdir(directory)
        cwd = subprocess.check_output("pwd",shell=True,text=True).strip()

        for term in self.__terminals:
            if term['terminal_id'] == id:
                term["cwd"] = cwd
                print(term['cwd'])
                break
        return cwd

    def is_cd_command(self,command):
        split = command.split(" ")
        if(split[0]=="cd") : return True
        return False
    
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
        print(payload)
        
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

        # if self.__cwd == payload['path']:
        #     self.emit("load_desktop_response",{"path":payload['path'],"status":True,"data":data})

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
    
    def on_rename_item_request(self,payload):

        source = os.path.join(payload["path"],payload["oldName"])
        dest = os.path.join(payload["path"],payload["newName"])

        print(f"server requested to rename { source } to {dest}")
        os.rename(source,dest)

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
    def on_remove_item_from_path_request(self,payload):
        
        print(f"server requested to delete { payload['path'] } items")
        
        path = payload['path']
        
        dir_name = os.path.dirname(path)

        if not self.isPathValid(path):
            self.emit('load_dir_response',{'status':False,'data':None})
            return
            
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
        
        data = self.listItems(dir_name)
        
        self.emit("load_dir_response",{"path":dir_name,"status":True,"data":data})

        if self.__cwd == payload['path']:
            self.emit("load_desktop_response",{"path":payload['path'],"status":True,"data":data})
        
    
    #------------------- folder and its files events -END -------------------#
        
    #------------------- files and its data events -------------------#     
    
    """
        schema for request payload of the function below:-
        {
            path:"path",
        }
        schema for response payload of the function below:-
        {
            path:"path",
            data:"data"
        }
    """
    def on_get_data_from_file_request(self,payload):
        
        if not self.isPathValid(payload['path']):
            self.emit('get_data_from_file_response',{'status':False,'data':None})
            return
        
        file = open(payload['path'],"r")
        fileData = file.read()
        
        data = {
            'path':payload['path'],
            'data':fileData,
        }
        self.emit("get_data_from_file_response",{'status':True,'data':data})


    """
        schema for request payload of the function below:-
        {
            path:"path",
            data:"data",
        }
        schema for response payload of the function below:-
        {
            path:"path",
            data:"data"
        }
    """
    def on_set_data_to_file_request(self,payload):
        path = payload['path']
        
        if not self.isPathValid(path):
            self.emit('set_data_to_file_response',{'status':False,'data':None})
            return
        
        file = open(path,'w')
        file.write(payload['data'])
        file.close()
        
        newFile = open(path,'r')
        fileData = newFile.read()
        
        data = {
            'path':path,
            'data':fileData
        }
        self.emit('get_data_from_file_response',{'status':True,'data':data})     
    
    #------------------- files and its data events -END-------------------#     
    
    #------------------- terminal and its events -------------------#   
    
    #terminal command execution request
    def on_execute_command_request(self,payload):
        self.addTerminal(payload["id"])
        print("server requested to execute command")
        print(payload['command'])
        result = self.execute_command(payload['id'],payload['command']).strip()
        self.emit("execute_command_response",{"id":payload["id"],"result":result})

    #terminal opened by user
    def on_terminal_open_request(self,payload):
        self.addTerminal(payload['terminal_id'])
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
