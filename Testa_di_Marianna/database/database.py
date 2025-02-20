import pickle
import berkeleydb
import json


with open("/home/filippo/Scrivania/Marianna_head/database/dati_per_database_riassunti.pkl", "rb") as file:
    loaded_data = pickle.load(file)

print(len(loaded_data))


def tuple_to_dict(t):
    """
    Convert a tuple of (key, value) into a dictionary where the first element
    becomes the key and the second element becomes the value.
    
    Parameters:
    t (tuple): A tuple containing a string key and a dictionary value
    
    Returns:
    dict: A dictionary with the converted structure
    """
    key, value = t
    return {key: value}


all_dicts = list(map(tuple_to_dict, loaded_data))

    
def save_to_berkeley_db(data, db_path):
    """
    Save dictionary data to Berkeley DB.
    
    Args:
        data: List of dictionaries to save
        db_path: Path where to create/open the Berkeley DB file
    """
    # Open the database in write mode
    db = berkeleydb.hashopen(db_path, "c")  # 'c' creates a new db if it doesn't exist
    
    try:
        # Iterate through the list of dictionaries
        for item in data:
            for key, value in item.items():
                # Convert the key to bytes (Berkeley DB requires byte keys)
                key_bytes = key.encode('utf-8')
                
                # Serialize the value dictionary using pickle
                value_bytes = pickle.dumps(value)
                
                # Store in database using dictionary-style assignment
                db[key_bytes] = value_bytes
                
        print(f"Database saved successfully at {db_path}")
        
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        
    finally:
        # Always close the database
        db.close()

# Save to database
db_path = "/home/filippo/Scrivania/Marianna_head/database/wiki_napoli_main.db"  # Specify your desired path
save_to_berkeley_db(all_dicts, db_path)

# # Optional: Verify the data was saved correctly
# def verify_database(db_path):
#     db = berkeleydb.hashopen(db_path, "r")
#     c = 0  # Open in read-only mode
#     try:
#         print("\nVerifying database contents:")
#         for key, value in db.items():
#             print(f"\nKey: {key.decode('utf-8')}")
#             data = pickle.loads(value)
#             print(f"Value: {data}")
#             c += 1
    
    
#     finally:
#         db.close()
    
#     print(c)

# # Uncomment to verify
# verify_database(db_path)




