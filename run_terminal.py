import main

if __name__ == "__main__":
    main.app = main.PyTerm()
    main.app.start()
    app = QApplication(sys.argv)
    window = QMainWindow()
    terminal = Terminal()
    window.setCentralWidget(terminal)
    window.setWindowTitle("PyTerm Terminal")
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())
