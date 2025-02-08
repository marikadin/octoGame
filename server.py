import json
import socket
import asyncio
from googletrans import Translator
import random
import time
class Game:


     def __init__(self):
          self.player = None
          self.rnd= random.randint(0,102)
          self.languages = None
          Game.GetLangs(self)
          self.languagesNames = list(self.languages.keys())
          self.lang = self.languages[str(self.languagesNames[self.rnd])]
          self.done = Game.Handle_Sockets(self)
          if self.done:
               sock = socket.socket()
               sock.bind(('', 5555))
               while True:
                    sock.listen(5)
                    conn, clt_address = sock.accept()
                    print('now: ', clt_address)
                    conn.send(f"Do you want to play another game?".encode())
                    answer = conn.recv(2048).decode()
                    if answer == "yes":
                         sock.close()
                         time.sleep(1)
                         Game.__init__(self)
                    else:
                         sock.close()
                         exit()

     def GetLangs(self) -> None :
          with open("langs.json" , "r") as file:
               langs = json.load(file)
          self.languages = langs


     async def translate_text(self,text: str) -> str:
         translator = Translator()
         result = await translator.translate(text, dest=self.lang)
         return (result.text)


     def Handle_Sockets(self) -> True :
          new_socket = socket.socket()
          port =5555
          new_socket.bind(('', port))
          new_socket.listen(5)
          while True:
               conn, clt_address = new_socket.accept()
               print('Connection established: ', clt_address)
               conn.send("State your username ".encode())
               self.player = conn.recv(2048).decode()
               with open("database.json", 'r') as file:
                    data = json.load(file)

               if self.player not in data.keys():
                    data[self.player] = [0, 0]

               with open("database.json", 'w') as file:  # Write the modified data back to the file
                    json.dump(data, file, indent=4)
               conn.send("Say the text to translate in English: ".encode())
               text = conn.recv(2048).decode()
               conn.send( f"{text} in another language is: {asyncio.run(self.translate_text(text))}\nGuess the language of the translated text!\nChoose the correct language of the following: ".encode())

               options = [self.languagesNames[self.rnd]]
               for i in range(3):
                    newlang= self.languagesNames[random.randint(0,102)]
                    while newlang in options:
                         newlang = self.languagesNames[random.randint(0, 102)]
                    options.append(newlang)

               random.shuffle(options)

               answer=0

               for i in range(4):
                    if options[i] == self.languagesNames[self.rnd]:
                         answer = i
                         break
               conn.send(f"1. {options[0]}\n2. {options[1]}\n3. {options[2]}\n4. {options[3]}\nThe answer is: ".encode())
               print(f"correct answer: {answer+1}")
               guess = conn.recv(2048).decode()
               if int(guess) == answer+1:
                    conn.send("Correct!".encode())
                    with open("database.json", 'r') as file:
                         data = json.load(file)
                         data[self.player][0]+=1  # Initialize the list for the player

                    with open("database.json", 'w') as file:  # Write the modified data back to the file
                         json.dump(data, file, indent=4)
               else:
                    conn.send(f"Incorrect! language is {self.languagesNames[self.rnd]}".encode())
                    with open("database.json", 'r') as file:
                         data = json.load(file)
                         data[self.player][1] += 1

                    with open("database.json", 'w') as file:  # Write the modified data back to the file
                         json.dump(data, file, indent=4)


               conn.close()
               return True

if __name__ == "__main__":
    game= Game()


    