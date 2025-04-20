import tkinter as tk
import pandas as pd
import requests
from io import StringIO
from tkinter import filedialog, messagebox
import zipfile
import os
import tempfile

# ---------------------- Styling Constants ----------------------
BG_COLOR = "#0D1117"
TEXT_COLOR = "#00FF99"
BUTTON_BG = "#1e1e1e"
BUTTON_FG = "#00FFFF"
HIGHLIGHT = "#FF66CC"
FONT = ("Courier", 10, "bold")

# ---------------------- PII Keywords ----------------------
COMPREHENSIVE_PII_KEYWORDS = [
    # Basic Identity
    'name', 'firstname', 'lastname', 'fullname', 'surname', 'middlename', 'nickname',
    'initials', 'alias',

    # Date of Birth / Age
    'dob', 'dateofbirth', 'birthdate', 'birthday', 'age',

    # National Identifiers
    'ssn', 'socialsecuritynumber', 'nin', 'nationalid', 'passport', 'visa', 'idnumber',
    'driverlicense', 'licenseplate', 'taxid', 'itin', 'pan', 'aadhaar',

    # Contact Info
    'email', 'emailaddress', 'phone', 'phonenumber', 'mobile', 'cell', 'fax',
    'contact', 'telephone',

    # Location / Address
    'address', 'homeaddress', 'street', 'city', 'state', 'province', 'region',
    'country', 'zip', 'zipcode', 'postalcode', 'geolocation', 'lat', 'latitude', 'longitude', 'lng',

    # Financial Information
    'creditcard', 'ccnumber', 'cardnumber', 'cvc', 'cvv', 'accountnumber',
    'iban', 'bic', 'bankname', 'bankaccount', 'routingnumber', 'sortcode',

    # Authentication
    'username', 'user', 'userid', 'user_id', 'login', 'password', 'passcode', 'pin',

    # Biometrics
    'fingerprint', 'retina', 'iris', 'voiceprint', 'faceprint', 'facial', 'genetic', 'dna',

    # Online IDs
    'ip', 'ipaddress', 'macaddress', 'deviceid', 'imei', 'imsi', 'browserfingerprint',
    'sessionid', 'cookieid', 'token',

    # Employment & Education
    'employer', 'employerid', 'jobtitle', 'occupation', 'salary',
    'school', 'studentid', 'education', 'degree', 'grades',

    # Medical/Health Info
    'health', 'diagnosis', 'condition', 'treatment', 'medication',
    'insurance', 'policy', 'medicalrecord', 'mrn', 'npi',

    # Other
    'ssnid', 'socialinsurancenumber', 'residency', 'ethnicity',
    'maritalstatus', 'religion', 'gender', 'race', 'sexualorientation',
    'citizenship', 'nationality', 'militarystatus',

    # General Privacy Terms
    'pii', 'sensitive', 'confidential', 'privateinfo'
]

# ---------------------- Data Functions ----------------------
def fetch_dataset(url):
    try:
        # Determine the file extension
        file_extension = os.path.splitext(url)[1].lower()

        # Read the file based on its extension
        if file_extension == '.csv':
            df = pd.read_csv(url)
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(url)
        else:
            raise ValueError("Unsupported file format")

        return df

    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def load_local_dataset():
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Supported files", "*.csv *.xlsx *.xls *.zip"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx;*.xls"),
            ("ZIP files", "*.zip")
        ]
    )

    if file_path:
        try:
            if file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
                return df

            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                return df

            elif file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Filter for valid data files inside the ZIP
                    data_files = [f for f in zip_ref.namelist() if f.endswith(('.csv', '.xls', '.xlsx'))]

                    if not data_files:
                        raise ValueError("ZIP archive does not contain a CSV or Excel file.")

                    # Extract to a temporary directory
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        zip_ref.extractall(tmpdirname)
                        extracted_path = os.path.join(tmpdirname, data_files[0])

                        # Load the first supported file
                        if extracted_path.endswith('.csv'):
                            df = pd.read_csv(extracted_path)
                        else:
                            df = pd.read_excel(extracted_path)

                        return df

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {e}")
            return None

    return None

def detect_pii(df):
    pii_columns = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in COMPREHENSIVE_PII_KEYWORDS):
            pii_columns.append(col)
    return pii_columns

def anonymise_data(df, pii_columns):
    for col in pii_columns:
        df[col] = "REDACTED"
    return df

from collections import Counter

def apply_k_anonymity(df, k, quasi_identifiers):
    if not quasi_identifiers:
        return df, []

    # Count the frequency of each quasi-identifier group
    group_counts = df.groupby(quasi_identifiers).size()
    insufficient_groups = group_counts[group_counts < k].index.tolist()

    redacted_rows = []

    for index in insufficient_groups:
        mask = (df[quasi_identifiers] == pd.Series(index, index=quasi_identifiers)).all(axis=1)
        df.loc[mask, quasi_identifiers] = "SUPPRESSED"
        redacted_rows.extend(df.index[mask].tolist())

    return df, redacted_rows

def calculate_individualisation(df, quasi_identifiers):
    if not quasi_identifiers:
        return 0

    group_counts = df.groupby(quasi_identifiers).size()
    unique_individuals = sum(group_counts == 1)
    return unique_individuals


