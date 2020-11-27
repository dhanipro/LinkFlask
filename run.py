from portal import create_app

# application = app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)