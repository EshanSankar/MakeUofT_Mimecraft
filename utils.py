import time
import math

def check_walking(landmarks, prev_states, time_window=2):
    if landmarks is None:
        return False, prev_states
    
    current_time = time.time()

    r_hip = get_landmark_coords(landmarks, 23)
    r_knee = get_landmark_coords(landmarks, 25)
    r_ankle = get_landmark_coords(landmarks, 27)

    l_hip = get_landmark_coords(landmarks, 24)
    l_knee = get_landmark_coords(landmarks, 26)
    l_ankle = get_landmark_coords(landmarks, 28)

    r_angle = calculate_angle(r_hip, r_knee, r_ankle)
    l_angle = calculate_angle(l_hip, l_knee, l_ankle)

    r_knee_y = r_knee.y
    l_knee_y = l_knee.y
    hip_y = (r_hip.y + l_hip.y) / 2
    


    step_conditions = {
        "right_bent": 120 < r_angle < 174 or r_knee_y < hip_y - 0.35,
        "left_bent": 120 < l_angle < 174 or l_knee_y < hip_y - 0.35,
    }

    current_state = None
    if step_conditions["right_bent"]:
        current_state = "right_step"
    elif step_conditions["left_bent"]:
        current_state = "left_step"
    else:
        current_state = "neutral"

    prev_states.append((current_state, current_time))
    
    print(prev_states)
    
    valid_states = [s for s in prev_states if current_time - s[1] <= time_window]
    prev_states[:] = valid_states[-10:]  

    if len(prev_states) >= 10:
        states = [s[0] for s in prev_states]
        if states.count("neutral") < 2:
            return True, prev_states

    return False, prev_states


def get_velocity(current_state, prev_state):
    if not prev_state:
        return 0
    return math.hypot(current_state.x - prev_state.x, current_state.y - prev_state.y)


def detect_arm_swing(landmarks, prev_state, arm="right"):
    if landmarks is None:
        return False, 0
    
    
    if arm == "right":
        shoulder = get_landmark_coords(landmarks, 12)
        elbow = get_landmark_coords(landmarks, 14)
        wrist = get_landmark_coords(landmarks, 16)
    else:
        shoulder = get_landmark_coords(landmarks, 11)
        elbow = get_landmark_coords(landmarks, 13)
        wrist = get_landmark_coords(landmarks, 15)

    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    wrist_velocity = get_velocity(wrist, prev_state)
  
    if elbow_angle < 150 or wrist_velocity > 0.15:
        return True, wrist_velocity
    else:
        return False, wrist_velocity


def get_landmark_coords(landmarks, index):
    if landmarks is None:
        return None
    return landmarks.landmark[index]


    
def calculate_angle(a, b, c):
    if a is None or b is None or c is None:
        return -1
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
    dot_product = ba[0] * bc[0] + ba[1] * bc[1]

    return math.degrees(math.acos(dot_product / (mag_ba * mag_bc)))