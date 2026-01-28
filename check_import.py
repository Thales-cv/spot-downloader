try:
    from spotdl import Spotdl
    print("Spotdl found")
except ImportError:
    try:
        from spotdl import SpotDL
        print("SpotDL found")
    except ImportError:
        print("None found")
