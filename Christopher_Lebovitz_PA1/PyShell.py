import os
import sys
import time

# function to check if the command that the user enter exceeds the character limit
def check_Input(line):
    #if the user only presses the enter button and nothing else keep asking for input until an command is entered
    while line == '':
        line = input('Python Shell>')
    #check if the input line is shorter than 80 characters
    if len(line) > 80:
        print("ERROR: Exceeded maximum character length of 80")
        line = input('Python Shell>')

    return line

# function to check the list for the & character, remove it from the list, and return true to tell the shell
# to run parent and child concurrently
def concurrent(command):
    if '&' in command:
        position = command.index('&')
        command.pop(position)
        return True
    else:
        return False

# this functioon check to see if the user wishes to redirect input and output to the console.
def file_operation(command):
    if '>' in command:
        # grab the name of the file by accssing the last element in the list and create a file to write to
        filename = open(str(command[-1]), 'w')
        # remove the last two items in the list which sould be the '>' character and the name of the file
        command.pop()
        command.pop()
        os.dup2(filename.fileno(), sys.stdout.fileno())
        #clear stdout
        sys.stdout = sys.__stdout__

    elif '<' in command:
        # grab the name of the file by accssing the last element in the list to read from and pass to the command
        filename = open(str(command[-1]), 'r')
        # remove the '<' character and the name of the file 
        command.pop()
        command.pop()
        os.dup2(filename.fileno(), sys.stdin.fileno())
        
# function to run the previous command if the user enters !!
def execute_Last(command, history):
    if '!!' in command:
        # if there is no command in the history list tell the user to enter there is no command history
        if not history:
            print("No command history")
            line = input('Python Shell>')
        else:
            # if ther is a command in history then remove the '!!' in the command list then
            # set the list = to the last index in history
            command.pop()
            command = history[-1].split()
            print(command)
            print("Python Shell>" + str(command))
    return command

#the function creates the child process and executes the commands stored int he command list.
def run_child(command):
    # flag that is use to check if the '&' character has been entered
    flag = concurrent(command)
    # fork a child process form the parent and save the pid to tell the parent and child which code to run
    pid = os.fork()
    # if the current process is the child then execute the command the user enters
    # else check the flag to see if the user want to run the parent and child concurrently
    if pid == 0:
        #print("child process: " + str(os.getpid()))
        file_operation(command)
        os.execvp(command[0], command)
    else:
        if not flag:
            #print("parent process: " + str(os.getpid()))
            os.waitpid(pid, 0)
        else:
            print("parent process running concurrently with child")
            #print("parent process: " + str(os.getpid()))

#function to feed the output of one command into another
def do_Pipe(command):     
    #create two pipes to pass information to the child processes
    pipeout,pipein = os.pipe()
    #find the position of the pipe and then split up the command list into the two seperate commands
    #using the position of the pipe in the list
    position = command.index('|')
    cmd1 = command[:position]
    cmd2 = command[position:]
    #remove the pipe from the cmd2 list
    cmd2.pop(cmd2.index('|'))
    #if there was an error open either pipe print an error
    if(pipein == -1) or (pipeout == -1):
        print("An error occured with opening the pipe\n")

    #create the first child process. then create the childs's chilld process and execute the first half of the command
    # after that execute the second half
    pid1 = os.fork()
    if (pid1 == 0):
        #child process 1
        pid2 = os.fork()
        if pid2 == 0:
            #child process 2
            #execute the first half of the command and pass the output throught the pipe
            os.dup2(pipein, sys.stdout.fileno())
            #close both pipe for the grandchild process
            os.close(pipein)
            os.close(pipeout)
            os.execvp(cmd1[0], cmd1)
        #grap the out put of the first half of the command and use it to execute the second half
        os.dup2(pipeout, sys.stdin.fileno())    
        os.execvp(cmd2[0], cmd2) 
        os.wait()
        os.close(pipein)
        os.close(pipeout)
    else: 
        os.wait()      
    #close both pipes 
    os.close(pipein)
    os.close(pipeout)
    #tell the parent to wait for both child processes to finish before proceeding 
    os.wait()
    

def main():
    line = ""
    history = []
    # running loop. keep going until the user enters exit
    while True:
        time.sleep(.5)
        line = input('Python Shell>')
        if line == 'exit':
            sys.exit()
        #if save the ouput of the function in case line has change due to user not entering anything
        line = check_Input(line)
        # splice up the commands into a list. the .split() function creates a list and separates by blank space
        command = line.split()
        #if user enters '!!' execute the last command entered.
        command = execute_Last(command, history)
        history.append(line)

        if '|' in command:
            do_Pipe(command)
        else:
            run_child(command)
        
if __name__ == "__main__":
    main()
