import tkinter as tk
from tkinter import messagebox
import networkx as nx
from matplotlib.gridspec import GridSpec
from network_analysis import create_activity_network, calculate_critical_path, calculate_sigma_for_critical_path
from calculations import calculate_probability
import matplotlib.pyplot as plt
def draw_combined_output(G, critical_path, critical_activities, mean, sigma, z_score, probability, target):
    # Create a figure with GridSpec layout
    fig = plt.figure(figsize=(14, 8))
    gs = GridSpec(3, 2, figure=fig)  # 3 rows, 2 columns grid
    # Network Diagram Plot
    ax1 = fig.add_subplot(gs[:, 0])  # Full height in the first column
    try:
        pos = nx.planar_layout(G)
    except nx.NetworkXException:
        print("Graph is not planar; using spring layout instead.")
        pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw(G, pos, ax=ax1, with_labels=True, node_size=2000, node_color='skyblue', font_size=12, font_weight='bold', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color='red')
    nx.draw_networkx_edges(G, pos, edgelist=critical_path, edge_color='red', width=2.5)
    ax1.set_title("Activity-on-Edge Network Diagram", fontsize=14)
    # Critical Path Information
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')  # No axis for text display
    critical_path_text = "\n".join([f"{u} → {v}" for u, v in critical_path])
    ax2.text(0.1, 0.8, "Critical Path:", fontsize=12, weight='bold')
    ax2.text(0.1, 0.6, critical_path_text, fontsize=10)
    ax2.text(0.1, 0.4, f"Critical Path Length (Mean): {mean:.2f}", fontsize=10)
    ax2.text(0.1, 0.2, f"Sigma Value: {sigma:.2f}", fontsize=10)
    # Probability Calculation
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')  # No axis for text display
    ax3.text(0.1, 0.8, "Probability Calculation:", fontsize=12, weight='bold')
    ax3.text(0.1, 0.6, f"Target Duration: {target}", fontsize=10)
    ax3.text(0.1, 0.4, f"Z-Score: {z_score:.2f}", fontsize=10)
    ax3.text(0.1, 0.2, f"Probability of Completing on Time: {probability:.4f}", fontsize=10)
    # Show Plot
    plt.tight_layout()
    plt.show()
class ActivityNetworkGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Activity Network Analysis")
        self.activities = []
        self.predecessors = []
        self.times = {}
        self.activity_details = {}
        self.activity_index = 0  # To track the current activity being entered
        self.create_widgets()
    def create_widgets(self):
        # Labels and inputs for the number of activities
        tk.Label(self.master, text="Enter the number of activities:").grid(row=0, column=0, padx=10, pady=5)
        self.num_activities_entry = tk.Entry(self.master)
        self.num_activities_entry.grid(row=0, column=1, padx=10, pady=5)
        # Button to proceed to input each activity's details
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit_num_activities)
        self.submit_button.grid(row=1, columnspan=2, pady=10)
    def submit_num_activities(self):
        try:
            self.num_activities = int(self.num_activities_entry.get())
            self.ask_activity_details(self.activity_index)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of activities.")
    def ask_activity_details(self, activity_index):
        if activity_index >= self.num_activities:
            self.target_duration_window()
            return
        # Create a new window for each activity
        activity_window = tk.Toplevel(self.master)
        activity_window.title(f"Activity {activity_index + 1} Details")
        tk.Label(activity_window, text="Activity Name:").grid(row=0, column=0, padx=10, pady=5)
        activity_name_entry = tk.Entry(activity_window)
        activity_name_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(activity_window, text="Predecessors (comma-separated or 'null'):").grid(row=1, column=0, padx=10, pady=5)
        preds_entry = tk.Entry(activity_window)
        preds_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(activity_window, text="Optimistic Time:").grid(row=2, column=0, padx=10, pady=5)
        optimistic_time_entry = tk.Entry(activity_window)
        optimistic_time_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(activity_window, text="Most Likely Time:").grid(row=3, column=0, padx=10, pady=5)
        most_likely_time_entry = tk.Entry(activity_window)
        most_likely_time_entry.grid(row=3, column=1, padx=10, pady=5)
        tk.Label(activity_window, text="Pessimistic Time:").grid(row=4, column=0, padx=10, pady=5)
        pessimistic_time_entry = tk.Entry(activity_window)
        pessimistic_time_entry.grid(row=4, column=1, padx=10, pady=5)
        def submit_activity():
            try:
                activity = activity_name_entry.get().strip().upper()
                preds = preds_entry.get().strip().upper()
                if preds == "NULL":
                    preds = []
                else:
                    preds = preds.split(",")
                o_time = float(optimistic_time_entry.get())
                m_time = float(most_likely_time_entry.get())
                p_time = float(pessimistic_time_entry.get())
                # Calculate expected time (TE)
                te = (o_time + 4 * m_time + p_time) / 6
                self.activities.append(activity)
                self.predecessors.append(preds)
                self.times[activity] = te
                self.activity_details[activity] = {
                    'optimistic': o_time,
                    'most_likely': m_time,
                    'pessimistic': p_time
                }
                # Close the current activity window
                activity_window.destroy()
                # Move to next activity
                self.activity_index += 1
                self.ask_activity_details(self.activity_index)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid times for all fields.")
        # Button to submit the current activity's details
        tk.Button(activity_window, text="Submit", command=submit_activity).grid(row=5, columnspan=2, pady=10)
    def target_duration_window(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()
        # Get target duration for probability calculation
        tk.Label(self.master, text="Enter the target duration for probability calculation:").grid(row=0, column=0, padx=10, pady=5)
        self.target_entry = tk.Entry(self.master)
        self.target_entry.grid(row=0, column=1, padx=10, pady=5)
        self.final_button = tk.Button(self.master, text="Calculate", command=self.calculate_results)
        self.final_button.grid(row=1, columnspan=2, pady=10)
    def calculate_results(self):
        try:
            target = float(self.target_entry.get())
            # Create network graph
            G, nodes = create_activity_network(self.activities, self.predecessors, self.times)
            E, L, critical_path = calculate_critical_path(G)
            # Calculate sigma value for the critical path
            sigma, critical_activities = calculate_sigma_for_critical_path(critical_path, nodes, self.activity_details)
            # Calculate critical path length (mean)
            mean = sum(self.times[activity] for activity in critical_activities)
            # Probability Calculation
            z_score, probability = calculate_probability(mean, sigma, target)
            # Show combined output
            draw_combined_output(G, critical_path, critical_activities, mean, sigma, z_score, probability, target)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid target duration.")
# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityNetworkGUI(root)
    root.mainloop()