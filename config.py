import toml

def load_config():
    try:
        with open('config.toml', 'r') as f:
            return toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError) as e:
        print(f"Error loading config: {e}. Exiting.")
        exit(1)

config = load_config()
