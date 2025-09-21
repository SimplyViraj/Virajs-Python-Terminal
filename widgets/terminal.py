from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import subprocess as sp
import os, time, platform, shutil, socket, getpass, multiprocessing, tkinter, sys, ctypes
import webbrowser as web
import datetime as dt
from time import gmtime, strftime
from transformers import pipeline
import re

nlp_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class Terminal(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.hasRunningProcess = False
        self.command = ''
        self.settings = {}
        self.oldHistory = []
        self.newHistory = []
        self.prompt = ''
        self.__os__ = platform.system()
        self._set()
        self._readHistory()
        self._init_cli()
        self.cwd = os.getcwd()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.history_path = os.path.join(self.project_root, "assets", "history", "data.txt")
        self.nlp_mode = False   # track whether natural mode is active
        self.supported_cmds = {
    "show current directory": "curDir",
    "print working directory": "curDir",
    "current folder": "curDir",
    "what time is it": "time",
    "date": "date",
    "show ip": "ip",
    "my ip": "ip",
    "which os": "os",
    " what is os version": "osver",
    "python version": "pyver",
    "list files": "ls",
    "clear screen": "clear",
    "help": "help",
    "exit terminal": "exit",
    "create a file": "mkfil",
    "make a new file": "mkfil",
    "add file": "mkfil",
    "read a file": "readFil",
    "open a file": "readFil",
    "read file content": "readFil",
    "read binary file": "readBinFil",
    "delete a file": "del",
    "remove a file": "del",
    "rename a file": "rename",
    "move a file": "move",
    
    # Directory operations
    "create a directory": "mkdir",
    "make a new directory": "mkdir",
    "add folder": "mkdir",
    "delete a directory": "delDir",
    "remove a directory": "delDir",
    "list directory contents": "ls",
    "show directories": "ls",
    "change directory": "cd",
}


    def _set(self):
        self.cursor = self.textCursor()
        self.setStyleSheet(
            'color: white; border-radius: 0; background-color: black; font-size: 15px;')
        self.setUndoRedoEnabled(False)
        self._setText()

    def _setText(self, text=None):
        # Always reload the prompt from settings before displaying the prompt
        self._promptUpdate()
        if text is None:
            text = self.prompt if self.prompt else "$"
        self.text = f'<span style="color: green; font-size: 16px;">{text}</span> '
        self.appendHtml(self.text)
        self.startPos = self.textCursor().positionInBlock()

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Backspace:
            pos = self.cursor.positionInBlock()
            if pos <= self.startPos:
                e.ignore()
            else:
                QPlainTextEdit.keyPressEvent(self, e)
        elif k == Qt.Key_Return:
            line = self.document().lastBlock().text()
            cmd = line[self.startPos:].strip()
            self.command = cmd
            self.newHistory.append(self.command)
            self._writeCommand(self.command)
            self._handle_command(self.command)
        elif k == Qt.Key_Up:
            if self.cursor.hasSelection():
                self.cursor.removeSelectedText()
                self.cursor.insertHtml(self.text)
                self.cursor.insertText(self.newHistory[-1])
            return
        else:
            QPlainTextEdit.keyPressEvent(self, e)
            self.cursor.select(QTextCursor.LineUnderCursor)

    def _init_cli(self):
        # Setup prompt and color
        self._setupColor()
        self._promptUpdate()
        self._show_title()

    def _show_title(self):
        self.appendPlainText('@------------------------------------------------------------------------------------@')
        self.appendPlainText('|                                  Viraj\'s Python Terminal                       |')
        self.appendPlainText('@------------------------------------------------------------------------------------@')
        self.appendPlainText('')
        # Blank line for spacing

    def _setupColor(self):
        try:
            f = open('user_data/settings/color.txt', 'r')
            os.system(f.read())
        except:
            os.system('color 0A')

    def _promptUpdate(self):
        if self._fileExists('user_data/settings'):
            if self._fileExists('user_data/settings/prompt.txt'):
                self.prompt = open('user_data/settings/prompt.txt', 'r').read()
            else:
                f = open('user_data/settings/prompt.txt', 'x')
                f.write('>')
                f.close()
                self.prompt = '>'
        else:
            os.makedirs('user_data/settings', exist_ok=True)
            f = open('user_data/settings/prompt.txt', 'x')
            f.write('>')
            f.close()
            self.prompt = '>'

    def _fileExists(self, name):
        return os.path.exists(name)

    def _flt(self, param):
        return float(param)
    
    # def _nlp_interpret(self, sentence: str) -> str:
    #     candidate_labels = list(self.supported_cmds.values())
    #     result = nlp_classifier(sentence, candidate_labels)
    #     best_label = result["labels"][0]
    #     score = result["scores"][0]
    #     if score > 0.6:  # confidence threshold
    #         return best_label
    #     return None
    def _nlp_interpret(self, sentence: str) -> str:
        candidate_labels = list(self.supported_cmds.keys())  # natural language labels
        result = nlp_classifier(sentence, candidate_labels)
        
        best_label = result["labels"][0]
        score = result["scores"][0]
        print("NLP DEBUG:", sentence, "=>", result)

        if score > 0.2:  # threshold
            return self.supported_cmds[best_label]  # return actual command
        return None


    
    def _handle_command(self, cmd):
        try:
            if self.nlp_mode and cmd not in ("mode normal", "mode natural"):
                mapped_cmd = self._nlp_interpret(cmd)
                if mapped_cmd:
                    self.appendPlainText(f"[Natural → {mapped_cmd}]")
                    cmd = mapped_cmd
                    self.nlp_mode = False  # switch back to normal mode after one command
                    self._handle_command(cmd)
                    self.nlp_mode= True  # recursively handle the mapped command
                else:
                    self.appendPlainText("Sorry, I didn’t understand that.")
                    self._setText(self.prompt)
                    
            elif cmd == 'help':
                self.appendPlainText('changelog                               Shows PyTerm\'s change log')
                self.appendPlainText('color                                   Changes the text and the background color')
                self.appendPlainText('exit, terminate                         Close the terminal window')
                self.appendPlainText('clear, cls                              Clear the terminal screen')
                self.appendPlainText('history                                  Show command history')
                self.appendPlainText('curDir                                  Show current directory')
                self.appendPlainText('date, time                              Show current date and time')
                self.appendPlainText('ip                                       Show local IP address')
                self.appendPlainText('os                                       Show operating system name')
                self.appendPlainText('osver                                    Show operating system version')
                self.appendPlainText('pyver                                    Show Python version')
                self.appendPlainText('repo                                      Open PyTerm repository in browser')
                self.appendPlainText('ver, version                             Show PyTerm version')
                self.appendPlainText('systeminfo, sysinfo                     Show system information')
                self.appendPlainText('mkdir, md                                Create a new directory (not supported in GUI)')
                self.appendPlainText('\nRead the docs for more commands\n')
                self.appendPlainText('help -a, help --alt                    Show alternate help')
            elif cmd in ('help -a', 'help --alt'):
                self.appendPlainText('changelog    Shows PyTerm\'s change log (../change.log)')
                self.appendPlainText('color        Changes the text and background color (user_data/settings/color.txt)')
                self.appendPlainText('exit         Close the terminal window')
                self.appendPlainText('clear, cls   Clear the terminal screen')
                self.appendPlainText('history      Show command history')
                self.appendPlainText('curDir       Show current directory')
                self.appendPlainText('date, time   Show current date and time')
                self.appendPlainText('ip            Show local IP address')
                self.appendPlainText('os            Show operating system name')
                self.appendPlainText('osver         Show operating system version')
                self.appendPlainText('pyver         Show Python version')
                self.appendPlainText('repo         Open PyTerm repository in browser')
                self.appendPlainText('ver, version  Show PyTerm version')
                self.appendPlainText('systeminfo, sysinfo  Show system information')
                self.appendPlainText('mkdir, md     Create a new directory (not supported in GUI)')
                self.appendPlainText('help -h, help --help, help /?  Show this help message')
            elif cmd in ('help -h', 'help --help', 'help /?'):
                self.appendPlainText('Usage: help [-a]')
                self.appendPlainText('Parameters:')
                self.appendPlainText('    -a  or  --alt      Prints help message another way')
            elif cmd in ('mkdir', 'md'):
                dir_name, ok = QInputDialog.getText(self, "Create Directory", "Directory name?")
                if ok and dir_name:
                    try:
                        os.mkdir(dir_name)
                        self.appendPlainText(f"Successfully created {dir_name}")
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd == 'mkfil':
                file_name, ok = QInputDialog.getText(self, "Create File", "Full file name?")
                if ok and file_name:
                    try:
                        with open(file_name, 'x') as f:
                            self.appendPlainText(f"Successfully created {file_name}")
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd == 'readFil':
                file_name, ok = QInputDialog.getText(self, "Read File", "Full file name or directory?")
                if ok and file_name:
                    if os.path.exists(file_name):
                        try:
                            with open(file_name, 'r') as f:
                                self.appendPlainText(f.read())
                        except Exception as e:
                            self.appendPlainText(f"Error: {e}")
                    else:
                        self.appendPlainText("The file does not exist!")
            elif cmd == 'readBinFil':
                file_name, ok = QInputDialog.getText(self, "Read Binary File", "Full binary file name or directory?")
                if ok and file_name:
                    if os.path.exists(file_name):
                        try:
                            with open(file_name, 'rb') as f:
                                self.appendPlainText(str(f.read()))
                        except Exception as e:
                            self.appendPlainText(f"Error: {e}")
                    else:
                        self.appendPlainText("The file does not exist!")
            elif cmd == "curDir":
                try:
                    self.appendPlainText(self.cwd)
                except AttributeError:
                    # fallback if self.cwd wasn’t set yet
                    self.cwd = os.getcwd()
                    self.appendPlainText(self.cwd)
                except Exception as e:
                    self.appendPlainText(f"[curDir Error] {str(e)}")

            elif cmd in ('del', 'delete'):
                file_name, ok = QInputDialog.getText(self, "Delete File", "Full file name or directory to delete?")
                if ok and file_name:
                    if os.path.exists(file_name):
                        try:
                            os.remove(file_name)
                            self.appendPlainText(f"Successfully deleted {file_name}")
                        except Exception as e:
                            self.appendPlainText(f"Error: {e}")
                    else:
                        self.appendPlainText("The file does not exist!")
            elif cmd in ('info', 'info -s', 'info --store'):
                info, ok = QInputDialog.getText(self, "Store Info", "Info to store?")
                if ok:
                    os.makedirs('user_data', exist_ok=True)
                    with open('user_data/info.txt', 'a') as f:
                        f.write('\n' + info)
            elif cmd in ('info -o', 'info --overwrite'):
                info, ok = QInputDialog.getText(self, "Overwrite Info", "Info to overwrite?")
                if ok:
                    os.makedirs('user_data', exist_ok=True)
                    with open('user_data/info.txt', 'w') as f:
                        f.write('\n' + info)
            elif cmd in ('info -g', 'info --get'):
                try:
                    with open('user_data/info.txt', 'r') as f:
                        self.appendPlainText(f.read())
                except:
                    self.appendPlainText('No info stored')
            elif cmd in ('info -c', 'info --clear'):
                with open('user_data/info.txt', 'w') as f:
                    f.write('')
            elif cmd in ('info -h', 'info --help', 'info /?'):
                self.appendPlainText('Usage: info [-s] [-g] [-c]')
                self.appendPlainText('    -s  or  --store      Appends info')
                self.appendPlainText('    -g  or  --get        Gets all stored info')
                self.appendPlainText('    -o  or  --overwrite  Overwrites all stored info')
                self.appendPlainText('    -c  or  --clear      Clears stored info')
            elif cmd in ('date', 'time'):
                self.appendPlainText(str(dt.datetime.now()))
            elif cmd == 'openLink':
                link, ok = QInputDialog.getText(self, "Open Link", "Link?")
                if ok and link:
                    web.open(link)
            elif cmd in ('clear', 'cls', 'CLS'):
                self.clear()
            elif cmd in ('exit', 'terminate'):
                self.appendPlainText('Use the window close button to exit.')
            elif cmd in ('ping',):
                host, ok = QInputDialog.getText(self, "Ping", "IP address to ping?")
                if ok and host:
                    param = '-n' if platform.system().lower() == 'windows' else '-c'
                    command = ['ping', param, '4', host]
                    result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
                    out, err = result.communicate()
                    self.appendPlainText(out.decode() if out else err.decode())
            elif cmd in ('systeminfo', 'sysinfo'):
                self.appendPlainText('System information\n')
                self.appendPlainText('Full OS name: '+platform.system()+' '+platform.version())
                self.appendPlainText('OS name: '+platform.system())
                self.appendPlainText('OS version: '+platform.version())
                self.appendPlainText('Computer name: '+socket.gethostname())
                self.appendPlainText('Username: '+getpass.getuser())
                self.appendPlainText('Timezone: '+strftime('%Z', gmtime()))
                self.appendPlainText('Logical processors: '+str(multiprocessing.cpu_count()))
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                self.appendPlainText('IP address: '+ip+'\n')
            elif cmd in ('systeminfo -a', 'systeminfo --alt', 'sysinfo -a', 'sysinfo --alt'):
                self.appendPlainText('You are on '+platform.system()+' version '+platform.release()+' using the computer name '+socket.gethostname()+' and user '+getpass.getuser()+', in the timezone '+strftime('%Z', gmtime())+', and with '+str(multiprocessing.cpu_count())+' logical processors ')
            elif cmd in ('systeminfo -h', 'systeminfo --help', 'systeminfo /?', 'sysinfo -h', 'sysinfo --help', 'sysinfo /?'):
                self.appendPlainText('Usage:    systeminfo [-a]')
                self.appendPlainText('Parameters:')
                self.appendPlainText('    -a  or  --alt      Prints systeminfo another way')
            elif cmd == 'shutdown':
                if self.__os__ == 'nt':
                    os.system('shutdown -s')
                else:
                    os.system('sudo shutdown now')
            elif cmd == 'restart':
                if self.__os__ == 'nt':
                    os.system('shutdown -r')
                else:
                    os.system('sudo shutdown -r')
            elif cmd == 'reset':
                self.clear()
                self._show_title()
            elif cmd.startswith("cd"):
                parts = cmd.split(maxsplit=1)
                if len(parts) == 1 or parts[1] == "~":
                    new_dir = os.path.expanduser("~")
                else:
                    new_dir = os.path.expanduser(parts[1])
                try:
                    os.chdir(new_dir)
                    self.cwd = os.getcwd()   # always normalize to absolute path
                    self.appendPlainText(f"Changed directory to {self.cwd}")
                except Exception as e:
                    self.appendPlainText(f"[cd Error] {str(e)}")

            elif cmd == 'echo':
                msg, ok = QInputDialog.getText(self, "Echo", "Message to echo?")
                if ok:
                    self.appendPlainText(msg)
            elif cmd == 'copy':
                src, ok1 = QInputDialog.getText(self, "Copy File", "Full file or directory name to copy?")
                dst, ok2 = QInputDialog.getText(self, "Copy File", "Directory path to copy it to?")
                if ok1 and ok2 and src and dst:
                    try:
                        shutil.copy(src, dst)
                        self.appendPlainText(f"Copied {src} to {dst}")
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd == 'find':
                file, ok1 = QInputDialog.getText(self, "Find Text", "Full file or directory path to find text?")
                if ok1 and file and os.path.exists(file):
                    text, ok2 = QInputDialog.getText(self, "Find Text", "Text to find?")
                    if ok2 and text:
                        try:
                            with open(file, 'r') as f:
                                content = f.read()
                                idx = content.find(text)
                                self.appendPlainText(f'First appearance of the word {text} is found at character {idx}')
                        except Exception as e:
                            self.appendPlainText(f"Error: {e}")
                else:
                    self.appendPlainText("File does not exist!")
            elif cmd == 'color':
                bgColor, ok1 = QInputDialog.getText(self, "Color", "Background color (0-F)?")
                fgColor, ok2 = QInputDialog.getText(self, "Color", "Text color (0-F)?")
                if ok1 and ok2 and bgColor and fgColor:
                    try:
                        os.system('color '+bgColor+fgColor)
                        os.makedirs('user_data/settings', exist_ok=True)
                        with open('user_data/settings/color.txt', 'w') as f:
                            f.write('color '+bgColor+fgColor)
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd in ('delDir', 'rm'):
                dir_name, ok = QInputDialog.getText(self, "Delete Directory", "Directory of the folder to delete?")
                if ok and dir_name and os.path.exists(dir_name):
                    try:
                        os.rmdir(dir_name)
                        self.appendPlainText(f"Deleted directory {dir_name}")
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
                else:
                    self.appendPlainText("Not a valid directory of a folder!")
            elif cmd == 'rename':
                old, ok1 = QInputDialog.getText(self, "Rename File", "Full path of the file to rename?")
                new, ok2 = QInputDialog.getText(self, "Rename File", "Full new path for the file?")
                if ok1 and ok2 and old and new:
                    try:
                        os.rename(old, new)
                        self.appendPlainText(f"Renamed {old} to {new}")
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd in ('dir', 'ls'):
                dir_path, ok = QInputDialog.getText(self, "Directory", "Directory?")
                if ok and dir_path:
                    try:
                        self.appendPlainText(', '.join(os.listdir(dir_path)))
                    except Exception as e:
                        self.appendPlainText(f"Error: {e}")
            elif cmd in ('dirRoot',):
                try:
                    self.appendPlainText(', '.join(os.listdir('\\')))
                except Exception as e:
                    self.appendPlainText(f"Error: {e}")
            elif cmd == 'cmd':
                if platform.system() == 'Windows':
                    os.system('start cmd')
                else:
                    self.appendPlainText('Error! The "cmd" function only works for Windows!')
            elif cmd == 'ip':
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                self.appendPlainText(ip)
            elif cmd == 'openWindow':
                window_name, ok = QInputDialog.getText(self, "Open Window", "Window name?")
                if ok and window_name:
                    import tkinter
                    window = tkinter.Tk()
                    window.title(window_name)
                    window.mainloop()
            elif cmd in ('changePrompt', 'prompt'):
                prompt, ok = QInputDialog.getText(self, "Change Prompt", "New prompt?")
                if ok and prompt:
                    os.makedirs('user_data/settings', exist_ok=True)
                    with open('user_data/settings/prompt.txt', 'w') as f:
                        f.write(prompt)
            elif cmd == 'exists':
                path, ok = QInputDialog.getText(self, "Exists", "Directory of file or folder?")
                if ok and path:
                    self.appendPlainText(str(os.path.exists(path)))
            elif cmd == 'math -a' or cmd == 'math --add':
                n1, ok1 = QInputDialog.getText(self, "Math Add", "Number one?")
                n2, ok2 = QInputDialog.getText(self, "Math Add", "Number two?")
                try:
                    numOne = float(n1)
                    numTwo = float(n2)
                    self.appendPlainText(f"{numOne} + {numTwo} = {numOne + numTwo}")
                except:
                    self.appendPlainText("Error! Please make sure you entered valid numbers")
            elif cmd == 'math -s' or cmd == 'math --subtract':
                n1, ok1 = QInputDialog.getText(self, "Math Subtract", "Number one?")
                n2, ok2 = QInputDialog.getText(self, "Math Subtract", "Number two?")
                try:
                    numOne = float(n1)
                    numTwo = float(n2)
                    self.appendPlainText(f"{numOne} - {numTwo} = {numOne - numTwo}")
                except:
                    self.appendPlainText("Error! Please make sure you entered valid numbers")
            elif cmd == 'math -m' or cmd == 'math --multiply':
                n1, ok1 = QInputDialog.getText(self, "Math Multiply", "Number one?")
                n2, ok2 = QInputDialog.getText(self, "Math Multiply", "Number two?")
                try:
                    numOne = float(n1)
                    numTwo = float(n2)
                    self.appendPlainText(f"{numOne} * {numTwo} = {numOne * numTwo}")
                except:
                    self.appendPlainText("Error! Please make sure you entered valid numbers")
            elif cmd == 'math -d' or cmd == 'math --divide':
                n1, ok1 = QInputDialog.getText(self, "Math Divide", "Number one?")
                n2, ok2 = QInputDialog.getText(self, "Math Divide", "Number two?")
                try:
                    numOne = float(n1)
                    numTwo = float(n2)
                    self.appendPlainText(f"{numOne} / {numTwo} = {numOne / numTwo}")
                except ZeroDivisionError:
                    self.appendPlainText("Error! Please make sure the divisor isn't zero!")
                except:
                    self.appendPlainText("Error! Please make sure you entered valid numbers")
            elif cmd in ('ver', 'version'):
                self.appendPlainText('PyTerm v0.5.2')
            elif cmd == 'notepad':
                if self.__os__ == 'Windows':
                    sp.Popen('notepad.exe')
                else:
                    self.appendPlainText('Sorry, notepad is only for Windows!')
            elif cmd == 'py':
                if self.__os__ == 'Windows':
                    os.system('start cmd /c py')
                else:
                    self.appendPlainText('Sorry, the "py" command is only for Windows!')
            elif cmd == 'license':
                if os.path.exists('../LICENSE.txt'):
                    with open('../LICENSE.txt', 'r') as f:
                        self.appendPlainText(f.read())
                else:
                    self.appendPlainText('Could not find license!')
            elif cmd == 'os':
                self.appendPlainText(platform.system())
            elif cmd == 'osver':
                self.appendPlainText(platform.version())
            elif cmd == 'netstat':
                self.appendPlainText(str(os.system('netstat')))
            elif cmd == 'diskpart':
                if self.__os__ == 'Windows':
                    os.system('diskpart')
                else:
                    self.appendPlainText('Error!, diskpart is only for Windows')
            elif cmd == 'TASKKILL':
                proc, ok = QInputDialog.getText(self, "TASKKILL", "Program file name?")
                if ok and proc:
                    os.system("taskkill /F /im "+proc)
            elif cmd == 'runPy':
                pyfile, ok = QInputDialog.getText(self, "Run Python", "Directory of Python file to run?")
                if ok and pyfile:
                    if self.__os__ == 'Windows':
                        os.system('start cmd /c py '+pyfile)
                    elif self.__os__ == 'Linux':
                        os.system('start gnome-terminal python '+pyfile)
                    elif self.__os__ == 'Darwin':
                        os.system('start open -a Terminal python '+pyfile)
                    else:
                        self.appendPlainText('OS is not recognized!')
            elif cmd == 'move':
                curFil, ok1 = QInputDialog.getText(self, "Move File", "Path/directory to current file to move?")
                newFil, ok2 = QInputDialog.getText(self, "Move File", "Path/directory to new file?")
                if ok1 and ok2 and curFil and newFil:
                    try:
                        os.rename(curFil, newFil)
                    except:
                        self.appendPlainText('Error! Make sure both directories are valid and no programs are using the file.')
            elif cmd == 'tree':
                dir_path, ok = QInputDialog.getText(self, "Tree", "Directory (backslash for root)?")
                if ok and dir_path:
                    os.system('tree '+str(dir_path))
            elif cmd == 'pyver':
                self.appendPlainText('Python '+platform.python_version())
            elif cmd == 'npm install':
                pkgName, ok = QInputDialog.getText(self, "npm install", "Package name?")
                if ok and pkgName:
                    os.system('npm install '+pkgName)
            elif cmd in ('npm upgrade', 'npm install -U', 'npm update'):
                pkgName, ok = QInputDialog.getText(self, "npm upgrade", "Package name?")
                if ok and pkgName:
                    os.system('npm install '+pkgName)
            elif cmd == 'pip install':
                pkgName, ok = QInputDialog.getText(self, "pip install", "Package name?")
                if ok and pkgName:
                    os.system('pip install '+pkgName)
            elif cmd in ('pip install -U', 'pip update', 'pip upgrade'):
                pkgName, ok = QInputDialog.getText(self, "pip upgrade", "Package name?")
                if ok and pkgName:
                    os.system('pip install -U '+pkgName)
            elif cmd == 'git clone':
                repoURL, ok1 = QInputDialog.getText(self, "git clone", "Repository url?")
                repoPath, ok2 = QInputDialog.getText(self, "git clone", "Directory to clone it to?")
                repoName, ok3 = QInputDialog.getText(self, "git clone", "Name to clone it as?")
                if ok1 and ok2 and ok3 and repoURL and repoPath and repoName:
                    os.system('cd '+repoPath+' & git clone '+repoURL+' '+repoName)
            elif cmd == 'title':
                if self.__os__ == 'Windows':
                    title, ok = QInputDialog.getText(self, "Console Title", "Name for new window title?")
                    if ok and title:
                        ctypes.windll.kernel32.SetConsoleTitleW(title)
                else:
                    self.appendPlainText('This function is only for Windows!')
            elif cmd == 'msgbox':
                if self.__os__ == 'Windows':
                    title, ok1 = QInputDialog.getText(self, "MsgBox", "Title?")
                    msg, ok2 = QInputDialog.getText(self, "MsgBox", "Message?")
                    if ok1 and ok2:
                        ctypes.windll.user32.MessageBoxW(0, msg, title, 0)
                else:
                    self.appendPlainText('This function is only for Windows!')
            elif cmd == 'openFil':
                fileName, ok = QInputDialog.getText(self, "Open File", "Path to file?")
                if ok and fileName and os.path.exists(fileName):
                    try:
                        sp.Popen(['open', fileName], check=True)
                    except:
                        self.appendPlainText('Error! Something went wrong! Please try again!')
                else:
                    self.appendPlainText('That file does not exist! Please try again with another file')
            elif cmd == 'deleteuserdata':
                reply = QMessageBox.question(self, 'Delete User Data', 'Are you sure you want to delete all user data?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if os.path.exists('user_data'):
                        try:
                            shutil.rmtree('user_data')
                            self.appendPlainText('Clearing data . . .')
                            time.sleep(0.5)
                            self.appendPlainText('Finished!')
                        except:
                            self.appendPlainText('There was an error clearing the data!')
                    else:
                        self.appendPlainText('There are no data to clear!')
            elif cmd == 'cache':
                try:
                    with open('user_data/cache.txt', 'r') as f:
                        self.appendPlainText(f.read())
                except:
                    self.appendPlainText('There is no current cache value!')
            elif cmd == 'refresh':
                self.clear()
                self._init_cli()
            elif cmd in ('powershell', 'ps'):
                try:
                    os.system('start powershell')
                except:
                    self.appendPlainText('Error! Make sure you have PowerShell installed!')
            elif cmd.strip() == '':
                pass
            elif cmd == "mode natural":
                self.nlp_mode = True
                self.appendPlainText("Natural mode enabled. Type instructions in plain English.")
            elif cmd == "mode normal":
                self.nlp_mode = False
                self.appendPlainText("Natural mode disabled. Back to command mode.")

            else:
                # fallback: try to run as shell command
                output = sp.Popen(
                    cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
                result = output.communicate()
                text = result[0] if result[0] else result[1]
                self.appendPlainText(text.decode('utf-8'))
        except Exception as e:
            self.appendPlainText(f"Error: {e}")
        self._setText(self.prompt)

    def _writeCommand(self, command):
        with open(self.history_path, 'a') as f:
            f.write(f'{command}\n')
        self._readHistory()

    def _readHistory(self):
        try:
            with open('./assets/history/data.txt', 'r') as f:
                self.oldHistory = f.read()
        except Exception:
            self.oldHistory = ''
