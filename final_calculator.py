import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageGrab

# --- Special Dedication Window ---
def show_dedication_window():
    """Creates a pop-up window with the special dedication message."""
    dedication_win = tk.Toplevel(root)
    dedication_win.title("A Special Dedication")
    # --- *** CORRECTION: Increased window height from 250 to 300 *** ---
    dedication_win.geometry("450x300") 
    dedication_win.resizable(False, False)
    dedication_win.configure(bg=PALETTE['bg'])

    # Make the window modal
    dedication_win.transient(root)
    dedication_win.grab_set()

    container = ttk.Frame(dedication_win, padding=20, style="TFrame")
    container.pack(expand=True, fill="both")

    ttk.Label(container, text="♥ For my dearest Keilah Camara ♥", font=('Segoe UI', 16, 'bold'), foreground=PALETTE['red_accent'], anchor="center").pack(pady=10)
    
    message_text = "I made this little application from scratch just for you.\nEvery line of code was written with you in mind.\nI love you more than words can say."
    ttk.Label(container, text=message_text, font=('Segoe UI', 11), anchor="center", justify="center").pack(pady=15)
    
    ttk.Label(container, text="With all my love,\nJuan Gutierrez", font=('Segoe UI', 12, 'italic'), anchor="center", justify="center").pack(pady=20)

# --- Formatting and Calculation Logic ---
def human_readable_formatter(x, pos):
    """Formats large numbers on the Y-axis to K, M, B, T with two decimal places."""
    if x >= 1e12: return f'${x*1e-12:.2f}T'
    if x >= 1e9: return f'${x*1e-9:.2f}B'
    if x >= 1e6: return f'${x*1e-6:.2f}M'
    if x >= 1e3: return f'${x*1e-3:.2f}K'
    return f'${x:,.0f}'

