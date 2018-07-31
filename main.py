from app import Server
import traceback, yaml, logging, sys


def main():
    try:
        path = "config/config.yaml"
        with open(path, 'r') as f:
            config = yaml.load(f)
        logging.basicConfig(
            level=config["log"]["level"],
            format=config["log"]["format"],
        )
        srv = Server(config)
        srv.start()

    except Exception as e:
        traceback.print_exc()
        return 1

    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
