
def main():
    import sys
    if sys.version_info < (3, 5):
        from jrti_game.fallback import main
    else:
        from jrti_game.game import main
    return main()