# ---------------------- GUI Class ----------------------
class DataanonymiserApp:
    def __init__(self, master):
        self.master = master
        master.title("🛡️ Data anonymiser Pro")
        master.configure(bg=BG_COLOR)

        # Initialize variables after root window is created
        self.select_columns_var = tk.BooleanVar()
        self.enable_k_var = tk.BooleanVar()
        self.k_value = tk.IntVar(value=2)  # default to k=2
        self.qid_columns = []

        self.selected_columns = []
        self.df = None
        self.anonymised_df = None

        self.label = tk.Label(master, text="Enter Dataset URL:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
        self.label.pack(pady=(10, 0))

        self.url_entry = tk.Entry(master, width=60, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.url_entry.pack(pady=5)

        self.fetch_button = tk.Button(master, text="🌐 Fetch Dataset", command=self.fetch_dataset, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.fetch_button.pack(pady=5)

        self.load_button = tk.Button(master, text="📂 Load Local Dataset", command=self.load_dataset, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.load_button.pack(pady=5)

        self.select_columns_check = tk.Checkbutton(master, text="Select Columns", variable=self.select_columns_var, 
                                                 command=self.on_select_columns_checked, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.select_columns_check.pack(pady=5)

        self.k_check = tk.Checkbutton(master, text="Enable k-Anonymity", variable=self.enable_k_var,
                                      bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.k_check.pack(pady=5)

        self.k_entry = tk.Entry(master, textvariable=self.k_value, width=5, bg=BUTTON_BG, fg=TEXT_COLOR,
                                insertbackground=TEXT_COLOR)
        self.k_entry.pack(pady=2)


        self.anonymise_button = tk.Button(master, text="🔐 anonymise Data", command=self.anonymise_data, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.anonymise_button.pack(pady=5)

        self.export_button = tk.Button(master, text="💾 Export anonymised Data", command=self.export_data, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT)
        self.export_button.pack(pady=5)

        self.text = tk.Text(master, height=18, width=85, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.text.pack(padx=10, pady=(10, 15))

    def on_select_columns_checked(self):
        if self.select_columns_var.get():
            if self.df is not None:  # Make sure data is loaded
                self.open_column_selector()
            else:
                messagebox.showwarning("Warning", "Please load a dataset first.")

    def open_column_selector(self):
        def apply_selection():
            self.selected_columns = [col for col, var in checkbox_vars.items() if var.get()]
            selector_window.destroy()

        selector_window = tk.Toplevel(self.master)
        selector_window.title("Select Columns to anonymise")
        selector_window.geometry("300x400")
        selector_window.configure(bg=BG_COLOR)

        tk.Label(selector_window, text="Select columns:", bg=BG_COLOR, fg=TEXT_COLOR).pack()

        checkbox_vars = {}
        for col in self.df.columns:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(selector_window, text=col, variable=var, 
                                    bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BUTTON_BG)
            checkbox.pack(anchor='w')
            checkbox_vars[col] = var

        tk.Button(selector_window, text="Apply", command=apply_selection, 
                bg=BUTTON_BG, fg=BUTTON_FG, font=FONT).pack(pady=10)

    def fetch_dataset(self):
        url = self.url_entry.get()
        self.df = fetch_dataset(url)
        if self.df is not None:
            self.text.insert(tk.END, f"Dataset fetched successfully with {len(self.df)} records.\n")
            self.text.insert(tk.END, f"Columns: {self.df.columns.tolist()}\n")

    def load_dataset(self):
        self.df = load_local_dataset()
        if self.df is not None:
            self.text.insert(tk.END, f"Dataset loaded successfully with {len(self.df)} records.\n")
            self.text.insert(tk.END, f"Columns: {self.df.columns.tolist()}\n")

    def anonymise_data(self):
        if self.df is not None:
            if self.select_columns_var.get() and self.selected_columns:
                # Use manually selected columns
                columns_to_anonymise = self.selected_columns
            else:
                # Auto-detect PII columns
                columns_to_anonymise = detect_pii(self.df)
                if not columns_to_anonymise:
                    messagebox.showwarning("Warning", "No PII columns detected automatically.")
                    return

            self.anonymised_df = self.df.copy()

            for col in columns_to_anonymise:
                self.anonymised_df[col] = "REDACTED"

            # Optional k-Anonymity
            if self.enable_k_var.get():
                k = self.k_value.get()
                self.qid_columns = columns_to_anonymise  # Treat them as QIDs for simplicity

                self.anonymised_df, redacted_rows = apply_k_anonymity(self.anonymised_df, k, self.qid_columns)
                self.text.insert(tk.END, f"Applied k-anonymity (k={k}). Rows suppressed: {len(redacted_rows)}\n")

                i = calculate_individualisation(self.anonymised_df, self.qid_columns)
                self.text.insert(tk.END, f"Number of unique individuals (i): {i}\n")

            self.text.insert(tk.END, f"Anonymised columns: {columns_to_anonymise}\n")
            self.text.insert(tk.END, "Data anonymisation complete!\n")

            self.text.insert(tk.END, "Data anonymization complete!\n")
        else:
            messagebox.showwarning("Warning", "No dataset loaded.")

    def export_data(self):
        if self.anonymised_df is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if file_path:
                if file_path.endswith('.csv'):
                    self.anonymised_df.to_csv(file_path, index=False)
                elif file_path.endswith(('.xls', '.xlsx')):
                    self.anonymised_df.to_excel(file_path, index=False)
                self.text.insert(tk.END, f"anonymised data exported to {file_path}\n")
        else:
            messagebox.showwarning("Warning", "No anonymised data to export.")

# ---------------------- Run Application ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DataanonymiserApp(root)
    root.mainloop()