def calculate_investment():
    """Performs a day-by-day simulation and prepares aggregated data for visuals."""
    try:
        initial_deposit = float(initial_deposit_entry.get())
        daily_rate_percent = float(rate_entry.get())
        duration = int(duration_entry.get())
        duration_unit = duration_unit_var.get()
        contribution_amount = float(contributions_entry.get())
        contribution_freq = contribution_freq_var.get()
        breakdown_period = breakdown_period_var.get()

        if duration_unit == "Years": total_days = duration * 365
        else: total_days = duration * 30

        daily_rate = daily_rate_percent / 100
        
        table_data, chart_labels = [], []
        chart_principals, chart_contributions, chart_interests = [], [], []
        
        current_balance = initial_deposit
        total_contributions = 0
        capital_at_period_start = initial_deposit
        interest_this_period = 0
        last_period_day = 0

        period_days = {"Daily": 1, "Monthly": 30, "Annually": 365}
        period_divisor = period_days[breakdown_period]

        for day in range(1, total_days + 1):
            add_contribution_today = False
            if contribution_freq == "Daily": add_contribution_today = True
            elif contribution_freq == "Monthly" and day % 30 == 0: add_contribution_today = True
            elif contribution_freq == "Annually" and day % 365 == 0: add_contribution_today = True
            
            if add_contribution_today:
                current_balance += contribution_amount
                total_contributions += contribution_amount

            interest_today = current_balance * daily_rate
            current_balance += interest_today
            interest_this_period += interest_today

            if day % period_divisor == 0:
                period_number = day // period_divisor
                table_data.append({"period": period_number, "capital_start": f"{capital_at_period_start:,.2f}", "interest_gain": f"+{interest_this_period:,.2f}", "total_end": f"{current_balance:,.2f}"})
                chart_labels.append(str(period_number))
                chart_principals.append(initial_deposit)
                chart_contributions.append(total_contributions)
                chart_interests.append(current_balance - initial_deposit - total_contributions)
                capital_at_period_start = current_balance
                interest_this_period = 0
                last_period_day = day

        if total_days > last_period_day:
            is_yearly_input_monthly_breakdown = duration_unit == "Years" and breakdown_period == "Monthly"
            if is_yearly_input_monthly_breakdown and table_data:
                table_data[-1]["interest_gain"] = f"+{float(table_data[-1]['interest_gain'].replace('+', '').replace(',', '')) + interest_this_period:,.2f}"
                table_data[-1]["total_end"] = f"{current_balance:,.2f}"
                chart_interests[-1] = current_balance - initial_deposit - total_contributions
            else:
                period_number = (last_period_day // period_divisor) + 1
                table_data.append({"period": period_number, "capital_start": f"{capital_at_period_start:,.2f}", "interest_gain": f"+{interest_this_period:,.2f}", "total_end": f"{current_balance:,.2f}"})
                chart_labels.append(str(period_number))
                chart_principals.append(initial_deposit)
                chart_contributions.append(total_contributions)
                chart_interests.append(current_balance - initial_deposit - total_contributions)

        total_investment = initial_deposit + total_contributions
        total_gain = current_balance - total_investment
        summary_gain_var.set(f"${total_gain:,.2f}")
        summary_final_capital_var.set(f"${current_balance:,.2f}")
        summary_investment_var.set(f"${total_investment:,.2f}")

        update_table(table_data, breakdown_period)
        update_chart(chart_labels, chart_principals, chart_contributions, chart_interests, breakdown_period)

    except ValueError: messagebox.showerror("Input Error", "Please enter valid numbers in all fields.")
    except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def update_table(data, period_name):
    tree.heading("Period", text=period_name)
    for i in tree.get_children(): tree.delete(i)
    for row in data: tree.insert("", "end", values=(row["period"], row["capital_start"], row["interest_gain"], row["total_end"]))

def update_chart(labels, principals, contributions, interests, period_name):
    ax_bar.clear()
    ax_bar.set_facecolor(PALETTE['chart_bg'])
    principals, contributions, interests = np.array(principals), np.array(contributions), np.array(interests)
    
    ax_bar.bar(labels, principals, label='Initial Deposit', color=PALETTE['chart_bar1'])
    ax_bar.bar(labels, contributions, bottom=principals, label='Additional Contributions', color=PALETTE['chart_bar2'])
    ax_bar.bar(labels, interests, bottom=principals + contributions, label='Accumulated Interest', color=PALETTE['chart_bar3'])
    
    ax_bar.set_ylabel("Amount ($)", color=PALETTE['text'])
    ax_bar.set_xlabel(f"Time ({period_name})", color=PALETTE['text'])
    ax_bar.set_title("Investment Growth Over Time", color=PALETTE['text'])
    ax_bar.legend()
    ax_bar.get_yaxis().set_major_formatter(FuncFormatter(human_readable_formatter))
    ax_bar.tick_params(colors=PALETTE['text'])
    
    num_labels = len(labels)
    if num_labels > 1:
        tick_indices = np.linspace(0, num_labels - 1, min(num_labels, 15), dtype=int)
        tick_labels = [labels[i] for i in tick_indices]
        ax_bar.set_xticks(tick_indices)
        ax_bar.set_xticklabels(tick_labels)
        if num_labels > 20: plt.setp(ax_bar.get_xticklabels(), rotation=45, ha="right")
        else: plt.setp(ax_bar.get_xticklabels(), rotation=0, ha="center")
            
    fig_bar.tight_layout()
    canvas_bar.draw()

def save_image():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png"), ("All files", "*.*")])
        if not file_path: return
        x, y, w, h = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(file_path)
        messagebox.showinfo("Success", f"Image successfully saved to:\n{file_path}")
    except Exception as e: messagebox.showerror("Save Error", f"Could not save the image. Error: {e}")

# --- GUI Setup ---
PALETTE = {
    "bg": "#FFF0F5", "text": "#5D4037", "green_accent": "#66CDAA", "red_accent": "#E91E63", 
    "grey_accent": "#BDBDBD", "heading_bg": "#F8BBD0", "chart_bg": "#FFFFFF", 
    "chart_bar1": "#8E24AA", "chart_bar2": "#D81B60", "chart_bar3": "#FFB6C1"
}

root = tk.Tk()
root.title("For Keilah, With Love")
root.geometry("850x750")
root.configure(bg=PALETTE['bg'])

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
about_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="About", menu=about_menu)
about_menu.add_command(label="Dedication", command=show_dedication_window)

style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background=PALETTE['bg'], foreground=PALETTE['text'], font=('Segoe UI', 10))
style.configure("TFrame", background=PALETTE['bg'])
style.configure("TNotebook", background=PALETTE['bg'], borderwidth=0)
style.configure("TNotebook.Tab", font=('Segoe UI', 10, 'bold'), padding=[10, 5], background=PALETTE['bg'], borderwidth=0)
style.map("TNotebook.Tab", background=[("selected", PALETTE['chart_bg'])], foreground=[("selected", PALETTE['red_accent'])])
style.configure("Treeview", rowheight=25, font=('Segoe UI', 10), background=PALETTE['chart_bg'], fieldbackground=PALETTE['chart_bg'], foreground=PALETTE['text'])
style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=PALETTE['heading_bg'], foreground=PALETTE['text'], relief="flat")
style.map("Treeview.Heading", background=[('active', PALETTE['red_accent'])])

header_frame = ttk.Frame(root)
header_frame.pack(pady=(10, 5), fill="x")
ttk.Label(header_frame, text="Advanced Compound Interest Calculator", font=('Segoe UI', 16, 'bold'), anchor="center").pack()

