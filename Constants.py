import pygame

STATE_IDLE = 0
STATE_ATK = 1
STATE_BLK = 2
STATE_JUMP = 3
STATE_CHG = 4
STATE_DAMAGED = 5
STATE_FAIL_ATK = 6

ENM_IDLE = 0
ENM_TOP_PREP = 1
ENM_TOP_ATK = 2
ENM_BOT_PREP = 3
ENM_BOT_ATK = 4

FIST_MAN_SEQ = [ENM_IDLE,
                ENM_IDLE,
                ENM_TOP_PREP,
                ENM_TOP_ATK,
                ENM_IDLE,
                ENM_IDLE,
                ENM_BOT_PREP,
                ENM_BOT_ATK]



PURPLE_FIST_MAN_SEQ = [ENM_TOP_PREP,
                        ENM_TOP_ATK,
                        ENM_BOT_PREP,
                        ENM_BOT_ATK,
                        ENM_IDLE,
                        ENM_BOT_PREP,
                        ENM_BOT_ATK,
                        ENM_IDLE]

HYDRA_SEQ = [ENM_IDLE,
            ENM_IDLE,
            ENM_TOP_PREP,
            ENM_TOP_ATK]

PURPLE_HYDRA_SEQ = [ENM_IDLE,
                    ENM_TOP_PREP,
                    ENM_TOP_ATK,
                    ENM_TOP_ATK,
                    ENM_TOP_PREP,
                    ENM_TOP_ATK,
                    ENM_TOP_ATK,
                    ENM_TOP_ATK]

EMPTY_SEQ = [ENM_IDLE]

FREDERICK_SEQ = [ENM_IDLE]

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

#   270 x 480 in graphics pixels
