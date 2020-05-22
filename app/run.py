from tkinter import *

def onFakeSubmit(event):
	print("Fake pressed!")

root = Tk()
root.title("Faker")
root.geometry("1000x1000")

fakeButton = Button(root, text="Fake", background="#555", foreground="#ccc", padx="8", pady="8")
fakeButton.bind("<Button-1>", onFakeSubmit)

fra1 = Frame(root, width=500, height=100, bg="darkred")
fra2 = Frame(root, width=500, height=100, bg="green", bd="20")

fra1.pack()
fra2.pack()
fakeButton.pack()

root.mainloop()