summary_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
summary_frame.pack(fill="x")
summary_frame.columnconfigure((0, 1, 2), weight=1)
summary_gain_var, summary_final_capital_var, summary_investment_var = tk.StringVar(value="$0.00"), tk.StringVar(value="$0.00"), tk.StringVar(value="$0.00")
def create_summary_item(parent, title, textvariable, color):
    item_frame = ttk.Frame(parent)
    ttk.Label(item_frame, text=title, font=('Segoe UI', 10, 'bold'), anchor="center").pack(fill="x")
    ttk.Label(item_frame, textvariable=textvariable, font=('Segoe UI', 24, 'bold'), foreground=color, anchor="center").pack(fill="x")
    return item_frame
create_summary_item(summary_frame, "Total Gain", summary_gain_var, PALETTE['green_accent']).grid(row=0, column=0)
create_summary_item(summary_frame, "Final Capital", summary_final_capital_var, PALETTE['red_accent']).grid(row=0, column=1)
create_summary_item(summary_frame, "Total Investment", summary_investment_var, PALETTE['grey_accent']).grid(row=0, column=2)

ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)

controls_frame = ttk.Frame(root, padding="10 0 10 20"); controls_frame.pack(fill="x")
ttk.Label(controls_frame, text="Initial Deposit ($):").grid(row=0, column=0, sticky="w", pady=5)
initial_deposit_entry = ttk.Entry(controls_frame, width=18); initial_deposit_entry.grid(row=0, column=1, padx=5)
ttk.Label(controls_frame, text="Daily Interest Rate (%):").grid(row=1, column=0, sticky="w", pady=5)
rate_entry = ttk.Entry(controls_frame, width=18); rate_entry.grid(row=1, column=1, padx=5)
ttk.Label(controls_frame, text="Investment Term:").grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)
duration_entry = ttk.Entry(controls_frame, width=10); duration_entry.grid(row=0, column=3, sticky="w")
duration_unit_var = tk.StringVar(value="Years")
duration_unit_menu = ttk.Combobox(controls_frame, textvariable=duration_unit_var, values=["Years", "Months"], width=7, state="readonly"); duration_unit_menu.grid(row=0, column=4, sticky="w", padx=5)
ttk.Label(controls_frame, text="Additional Contributions ($):").grid(row=1, column=2, sticky="w", padx=(20, 5), pady=5)
contributions_entry = ttk.Entry(controls_frame, width=10); contributions_entry.grid(row=1, column=3, sticky="w")
contribution_freq_var = tk.StringVar(value="Monthly")
contribution_freq_menu = ttk.Combobox(controls_frame, textvariable=contribution_freq_var, values=["Daily", "Monthly", "Annually"], width=7, state="readonly"); contribution_freq_menu.grid(row=1, column=4, sticky="w", padx=5)
calculate_button = ttk.Button(controls_frame, text="Calculate", command=calculate_investment, width=15); calculate_button.grid(row=0, column=5, rowspan=2, padx=(20, 5), ipady=8)

visuals_frame = ttk.Frame(root, padding="20 10 20 10"); visuals_frame.pack(fill="both", expand=True)
breakdown_controls = ttk.Frame(visuals_frame); breakdown_controls.pack(fill="x", pady=(0, 5))
ttk.Label(breakdown_controls, text="Breakdown Detail:").pack(side="left", padx=(5,10))
breakdown_period_var = tk.StringVar(value="Monthly")
breakdown_menu = ttk.Combobox(breakdown_controls, textvariable=breakdown_period_var, values=["Daily", "Monthly", "Annually"], width=10, state="readonly"); breakdown_menu.pack(side="left")

notebook = ttk.Notebook(visuals_frame); notebook.pack(fill="both", expand=True)
chart_tab = ttk.Frame(notebook); notebook.add(chart_tab, text="Summary Chart")
fig_bar, ax_bar = plt.subplots(facecolor=PALETTE['chart_bg']); canvas_bar = FigureCanvasTkAgg(fig_bar, master=chart_tab); canvas_bar.get_tk_widget().pack(fill="both", expand=True, pady=5)
table_tab = ttk.Frame(notebook); notebook.add(table_tab, text="Detailed Breakdown")
columns = ("Period", "Capital ($)", "Interest ($)", "Total ($)"); tree = ttk.Treeview(table_tab, columns=columns, show='headings')
for col in columns: tree.heading(col, text=col)
tree.column("Period", anchor="center", width=80, stretch=False); tree.column("Capital ($)", anchor="e", width=200); tree.column("Interest ($)", anchor="e", width=200); tree.column("Total ($)", anchor="e", width=200)
scrollbar = ttk.Scrollbar(table_tab, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set); tree.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")

footer = ttk.Frame(root, padding=10); footer.pack(fill="x")
ttk.Button(footer, text="Save Image ⤓", command=save_image).pack(side="right", padx=5)
ttk.Button(footer, text="Share →", command=save_image).pack(side="right")


root.mainloop()

