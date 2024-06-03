from api import app 
from ip_address import ip_address

# To run the application
if __name__ == "__main__":
    import uvicorn

    # runs my FastAPI application using the Uvicorn ASGI (Asynchronous Server Gateway interface) server
    # we are just going to define the port to be 8000, which is common for development servers, although others may be used
    uvicorn.run(app, host=ip_address, port=8000)