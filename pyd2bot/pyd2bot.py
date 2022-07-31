from pyd2bot.PyD2Bot import PyD2Bot
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="the server host", type=str, default="0.0.0.0")
    parser.add_argument("--port", help="the server port", type=int, default=9999)
    args = parser.parse_args()
    PyD2Bot().runServer(args.host, args.port)
        
    
        