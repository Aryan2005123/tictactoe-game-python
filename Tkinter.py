import tkinter as tk
root = tk.Tk()
root.geometry("600x400")
root.title("Canvas Example")

canvas = tk.Canvas(root, width=400, height=300, bg="white")
canvas.pack(pady=20)
# Draw a line
canvas.create_line(50, 50, 350, 250, fill="blue", width=2)
# Draw a rectangle
canvas.create_rectangle(100, 100, 300, 200, outline="red", width=3)
# Draw an oval
canvas.create_oval(150, 50, 250, 150, outline="green", width=4)
#draw an arc
canvas.create_arc(50, 150, 150, 250, start=0, extent=150, outline="purple", width=2)
# Draw a polygon
canvas.create_polygon(200, 50, 250, 150, 150, 150, fill="yellow", outline="black", width=2)
root.mainloop()
# ------------------------------------------------------------------------------------------------------

label1 = tk.Label(root, )