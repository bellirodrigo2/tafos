import cmd, sys

# estudar cmdparser, cmd e argparser
# https://pypi.org/project/cmdparser/
# https://docs.python.org/3/library/argparse.html

class TafosShell(cmd.Cmd):
    intro = 'Welcome to the "tafos" shell.   Type help or ? to list commands.\n'
    # user = ''
    # prompt = 'tafos> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.mode = None
        self.__update_user(None)

    def __update_user(self, user):
        self.user = user
        user_str = '' if self.user is None else self.user
        self.prompt = 'tafos' + user_str + '>'
    
    def __update_mode(self, mode):
        if self.user is None:
            return False
        self.mode = mode
        self.prompt = self.prompt[:-1]
        self.prompt += '|' + mode + '>'

    def precmd(self, line):
        line = line.split()
        line[0] = line[0].upper()
        l = ''
        for word in line:
            l += word + ' '
        return l
    
    # ----- tafos user commands -----
    def do_USER(self, arg):
        'Select a user and provide a password:  USER ADMIN PASSWORD123'
        line_list = arg.strip().split(' ')
        if len(line_list) !=2:
            self.stdout.write(f'[-] User command requires 2 arguments, but {len(line_list)} was/were given.\n')
            return
        # CHECAR LEN(LINE_LIST) TEM QUE SER = 2
        user, psw = line_list
        # VALIDAR PSWD
        self.__update_user('|' + user)
    
    def do_CREATEUSER(self, arg):
        'Create an user, given a username and password:  CREATEUSER ADMIN PASSWORD123'
        user, psw = arg.strip().split(' ')
        print(user, psw)
    
    def do_DELETEUSER(self, arg):
        'Delete an user, given a username and password:  DELETEUSER ADMIN PASSWORD123'
        user, psw = arg.strip().split(' ')
        print(user, psw)
    
    def do_CHANGEPASSWORD(self, arg):
        'Change a user´s password after logged in:  CHANGEPASSWORD PASSWORD123'
        user, psw = arg.strip().split(' ')
        print(user, psw)
        
    # ----- tafos tree commands -----
    
    def do_SELECT(self, arg):
        'Change between template builder and nodes builder:  SELECT <node/template>'
        self.__update_mode(arg)
        # make a tree here...
    
    def do_LS(self, arg):
        # print successors
        pass
    
    def do_MKDIR(self, arg):
        #
        pass
    
    def do_CD(self, arg):
        pass
    
if __name__ == '__main__':
    TafosShell().cmdloop()