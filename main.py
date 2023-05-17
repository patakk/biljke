import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import random
import os


def create_connection(db_file):
    db_connection = None
    try:
        db_connection = sqlite3.connect(db_file)
        return db_connection
    
    except sqlite3.Error as db_error:
        print(db_error)
    
    return db_connection


CONNECTION = create_connection('biljke.db')
CURSOR = CONNECTION.cursor()

CURRENT_USER_ID = None
CURRENT_USER_DATA = None


def update_current_user_data():
    # Fetch pots for the user
    CURSOR.execute("SELECT user_pots FROM users WHERE user_id=?", (CURRENT_USER_ID,))
    pot_ids_str = CURSOR.fetchone()[0]
    pot_ids = pot_ids_str.split(',')
    pot_ids_integers = tuple(int(pot_id) for pot_id in pot_ids)

    questionmarks = ', '.join(['?' for _ in pot_ids_integers])
    query = f"SELECT pot_id, plant_id, pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level FROM pots WHERE pot_id IN ({questionmarks})"
    CURSOR.execute(query, pot_ids_integers)
    pots = CURSOR.fetchall()

    # Fetch plant data for each pot
    global CURRENT_USER_DATA
    CURRENT_USER_DATA = {}
    for pot in pots:
        plant_id = pot[1]
        CURSOR.execute("SELECT plant_id, plant_name, plant_optimal_ph, plant_optimal_salinity, plant_min_temp, plant_max_temp, plant_min_soil_moisture, plant_needed_light_level, plant_photo FROM plants WHERE plant_id=?", (plant_id,))
        plant = CURSOR.fetchone()
        pot_with_plant = pot + plant
        pot_with_plant = {
            'pot_id': pot[0],
            'plant_id': pot[1],
            'pot_ph': pot[2],
            'pot_salinity': pot[3],
            'pot_temp': pot[4],
            'pot_soil_moisture': pot[5],
            'pot_light_level': pot[6],
            'plant_name': plant[1],
            'plant_optimal_ph': plant[2],
            'plant_optimal_salinity': plant[3],
            'plant_min_temp': plant[4],
            'plant_max_temp': plant[5],
            'plant_min_soil_moisture': plant[6],
            'plant_needed_light_level': plant[7],
            'plant_photo': plant[8]
        }
        CURRENT_USER_DATA[pot[0]] = pot_with_plant


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Login")
        self.geometry("1500x1000")
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def show_plant_frame(self):
        self.login_frame.pack_forget()
        self.plant_frame = PlantFrame(self)
        self.plant_frame.pack(fill=tk.BOTH, expand=True)


class LoginFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.user_label = ttk.Label(self, text="Username:")
        self.user_label.grid(row=0, column=0, padx=(10, 0), pady=10)

        self.user_entry = ttk.Entry(self)
        self.user_entry.grid(row=0, column=1, padx=(0, 10), pady=10)

        self.pass_label = ttk.Label(self, text="Password:")
        self.pass_label.grid(row=1, column=0, padx=(10, 0), pady=10)

        self.pass_entry = ttk.Entry(self, show="*")
        self.pass_entry.grid(row=1, column=1, padx=(0, 10), pady=10)

        self.login_button = ttk.Button(self, text="Login", command=self.check_login)
        self.login_button.grid(row=2, column=1, padx=(0, 10), pady=(10, 0))

    def check_login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()

        CURSOR.execute("SELECT user_id FROM users WHERE user_name=? AND user_password=?", (user, password))
        result = CURSOR.fetchone()

        if result:
            global CURRENT_USER_ID
            CURRENT_USER_ID = result[0]
            
            update_current_user_data()

            self.master.show_plant_frame()
        else:
            messagebox.showerror("Error", "Invalid username or password.")


class PlantFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.tree = ttk.Treeview(self, columns=("pot_id", "plant_id", "plant_name", "plant_optimal_ph", "plant_optimal_salinity", "plant_min_temp", "plant_max_temp", "plant_min_soil_moisture", "plant_needed_light_level"), show="headings")
        self.tree.heading("pot_id", text="Pot ID")
        self.tree.heading("plant_id", text="Plant ID")
        self.tree.heading("plant_name", text="Plant Name")
        self.tree.heading("plant_optimal_ph", text="Plant pH")
        self.tree.heading("plant_optimal_salinity", text="Plant Salinity")
        self.tree.heading("plant_min_temp", text="Plant Min Temp")
        self.tree.heading("plant_max_temp", text="Plant Max Temp")
        self.tree.heading("plant_min_soil_moisture", text="Plant Soil Moisture")
        self.tree.heading("plant_needed_light_level", text="Plant Light Level")

        self.tree.column("pot_id", width=70, anchor=tk.CENTER)
        self.tree.column("plant_id", width=70, anchor=tk.CENTER)
        self.tree.column("plant_name", width=150, anchor=tk.CENTER)
        self.tree.column("plant_optimal_ph", width=100, anchor=tk.CENTER)
        self.tree.column("plant_optimal_salinity", width=100, anchor=tk.CENTER)
        self.tree.column("plant_min_temp", width=100, anchor=tk.CENTER)
        self.tree.column("plant_max_temp", width=100, anchor=tk.CENTER)
        self.tree.column("plant_min_soil_moisture", width=100, anchor=tk.CENTER)
        self.tree.column("plant_needed_light_level", width=100, anchor=tk.CENTER)

        for pot_id in CURRENT_USER_DATA:
            pwp = CURRENT_USER_DATA[pot_id]
            pot_data = [pwp['pot_id'], pwp['plant_id'], pwp['plant_name'], pwp['plant_optimal_ph'], pwp['plant_optimal_salinity'], pwp['plant_min_temp'], pwp['plant_max_temp'], pwp['plant_min_soil_moisture'], pwp['plant_needed_light_level']] 
            self.tree.insert("", tk.END, values=pot_data)
        self.tree.pack(fill=tk.BOTH, expand=True)

        keys = list(CURRENT_USER_DATA.keys())
        if len(keys) > 0:
            selected_pot_id = keys[0]
            if selected_pot_id is not None:
                for item in self.tree.get_children():
                    if self.tree.item(item)['values'][0] == selected_pot_id:
                        self.tree.selection_set(item)
                        break

        # Dropdown menu for plant selection
        self.selected_plant = tk.StringVar()
        self.plant_names = ['Suncokret', 'Tulipan', 'Ruža']
        self.selected_plant.set(self.plant_names[0])
        self.plant_dropdown = ttk.OptionMenu(self, self.selected_plant, *self.plant_names)
        # self.plant_dropdown.pack(pady=(10, 0))
        self.plant_dropdown.pack()

        # Add button for adding a new pot
        self.add_button = ttk.Button(self, text="Add", command=self.add_pot)
        self.add_button.pack()

        self.lower_frame = tk.Frame(self)
        self.lower_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.lower_frame)
        self.left_frame.grid(row=0, column=0, sticky='nswe')

        self.right_frame = tk.Frame(self.lower_frame)
        self.right_frame.grid(row=0, column=1, sticky='nswe')

        self.lower_frame.grid_columnconfigure(0, weight=1)
        self.lower_frame.grid_columnconfigure(1, weight=1)
        self.lower_frame.grid_rowconfigure(0, weight=1)

        self.logout_button = ttk.Button(self, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT, padx=(0, 30), pady=(0, 10))

        self.sync_button = ttk.Button(self, text="Sync", command=self.sync)
        self.sync_button.pack(side=tk.LEFT, padx=(30, 0), pady=(0, 10))

        self.remove_button = ttk.Button(self, text="Remove", command=self.remove_selected_pot)
        self.remove_button.pack(side=tk.BOTTOM, pady=(0, 10))

        self.tree.bind("<<TreeviewSelect>>", self.display_plant_info_and_image)
        self.image_label = ttk.Label(self.left_frame)
        self.image_label.pack(expand=True)
        
        self.plot_label = ttk.Label(self.right_frame)
        self.plot_label.pack(expand=True)

    
    def plot_data(self, pot_id):
        # Fetch the pot data
        pot_ph = CURRENT_USER_DATA[pot_id]['pot_ph']
        pot_salinity = CURRENT_USER_DATA[pot_id]['pot_salinity']
        pot_temp = CURRENT_USER_DATA[pot_id]['pot_temp']
        pot_soil_moisture = CURRENT_USER_DATA[pot_id]['pot_soil_moisture']
        pot_light_level = CURRENT_USER_DATA[pot_id]['pot_light_level']


        # Prepare the data for plotting
        pot_ph = [float(x) for x in pot_ph.split(',')]
        pot_salinity = [float(x) for x in pot_salinity.split(',')]
        pot_temp = [float(x) for x in pot_temp.split(',')]
        pot_soil_moisture = [float(x) for x in pot_soil_moisture.split(',')]
        pot_light_level = [float(x) for x in pot_light_level.split(',')]
        time_series = list(range(len(pot_ph)))

        # Plot the data
        import matplotlib.pyplot as plt
        plt.figure(figsize=(5,4))
        plt.plot(time_series, pot_ph, marker='o', label='pH')
        plt.plot(time_series, pot_salinity, marker='o', label='Salinity')
        plt.plot(time_series, pot_temp, marker='o', label='Temperature')
        plt.plot(time_series, pot_soil_moisture, marker='o', label='Soil Moisture')
        plt.plot(time_series, pot_light_level, marker='o', label='Light Level')
        plt.legend()
        plt.xlabel('Time')
        plt.title(f'Pot {pot_id} Data Over Time')

        # Save the plot as an image

        if not os.path.exists('pot_data_plots'):
            os.mkdir('pot_data_plots')

        image_path = f'pot_data_plots/pot_{pot_id}_data.png'
        plt.savefig(image_path)
        plt.close()

        # Display the image using a tkinter Label or similar widget
        plot_image = tk.PhotoImage(file=image_path)
        self.plot_label.config(image=plot_image)
        self.plot_label.image = plot_image


    def display_plant_info_and_image(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        pot_id = self.tree.item(selected_item)['values'][0]
        CURSOR.execute("SELECT plant_id, pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level FROM pots WHERE pot_id=?", (pot_id,))
        pot_data = CURSOR.fetchone()
        plant_id = pot_data[0]
        CURSOR.execute("SELECT plant_id, plant_name, plant_optimal_ph, plant_optimal_salinity, plant_min_temp, plant_max_temp, plant_min_soil_moisture, plant_needed_light_level, plant_photo FROM plants WHERE plant_id=?", (plant_id,))
        plant_data = CURSOR.fetchone()
        image_filename = plant_data[-1]

        image_path = f"plant_images/{image_filename}"
        plant_image = tk.PhotoImage(file=image_path)
        self.image_label.config(image=plant_image)
        self.image_label.image = plant_image  


        self.show_data()


    def add_pot(self):
        plant_name = self.selected_plant.get()

        # Get plant ID and optimal values using the plant name
        CURSOR.execute("SELECT plant_id, plant_optimal_ph, plant_optimal_salinity, plant_min_temp, plant_min_soil_moisture, plant_needed_light_level FROM plants WHERE plant_name=?", (plant_name,))
        plant_data = CURSOR.fetchone()
        plant_id = plant_data[0]
        pot_ph = plant_data[1]
        pot_salinity = plant_data[2]
        pot_temp = plant_data[3]
        pot_soil_moisture = plant_data[4]
        pot_light_level = plant_data[5]
        
        # Insert a new pot into the pots table with default values
        CURSOR.execute("INSERT INTO pots (plant_id, pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level) VALUES (?, ?, ?, ?, ?, ?)", (plant_id, pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level))
        CONNECTION.commit()

        # Update the user's pots list
        new_pot_id = CURSOR.lastrowid
        CURSOR.execute("SELECT user_pots FROM users WHERE user_id=?", (CURRENT_USER_ID,))
        user_pots = CURSOR.fetchone()[0]
        updated_user_pots = user_pots + "," + str(new_pot_id)
        CURSOR.execute("UPDATE users SET user_pots=? WHERE user_id=?", (updated_user_pots, CURRENT_USER_ID))
        CONNECTION.commit()

        # Refresh the treeview
        self.tree.delete(*self.tree.get_children())
        update_current_user_data()
        for pot_id in CURRENT_USER_DATA:
            pwp = CURRENT_USER_DATA[pot_id]
            pot_data = [pwp['pot_id'], pwp['plant_id'], pwp['plant_name'], pwp['plant_optimal_ph'], pwp['plant_optimal_salinity'], pwp['plant_min_temp'], pwp['plant_max_temp'], pwp['plant_min_soil_moisture'], pwp['plant_needed_light_level']]     # Extract first 7 columns (pot data and plant name)
            self.tree.insert("", tk.END, values=pot_data)

        if new_pot_id is not None:
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == new_pot_id:
                    self.tree.selection_set(item)
                    break


    def remove_selected_pot(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No pot selected.")
            return

        pot_id = self.tree.item(selected_item)['values'][0]

        CURSOR.execute("DELETE FROM pots WHERE pot_id=?", (pot_id,))
        CONNECTION.commit()

        # Update user_pots in users table
        CURRENT_USER_DATA.pop(pot_id)
        str_keys = [str(key) for key in CURRENT_USER_DATA.keys()]
        pot_ids_str_updated = ','.join(str_keys)
        CURSOR.execute("UPDATE users SET user_pots=? WHERE user_id=?", (pot_ids_str_updated, CURRENT_USER_ID))
        CONNECTION.commit()

        # Remove pot from the tree view
        self.tree.delete(selected_item)
        self.image_label.image = None
        self.plot_label.image = None

    def logout(self):
        self.master.login_frame.user_entry.delete(0, tk.END)
        self.master.login_frame.pass_entry.delete(0, tk.END)
        self.pack_forget()
        self.master.login_frame.pack(side=tk.LEFT)
        

    def sync(self):
        selected_item = self.tree.selection()
        selected_pot_id = None
        if selected_item:
            selected_pot_id = self.tree.item(selected_item)['values'][0]
            
        # Fetch all pot IDs for the current user
        CURSOR.execute("SELECT user_pots FROM users WHERE user_id=?", (CURRENT_USER_ID,))
        pot_ids_str = CURSOR.fetchone()[0]
        pot_ids = pot_ids_str.split(',')

        for pot_id in pot_ids:
            # Fetch current pot data from the database
            CURSOR.execute("SELECT pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level FROM pots WHERE pot_id=?", (pot_id,))
            pot_data = CURSOR.fetchone()

            # Add a random value to each parameter
            updated_pot_data = []
            for value in pot_data:
                if value:
                    new_values = value.split(',')
                    new_values.append(str(float(new_values[-1]) + random.uniform(-0.5, 0.5)))  # Add random fluctuation to the last value
                    updated_value = ','.join(new_values)
                else:
                    updated_value = str(random.uniform(6.0, 7.0))  # If value is None, initialize it with a random number between 6 and 7

                updated_pot_data.append(updated_value)

            # Update the pot data in the database
            CURSOR.execute("UPDATE pots SET pot_ph=?, pot_salinity=?, pot_temp=?, pot_soil_moisture=?, pot_light_level=? WHERE pot_id=?",
                        (*updated_pot_data, pot_id))
        CONNECTION.commit()

        # Refresh the treeview
        self.tree.delete(*self.tree.get_children())
        update_current_user_data()
        for pot_id in CURRENT_USER_DATA:
            pwp = CURRENT_USER_DATA[pot_id]
            pot_data = [pwp['pot_id'], pwp['plant_id'], pwp['plant_name'], pwp['plant_optimal_ph'], pwp['plant_optimal_salinity'], pwp['plant_min_temp'], pwp['plant_max_temp'], pwp['plant_min_soil_moisture'], pwp['plant_needed_light_level']]  # Extract first 7 columns (pot data and plant name)
            self.tree.insert("", tk.END, values=pot_data)

        self.plot_data(selected_pot_id)
        if selected_pot_id is not None:
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == selected_pot_id:
                    self.tree.selection_set(item)
                    break
    
    
    def show_data(self):
        selected_item = self.tree.selection()
        selected_pot_id = None
        if selected_item:
            selected_pot_id = self.tree.item(selected_item)['values'][0]
            
        if selected_pot_id is not None:
            self.plot_data(selected_pot_id)
    


if __name__ == '__main__':
    app = Application()
    app.mainloop()

    # Close the cursor and the connection
    CURSOR.close()
    CONNECTION.close()
