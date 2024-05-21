from project import create_app # Defined in __init__.py

if __name__ == '__main__': # Checks that this script is being run directly
  app = create_app() # Singleton pattern
  app.run(host = '0.0.0.0', port = 8000, debug=True) # Local host on https port 
