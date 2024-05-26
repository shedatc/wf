class EngineConfig:

    ACTION_EXIT      = "exit"
    ACTION_PLAY      = "play"
    TYPE_MULTI_2V2   = "multi-2v2"
    TYPE_SINGLE_2V2  = "single-2v2"
    TYPE_SINGLE_DUEL = "single-duel"

    def __init__(self):
        self.action = None
        self.arena  = None
        self.type   = None
