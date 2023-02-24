try:
	from core.app import app
except:
	from .core.app import app

if __name__ == "__main__":
    app.run()
