import os

# Define the parent folder and the new folder
parent_folder = "news"
new_folder_name = "my_new_subfolder"

# Check if the parent folder exists, and if not, create it
if not os.path.exists(parent_folder):
    os.makedirs(parent_folder)
    print(f"Parent folder '{parent_folder}' created.")

# Define the full path for the new subfolder
new_folder_path = os.path.join(parent_folder, new_folder_name)

# Create the new subfolder
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f"Subfolder '{new_folder_name}' created inside '{parent_folder}'.")
else:
    print(f"Subfolder '{new_folder_name}' already exists inside '{parent_folder}'.")
