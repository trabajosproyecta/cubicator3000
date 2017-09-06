from backend import start
from tkinter import Tk, N,GROOVE,END
from tkinter.ttk import Frame,Button,Style,Label,Entry
from tkinter.filedialog import askopenfilename,askdirectory
from os import path


class Gui(Frame):
    def __init__(self,root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        self.master.title("Cubicator3000")
        self.style = Style()
        self.center_window()

        self.columnconfigure(0, pad=10)
        self.columnconfigure(1, pad=10)
        self.columnconfigure(2, pad=10)

        self.rowconfigure(0, pad=10)
        self.rowconfigure(1, pad=10)
        self.rowconfigure(2, pad=10)
        self.rowconfigure(3, pad=10)
        self.rowconfigure(4, pad=10)

        label_title = Label(self,text="Cubicador Proyecta!",background="white",foreground="cyan",width=25,anchor=N,
                            borderwidth=5,relief=GROOVE,font=("default",16,"bold"))
        label_title.grid(row=0,columnspan=3)

        label_input = Label(self, text="Excel a cubicar")
        label_input.grid(row=1, column=0)
        self.entry_input = Entry(self)
        self.entry_input.grid(row=1, column=1)
        input_button = Button(self,text="Abrir",command=lambda:self.get_excel_file(self.entry_input))
        input_button.grid(row=1,column=2)

        label_output = Label(self, text="Guardar resultados en")
        label_output.grid(row=2, column=0)
        self.entry_output = Entry(self)
        self.entry_output.grid(row=2, column=1)
        output_button = Button(self, text="Abrir",command=lambda:self.get_dir(self.entry_output))
        output_button.grid(row=2, column=2)

        label_images = Label(self, text="Guardar imágenes en")
        label_images.grid(row=3, column=0)
        self.entry_images = Entry(self)
        self.entry_images.grid(row=3, column=1)
        images_button = Button(self, text="Abrir",command=lambda:self.get_dir(self.entry_images))
        images_button.grid(row=3, column=2)

        self.label_result = Label(self,text="")
        self.label_result.grid(row=4,column=0)

        startButton = Button(self, text="Cubicar!",command=lambda :self.run_optimize())
        startButton.grid(row=4,column=1)
        closeButton = Button(self, text="Salir", command=self.quit)
        closeButton.grid(row=4,column=2)
        self.pack()

    def center_window(self):
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        w = 450
        h = 200

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def get_excel_file(self,entry):
        fname = askopenfilename(filetypes=(("Excel files","*.xls"),("Excel files","*.xlsx")))
        if fname:
            entry.delete(0,END)
            entry.insert(0,fname)

    def get_dir(self,entry):
        dirname = askdirectory()
        if dirname:
            entry.delete(0, END)
            entry.insert(0, dirname)

    def run_optimize(self):
        self.label_result.config(text="Calculando...")
        self.root.update()
        start(self.entry_input.get(), path.join(self.entry_output.get(), "resultado.txt"), self.entry_images.get()+"/")
        self.label_result['text'] = "Listo!"


def main():
    root = Tk()
    ex = Gui(root)
    root.mainloop()


if __name__ == '__main__':
    main()