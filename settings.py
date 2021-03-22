# ---------------------------------------------------------------------------------------------------------------------------
# Game settings

PLAYER_1_HP = 7
PLAYER_2_HP = 7
PLAYER_1_BOARD = [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]]
PLAYER_2_BOARD = [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 1, 0, 1, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]]
BOARD_ROWS = 5
BOARD_COLUMNS = 5

# ---------------------------------------------------------------------------------------------------------------------------
# Search settings
SEARCHDEPTH = 2
SEARCHSEED = 42

# ---------------------------------------------------------------------------------------------------------------------------
# Reward settings

BASE_ACTIVE = 1
BASE_INACTIVE = 0.25
BASE_EMPTY = 0
INACTIVE_HIDING_PENALTY = -0.25
ACTIVE_HIDING_PENALTY = -0.1
EVEN_ROWS = 0.05
SIDE_PLACEMENT_PENALTY = -0.03
FRONTBACK_SIDE_PLACEMENT_PENALTY = -0.02
HITPOINTS = 3.5
VICTORY = 1000

# ---------------------------------------------------------------------------------------------------------------------------
# Keras settings (Not implemented yet)

weights_folder = 'weights/'

gamma = 0.95  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
        epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken
batch_size = 32  # Size of batch taken from replay buffer
max_steps_per_episode = 100

epsilon_random_frames = 250000
# Number of frames for exploration
epsilon_greedy_frames = 1000000.0
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
max_memory_length = 1000
# Train the model after 1 actions
update_after_actions = 3
# How often to update the target network
update_target_network = 1000
# Using huber loss for stability

learning_rate = 0.00001

clip_norm = 0.1
