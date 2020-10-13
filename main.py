import coordinator


# calls this program's coordinator which curates it's workflow
def start_scraper():
    coordinator.start()


# starts the program
if __name__ == "__main__":
    start_scraper()
