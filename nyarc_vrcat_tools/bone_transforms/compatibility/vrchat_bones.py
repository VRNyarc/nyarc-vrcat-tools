# VRChat Standard Bone Definitions and Compatibility Checking
# Extracted from HEAD_TAIL_DIRECT_FIX version for proper modular structure
# Enhanced with comprehensive bone name variations from Avatar Toolkit by Team Neoneko
# Reference: https://github.com/teamneoneko/Avatar-Toolkit/blob/Current/core/dictionaries.py

# Standard VRChat bone sets for compatibility checking
VRCHAT_STANDARD_BONES = {
    'core': [
        # Core body bones (most critical) - Enhanced from Avatar Toolkit with Valve/Source engine support
        
        # Hips/Pelvis variations - Standard, Valve, Mixamo, Japanese, IK
        'hips', 'hip', 'pelvis', 'root', '腰', 'ik_腰', 'ik_hips',
        'valvebipedbip01pelvis', 'valvebipedbip01hip', 'mixamorig:hips', 'mixamorig_hips', 'mixamorighips', 'bip01pelvis', 'bip01_pelvis',
        
        # Spine variations - Standard, Valve, Mixamo, Japanese, IK
        'spine', 'back', 'torso', '脊椎', 'ik_脊椎', 'ik_spine',
        'valvebipedbip01spine', 'valvebipedbip01spine1', 'mixamorig:spine', 'mixamorig:spine1', 'mixamorig_spine', 'mixamorig_spine1',
        'bip01spine', 'bip01_spine', 'bip01spine1', 'bip01_spine1',
        
        # Chest variations - Standard, Valve, Mixamo, Japanese, IK
        'chest', 'ribcage', 'upper_body', '胸', 'ik_胸', 'ik_chest',
        'upperchest', 'upper_chest', '上胸', 'ik_上胸', 'ik_upperchest',
        'valvebipedbip01spine2', 'valvebipedbip01spine3', 'mixamorig:spine2', 'mixamorig:spine3', 'mixamorig_spine2', 'mixamorig_spine3',
        'bip01spine2', 'bip01_spine2', 'bip01spine3', 'bip01_spine3',
        
        # Neck variations - Standard, Valve, Mixamo, Japanese, IK
        'neck', '首', 'ik_首', 'ik_neck', 'neck1',
        'valvebipedbip01neck1', 'valvebipedbip01neck', 'mixamorig:neck', 'mixamorig_neck', 'bip01neck', 'bip01_neck',
        'bip01neck1', 'bip01_neck1',
        
        # Head variations - Standard, Valve, Mixamo, Japanese, IK
        'head', '頭', 'ik_頭', 'ik_head', 'head1',
        'valvebipedbip01head1', 'valvebipedbip01head', 'mixamorig:head', 'mixamorig_head', 'bip01head', 'bip01_head',
        'bip01head1', 'bip01_head1'
    ],
    'shoulder_left': [
        # Left shoulder bones (clavicle) - Separated from arms for proper semantic mapping
        'shoulder.l', 'shoulder_l', 'leftshoulder', 'left_shoulder', 'shoulderl', 'lshoulder',
        'clavicle.l', 'clavicle_l', 'leftclavicle', 'left_clavicle', 'clavicleleft', 'lclavicle',
        '肩.l', '左肩', 'ik_左肩', 'ik_shoulder.l', 'left shoulder',
        'valvebipedbip01lclavicle', 'valvebipedbip01leftshoulder',
        'mixamorig:leftshoulder', 'mixamorig_leftshoulder', 'bip01lclavicle', 'bip01_l_clavicle'
    ],
    'upper_arm_left': [
        # Left upper arm bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'upper_arm.l', 'upperarm.l', 'arm.l', 'upper_arm_l', 'leftupperarm', 'leftarm',
        'arml', 'larm', 'upperarml', 'lupperarm', 'uparml', 'luparm', '左腕', '腕.l', 'ik_左腕', 'ik_upper_arm.l',
        'left arm', 'leftarm', 'left_arm',
        'upperarm_l', 'upperarm.l', 'upper_arm.l',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01lupperarm', 'valvebipedbip01leftarm', 'upperarm.l', 'arm.l',
        'mixamorig:leftarm', 'mixamorig_leftarm', 'bip01lupperarm', 'bip01_l_upperarm'
    ],
    'forearm_left': [
        # Left forearm/elbow bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'forearm.l', 'lower_arm.l', 'elbow.l', 'forearm_l', 'leftforearm', 'leftlowerarm',
        'elbowl', 'lelbow', 'leftelbow', 'lowerarml', 'llowerarm', 'lowerarm_l', 'lowarml', 'llowarm',
        'forearml', 'lforearm', '左ひじ', 'ひじ.l', 'すね.l', 'ik_左ひじ', 'ik_ひじ.l', 'ik_forearm.l',
        'left elbow', 'leftforearm', 'left_forearm', 'left_elbow',
        'lowerarm_l', 'lower_arm_l', 'lowerarm.l', 'forearm.l',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01lforearm', 'valvebipedbip01leftelbow', 'forearm.l', 'lowerarm.l',
        'mixamorig:leftforearm', 'mixamorig_leftforearm', 'bip01lforearm', 'bip01_l_forearm'
    ],
    'hand_left': [
        # Left hand/wrist bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'hand.l', 'wrist.l', 'hand_l', 'lefthand', 'leftwrist', 'lefthand',
        'handl', 'lhand', 'wristl', 'lwrist', '左手首', '手首.l', 'ik_左手首', 'ik_手首.l', 'ik_hand.l',
        'left hand', 'lefthand', 'left_hand', 'left wrist', 'left_wrist',
        'hand_l', 'hand.l',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01lhand', 'valvebipedbip01lefthand', 'hand.l', 'wrist.l',
        'mixamorig:lefthand', 'mixamorig_lefthand', 'bip01lhand', 'bip01_l_hand'
    ],
    'shoulder_right': [
        # Right shoulder bones (clavicle) - Separated from arms for proper semantic mapping
        'shoulder.r', 'shoulder_r', 'rightshoulder', 'right_shoulder', 'shoulderr', 'rshoulder',
        'clavicle.r', 'clavicle_r', 'rightclavicle', 'right_clavicle', 'clavicleright', 'rclavicle',
        '肩.r', '右肩', 'ik_右肩', 'ik_shoulder.r', 'right shoulder',
        'valvebipedbip01rclavicle', 'valvebipedbip01rightshoulder',
        'mixamorig:rightshoulder', 'mixamorig_rightshoulder', 'bip01rclavicle', 'bip01_r_clavicle'
    ],
    'upper_arm_right': [
        # Right upper arm bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'upper_arm.r', 'upperarm.r', 'arm.r', 'upper_arm_r', 'rightupperarm', 'rightarm',
        'armr', 'rarm', 'upperarmr', 'rupperarm', 'uparmr', 'ruparm', '右腕', '腕.r', 'ik_右腕', 'ik_upper_arm.r',
        'right arm', 'rightarm', 'right_arm',
        'upperarm_r', 'upperarm.r', 'upper_arm.r',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01rupperarm', 'valvebipedbip01rightarm', 'upperarm.r', 'arm.r',
        'mixamorig:rightarm', 'mixamorig_rightarm', 'bip01rupperarm', 'bip01_r_upperarm'
    ],
    'forearm_right': [
        # Right forearm/elbow bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'forearm.r', 'lower_arm.r', 'elbow.r', 'forearm_r', 'rightforearm', 'rightlowerarm',
        'elbowr', 'relbow', 'rightelbow', 'lowerarmr', 'rlowerarm', 'lowerarm_r', 'lowarmr', 'rlowarm',
        'forearmr', 'rforearm', '右ひじ', 'ひじ.r', 'すね.r', 'ik_右ひじ', 'ik_ひじ.r', 'ik_forearm.r',
        'right elbow', 'rightforearm', 'right_forearm', 'right_elbow',
        'lowerarm_r', 'lower_arm_r', 'lowerarm.r', 'forearm.r',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01rforearm', 'valvebipedbip01rightelbow', 'forearm.r', 'lowerarm.r',
        'mixamorig:rightforearm', 'mixamorig_rightforearm', 'bip01rforearm', 'bip01_r_forearm'
    ],
    'hand_right': [
        # Right hand/wrist bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat (all lowercase)
        'hand.r', 'wrist.r', 'hand_r', 'righthand', 'rightwrist', 'righthand',
        'handr', 'rhand', 'wristr', 'rwrist', '右手首', '手首.r', 'ik_右手首', 'ik_手首.r', 'ik_hand.r',
        'right hand', 'righthand', 'right_hand', 'right wrist', 'right_wrist',
        'hand_r', 'hand.r',  # Unity/VRChat patterns (lowercase)
        'valvebipedbip01rhand', 'valvebipedbip01righthand', 'hand.r', 'wrist.r',
        'mixamorig:righthand', 'mixamorig_righthand', 'bip01rhand', 'bip01_r_hand'
    ],
    'upper_leg_left': [
        # Left thigh/upper leg bones - Standard, Valve, Mixamo, Japanese, IK
        'thigh.l', 'upper_leg.l', 'leg.l', 'thigh_l', 'leftupperleg', 'leftupleg', 'leftleg',
        'legl', 'lleg', 'upperlegl', 'lupperleg', 'thighl', '左足', '太もも.l', 'ik_左足',
        'Left leg', 'left leg', 'LeftLeg', 'Left_Leg', 'LeftUpLeg', 'Left_UpLeg',
        'upper_leg_L', 'UpperLeg_L',  # Common underscore + capital L pattern
        'valvebipedbip01lthigh', 'valvebipedbip01leftleg', 'Thigh.L', 'UpperLeg.L',
        'mixamorig:LeftUpLeg', 'mixamorig_LeftUpLeg', 'bip01lthigh', 'bip01_l_thigh'
    ],
    'lower_leg_left': [
        # Left knee/lower leg bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat
        'shin.l', 'lower_leg.l', 'knee.l', 'shin_l', 'leftlowerleg', 'leftknee',
        'kneel', 'lknee', 'lowerlegl', 'llowerleg', 'lowlegl', 'llowleg', 'calfl', 'lcalf',
        'lower_leg_L', 'LowerLeg_L', 'lowerleg_l',  # Common Unity/VRChat patterns
        '左ひざ', 'ひざ.l', 'すね.l', 'ik_左ひざ', 'ik_knee.l',
        'Left knee', 'left knee', 'LeftKnee', 'leftKnee', 'LeftLeg', 'Left_Knee',
        'valvebipedbip01lcalf', 'valvebipedbip01leftknee', 'Shin.L', 'LowerLeg.L', 'Calf.L',
        'mixamorig:LeftLeg', 'mixamorig_LeftLeg', 'bip01lcalf', 'bip01_l_calf'
    ],
    'foot_left': [
        # Left foot/ankle bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat
        'foot.l', 'ankle.l', 'foot_l', 'leftfoot', 'leftankle',
        'anklel', 'lankle', 'footl', 'lfoot', '左足首', '足首.l', 'ik_左足首', 'ik_foot.l',
        'Left ankle', 'left ankle', 'LeftFoot', 'Left_Foot', 'LeftAnkle', 'Left_Ankle',
        'Foot_L', 'foot_l',  # Common Unity/VRChat patterns
        'valvebipedbip01lfoot', 'valvebipedbip01leftfoot', 'Foot.L', 'Ankle.L',
        'mixamorig:LeftFoot', 'mixamorig_LeftFoot', 'bip01lfoot', 'bip01_l_foot'
    ],
    'toe_left': [
        # Left toe bones - Standard, Valve, Mixamo, Japanese, IK
        'toe.l', 'toes.l', 'toe_l', 'lefttoe', 'lefttoes', '左つま先', 'つま先.l',
        'ik_左つま先', 'ik_toe.l', 'Left Toe', 'left toe', 'LeftToe', 'Left_Toe',
        'valvebipedbip01ltoe0', 'valvebipedbip01lefttoe', 'Toe.L', 'Toes.L',
        'mixamorig:LeftToeBase', 'mixamorig_LeftToeBase', 'bip01ltoe0', 'bip01_l_toe0'
    ],
    'upper_leg_right': [
        # Right thigh/upper leg bones - Standard, Valve, Mixamo, Japanese, IK
        'thigh.r', 'upper_leg.r', 'leg.r', 'thigh_r', 'rightupperleg', 'rightupleg', 'rightleg',
        'legr', 'rleg', 'upperlegr', 'rupperleg', 'thighr', '右足', '太もも.r', 'ik_右足',
        'Right leg', 'right leg', 'RightLeg', 'Right_Leg', 'RightUpLeg', 'Right_UpLeg',
        'upper_leg_R',  # Common underscore + capital R pattern
        'valvebipedbip01rthigh', 'valvebipedbip01rightleg', 'Thigh.R', 'UpperLeg.R',
        'mixamorig:RightUpLeg', 'mixamorig_RightUpLeg', 'bip01rthigh', 'bip01_r_thigh'
    ],
    'lower_leg_right': [
        # Right knee/lower leg bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat
        'shin.r', 'lower_leg.r', 'knee.r', 'shin_r', 'rightlowerleg', 'rightknee',
        'kneer', 'rknee', 'lowerlegr', 'rlowerleg', 'lowlegr', 'rlowleg', 'calfr', 'rcalf',
        'lower_leg_R', 'LowerLeg_R', 'lowerleg_r',  # Common Unity/VRChat patterns
        '右ひざ', 'ひざ.r', 'すね.r', 'ik_右ひざ', 'ik_knee.r',
        'Right knee', 'right knee', 'RightKnee', 'rightKnee', 'RightLeg', 'Right_Knee',
        'valvebipedbip01rcalf', 'valvebipedbip01rightknee', 'Shin.R', 'LowerLeg.R', 'Calf.R',
        'mixamorig:RightLeg', 'mixamorig_RightLeg', 'bip01rcalf', 'bip01_r_calf'
    ],
    'foot_right': [
        # Right foot/ankle bones - Standard, Valve, Mixamo, Japanese, IK, Unity/VRChat
        'foot.r', 'ankle.r', 'foot_r', 'rightfoot', 'rightankle',
        'ankler', 'rankle', 'footr', 'rfoot', '右足首', '足首.r', 'ik_右足首', 'ik_foot.r',
        'Right ankle', 'right ankle', 'RightFoot', 'Right_Foot', 'RightAnkle', 'Right_Ankle',
        'Foot_R', 'foot_r',  # Common Unity/VRChat patterns
        'valvebipedbip01rfoot', 'valvebipedbip01rightfoot', 'Foot.R', 'Ankle.R',
        'mixamorig:RightFoot', 'mixamorig_RightFoot', 'bip01rfoot', 'bip01_r_foot'
    ],
    'toe_right': [
        # Right toe bones - Standard, Valve, Mixamo, Japanese, IK
        'toe.r', 'toes.r', 'toe_r', 'righttoe', 'righttoes', '右つま先', 'つま先.r',
        'ik_右つま先', 'ik_toe.r', 'Right Toe', 'right toe', 'RightToe', 'Right_Toe',
        'valvebipedbip01rtoe0', 'valvebipedbip01righttoe', 'Toe.R', 'Toes.R',
        'mixamorig:RightToeBase', 'mixamorig_RightToeBase', 'bip01rtoe0', 'bip01_r_toe0'
    ],
    # Individual finger segments - Avatar Toolkit approach with separate categories for each finger bone
    # LEFT HAND FINGER SEGMENTS (following Avatar Toolkit structure)
    
    # Left Thumb segments (0=metacarpal, 1=proximal, 2=intermediate, 3=distal)
    'thumb_1_left': [
        # Thumb proximal segment (segment 1)
        'thumb_1_l', 'thumb1l', 'lthumb1', 'thumb_proximal_l', 'thumbproximal_l',
        'thumb.1.l', 'Thumb_1_L', 'Thumb.1.L', 'LeftThumb1', 'Left_Thumb_1',
        'valvebipedbip01lthumb1', 'valvebipedbip01lfinger0', 'bip01lthumb1',
        'mixamorig:LeftHandThumb1', 'mixamorig_LeftHandThumb1', 'lefthandthumb1',
        '左親指１', 'ik_thumb_1_l', 'thumb_proximal.l'
    ],
    'thumb_2_left': [
        # Thumb intermediate segment (segment 2)
        'thumb_2_l', 'thumb2l', 'lthumb2', 'thumb_intermediate_l', 'thumbintermediate_l',
        'thumb.2.l', 'Thumb_2_L', 'Thumb.2.L', 'LeftThumb2', 'Left_Thumb_2',
        'valvebipedbip01lthumb2', 'valvebipedbip01lfinger01', 'bip01lthumb2',
        'mixamorig:LeftHandThumb2', 'mixamorig_LeftHandThumb2', 'lefthandthumb2',
        '左親指２', 'ik_thumb_2_l', 'thumb_intermediate.l'
    ],
    'thumb_3_left': [
        # Thumb distal segment (segment 3)
        'thumb_3_l', 'thumb3l', 'lthumb3', 'thumb_distal_l', 'thumbdistal_l',
        'thumb.3.l', 'Thumb_3_L', 'Thumb.3.L', 'LeftThumb3', 'Left_Thumb_3',
        'valvebipedbip01lthumb3', 'valvebipedbip01lfinger02', 'bip01lthumb3',
        'mixamorig:LeftHandThumb3', 'mixamorig_LeftHandThumb3', 'lefthandthumb3',
        '左親指３', 'ik_thumb_3_l', 'thumb_distal.l'
    ],

    # Left Index finger segments
    'index_1_left': [
        # Index proximal segment (segment 1)
        'index_1_l', 'index1l', 'lindex1', 'index_proximal_l', 'indexproximal_l',
        'index.1.l', 'Index_1_L', 'Index.1.L', 'LeftIndex1', 'Left_Index_1',
        'valvebipedbip01lindexfinger1', 'valvebipedbip01lfinger1', 'bip01lindex1',
        'mixamorig:LeftHandIndex1', 'mixamorig_LeftHandIndex1', 'lefthandindex1',
        '左人差指１', 'ik_index_1_l', 'index_proximal.l'
    ],
    'index_2_left': [
        # Index intermediate segment (segment 2)
        'index_2_l', 'index2l', 'lindex2', 'index_intermediate_l', 'indexintermediate_l',
        'index.2.l', 'Index_2_L', 'Index.2.L', 'LeftIndex2', 'Left_Index_2',
        'valvebipedbip01lindexfinger2', 'valvebipedbip01lfinger11', 'bip01lindex2',
        'mixamorig:LeftHandIndex2', 'mixamorig_LeftHandIndex2', 'lefthandindex2',
        '左人差指２', 'ik_index_2_l', 'index_intermediate.l'
    ],
    'index_3_left': [
        # Index distal segment (segment 3)
        'index_3_l', 'index3l', 'lindex3', 'index_distal_l', 'indexdistal_l',
        'index.3.l', 'Index_3_L', 'Index.3.L', 'LeftIndex3', 'Left_Index_3',
        'valvebipedbip01lindexfinger3', 'valvebipedbip01lfinger12', 'bip01lindex3',
        'mixamorig:LeftHandIndex3', 'mixamorig_LeftHandIndex3', 'lefthandindex3',
        '左人差指３', 'ik_index_3_l', 'index_distal.l'
    ],

    # Left Middle finger segments
    'middle_1_left': [
        # Middle proximal segment (segment 1)
        'middle_1_l', 'middle1l', 'lmiddle1', 'middle_proximal_l', 'middleproximal_l',
        'middle.1.l', 'Middle_1_L', 'Middle.1.L', 'LeftMiddle1', 'Left_Middle_1',
        'valvebipedbip01lmiddlefinger1', 'valvebipedbip01lfinger2', 'bip01lmiddle1',
        'mixamorig:LeftHandMiddle1', 'mixamorig_LeftHandMiddle1', 'lefthandmiddle1',
        '左中指１', 'ik_middle_1_l', 'middle_proximal.l'
    ],
    'middle_2_left': [
        # Middle intermediate segment (segment 2)
        'middle_2_l', 'middle2l', 'lmiddle2', 'middle_intermediate_l', 'middleintermediate_l',
        'middle.2.l', 'Middle_2_L', 'Middle.2.L', 'LeftMiddle2', 'Left_Middle_2',
        'valvebipedbip01lmiddlefinger2', 'valvebipedbip01lfinger21', 'bip01lmiddle2',
        'mixamorig:LeftHandMiddle2', 'mixamorig_LeftHandMiddle2', 'lefthandmiddle2',
        '左中指２', 'ik_middle_2_l', 'middle_intermediate.l'
    ],
    'middle_3_left': [
        # Middle distal segment (segment 3)
        'middle_3_l', 'middle3l', 'lmiddle3', 'middle_distal_l', 'middledistal_l',
        'middle.3.l', 'Middle_3_L', 'Middle.3.L', 'LeftMiddle3', 'Left_Middle_3',
        'valvebipedbip01lmiddlefinger3', 'valvebipedbip01lfinger22', 'bip01lmiddle3',
        'mixamorig:LeftHandMiddle3', 'mixamorig_LeftHandMiddle3', 'lefthandmiddle3',
        '左中指３', 'ik_middle_3_l', 'middle_distal.l'
    ],

    # Left Ring finger segments
    'ring_1_left': [
        # Ring proximal segment (segment 1)
        'ring_1_l', 'ring1l', 'lring1', 'ring_proximal_l', 'ringproximal_l',
        'ring.1.l', 'Ring_1_L', 'Ring.1.L', 'LeftRing1', 'Left_Ring_1',
        'valvebipedbip01lringfinger1', 'valvebipedbip01lfinger3', 'bip01lring1',
        'mixamorig:LeftHandRing1', 'mixamorig_LeftHandRing1', 'lefthandring1',
        '左薬指１', 'ik_ring_1_l', 'ring_proximal.l'
    ],
    'ring_2_left': [
        # Ring intermediate segment (segment 2)
        'ring_2_l', 'ring2l', 'lring2', 'ring_intermediate_l', 'ringintermediate_l',
        'ring.2.l', 'Ring_2_L', 'Ring.2.L', 'LeftRing2', 'Left_Ring_2',
        'valvebipedbip01lringfinger2', 'valvebipedbip01lfinger31', 'bip01lring2',
        'mixamorig:LeftHandRing2', 'mixamorig_LeftHandRing2', 'lefthandring2',
        '左薬指２', 'ik_ring_2_l', 'ring_intermediate.l'
    ],
    'ring_3_left': [
        # Ring distal segment (segment 3)
        'ring_3_l', 'ring3l', 'lring3', 'ring_distal_l', 'ringdistal_l',
        'ring.3.l', 'Ring_3_L', 'Ring.3.L', 'LeftRing3', 'Left_Ring_3',
        'valvebipedbip01lringfinger3', 'valvebipedbip01lfinger32', 'bip01lring3',
        'mixamorig:LeftHandRing3', 'mixamorig_LeftHandRing3', 'lefthandring3',
        '左薬指３', 'ik_ring_3_l', 'ring_distal.l'
    ],

    # Left Pinky finger segments
    'pinky_1_left': [
        # Pinky proximal segment (segment 1)
        'pinky_1_l', 'pinky1l', 'lpinky1', 'pinky_proximal_l', 'pinkyproximal_l',
        'little_1_l', 'little1l', 'llittle1', 'little_proximal_l', 'littleproximal_l',
        'pinky.1.l', 'Pinky_1_L', 'Pinky.1.L', 'LeftPinky1', 'Left_Pinky_1',
        'valvebipedbip01lpinky1', 'valvebipedbip01lfinger4', 'bip01lpinky1',
        'mixamorig:LeftHandPinky1', 'mixamorig_LeftHandPinky1', 'lefthandpinky1',
        '左小指１', 'ik_pinky_1_l', 'pinky_proximal.l'
    ],
    'pinky_2_left': [
        # Pinky intermediate segment (segment 2)
        'pinky_2_l', 'pinky2l', 'lpinky2', 'pinky_intermediate_l', 'pinkyintermediate_l',
        'little_2_l', 'little2l', 'llittle2', 'little_intermediate_l', 'littleintermediate_l',
        'pinky.2.l', 'Pinky_2_L', 'Pinky.2.L', 'LeftPinky2', 'Left_Pinky_2',
        'valvebipedbip01lpinky2', 'valvebipedbip01lfinger41', 'bip01lpinky2',
        'mixamorig:LeftHandPinky2', 'mixamorig_LeftHandPinky2', 'lefthandpinky2',
        '左小指２', 'ik_pinky_2_l', 'pinky_intermediate.l'
    ],
    'pinky_3_left': [
        # Pinky distal segment (segment 3)
        'pinky_3_l', 'pinky3l', 'lpinky3', 'pinky_distal_l', 'pinkydistal_l',
        'little_3_l', 'little3l', 'llittle3', 'little_distal_l', 'littledistal_l',
        'pinky.3.l', 'Pinky_3_L', 'Pinky.3.L', 'LeftPinky3', 'Left_Pinky_3',
        'valvebipedbip01lpinky3', 'valvebipedbip01lfinger42', 'bip01lpinky3',
        'mixamorig:LeftHandPinky3', 'mixamorig_LeftHandPinky3', 'lefthandpinky3',
        '左小指３', 'ik_pinky_3_l', 'pinky_distal.l'
    ],

    # RIGHT HAND FINGER SEGMENTS (mirror structure for right side)
    
    # Right Thumb segments
    'thumb_1_right': [
        # Thumb proximal segment (segment 1)
        'thumb_1_r', 'thumb1r', 'rthumb1', 'thumb_proximal_r', 'thumbproximal_r',
        'thumb.1.r', 'Thumb_1_R', 'Thumb.1.R', 'RightThumb1', 'Right_Thumb_1',
        'valvebipedbip01rthumb1', 'valvebipedbip01rfinger0', 'bip01rthumb1',
        'mixamorig:RightHandThumb1', 'mixamorig_RightHandThumb1', 'righthandthumb1',
        '右親指１', 'ik_thumb_1_r', 'thumb_proximal.r'
    ],
    'thumb_2_right': [
        # Thumb intermediate segment (segment 2)
        'thumb_2_r', 'thumb2r', 'rthumb2', 'thumb_intermediate_r', 'thumbintermediate_r',
        'thumb.2.r', 'Thumb_2_R', 'Thumb.2.R', 'RightThumb2', 'Right_Thumb_2',
        'valvebipedbip01rthumb2', 'valvebipedbip01rfinger01', 'bip01rthumb2',
        'mixamorig:RightHandThumb2', 'mixamorig_RightHandThumb2', 'righthandthumb2',
        '右親指２', 'ik_thumb_2_r', 'thumb_intermediate.r'
    ],
    'thumb_3_right': [
        # Thumb distal segment (segment 3)
        'thumb_3_r', 'thumb3r', 'rthumb3', 'thumb_distal_r', 'thumbdistal_r',
        'thumb.3.r', 'Thumb_3_R', 'Thumb.3.R', 'RightThumb3', 'Right_Thumb_3',
        'valvebipedbip01rthumb3', 'valvebipedbip01rfinger02', 'bip01rthumb3',
        'mixamorig:RightHandThumb3', 'mixamorig_RightHandThumb3', 'righthandthumb3',
        '右親指３', 'ik_thumb_3_r', 'thumb_distal.r'
    ],

    # Right Index finger segments
    'index_1_right': [
        # Index proximal segment (segment 1)
        'index_1_r', 'index1r', 'rindex1', 'index_proximal_r', 'indexproximal_r',
        'index.1.r', 'Index_1_R', 'Index.1.R', 'RightIndex1', 'Right_Index_1',
        'valvebipedbip01rindexfinger1', 'valvebipedbip01rfinger1', 'bip01rindex1',
        'mixamorig:RightHandIndex1', 'mixamorig_RightHandIndex1', 'righthandindex1',
        '右人差指１', 'ik_index_1_r', 'index_proximal.r'
    ],
    'index_2_right': [
        # Index intermediate segment (segment 2)
        'index_2_r', 'index2r', 'rindex2', 'index_intermediate_r', 'indexintermediate_r',
        'index.2.r', 'Index_2_R', 'Index.2.R', 'RightIndex2', 'Right_Index_2',
        'valvebipedbip01rindexfinger2', 'valvebipedbip01rfinger11', 'bip01rindex2',
        'mixamorig:RightHandIndex2', 'mixamorig_RightHandIndex2', 'righthandindex2',
        '右人差指２', 'ik_index_2_r', 'index_intermediate.r'
    ],
    'index_3_right': [
        # Index distal segment (segment 3)
        'index_3_r', 'index3r', 'rindex3', 'index_distal_r', 'indexdistal_r',
        'index.3.r', 'Index_3_R', 'Index.3.R', 'RightIndex3', 'Right_Index_3',
        'valvebipedbip01rindexfinger3', 'valvebipedbip01rfinger12', 'bip01rindex3',
        'mixamorig:RightHandIndex3', 'mixamorig_RightHandIndex3', 'righthandindex3',
        '右人差指３', 'ik_index_3_r', 'index_distal.r'
    ],

    # Right Middle finger segments
    'middle_1_right': [
        # Middle proximal segment (segment 1)
        'middle_1_r', 'middle1r', 'rmiddle1', 'middle_proximal_r', 'middleproximal_r',
        'middle.1.r', 'Middle_1_R', 'Middle.1.R', 'RightMiddle1', 'Right_Middle_1',
        'valvebipedbip01rmiddlefinger1', 'valvebipedbip01rfinger2', 'bip01rmiddle1',
        'mixamorig:RightHandMiddle1', 'mixamorig_RightHandMiddle1', 'righthandmiddle1',
        '右中指１', 'ik_middle_1_r', 'middle_proximal.r'
    ],
    'middle_2_right': [
        # Middle intermediate segment (segment 2)
        'middle_2_r', 'middle2r', 'rmiddle2', 'middle_intermediate_r', 'middleintermediate_r',
        'middle.2.r', 'Middle_2_R', 'Middle.2.R', 'RightMiddle2', 'Right_Middle_2',
        'valvebipedbip01rmiddlefinger2', 'valvebipedbip01rfinger21', 'bip01rmiddle2',
        'mixamorig:RightHandMiddle2', 'mixamorig_RightHandMiddle2', 'righthandmiddle2',
        '右中指２', 'ik_middle_2_r', 'middle_intermediate.r'
    ],
    'middle_3_right': [
        # Middle distal segment (segment 3)
        'middle_3_r', 'middle3r', 'rmiddle3', 'middle_distal_r', 'middledistal_r',
        'middle.3.r', 'Middle_3_R', 'Middle.3.R', 'RightMiddle3', 'Right_Middle_3',
        'valvebipedbip01rmiddlefinger3', 'valvebipedbip01rfinger22', 'bip01rmiddle3',
        'mixamorig:RightHandMiddle3', 'mixamorig_RightHandMiddle3', 'righthandmiddle3',
        '右中指３', 'ik_middle_3_r', 'middle_distal.r'
    ],

    # Right Ring finger segments
    'ring_1_right': [
        # Ring proximal segment (segment 1)
        'ring_1_r', 'ring1r', 'rring1', 'ring_proximal_r', 'ringproximal_r',
        'ring.1.r', 'Ring_1_R', 'Ring.1.R', 'RightRing1', 'Right_Ring_1',
        'valvebipedbip01rringfinger1', 'valvebipedbip01rfinger3', 'bip01rring1',
        'mixamorig:RightHandRing1', 'mixamorig_RightHandRing1', 'righthandring1',
        '右薬指１', 'ik_ring_1_r', 'ring_proximal.r'
    ],
    'ring_2_right': [
        # Ring intermediate segment (segment 2)
        'ring_2_r', 'ring2r', 'rring2', 'ring_intermediate_r', 'ringintermediate_r',
        'ring.2.r', 'Ring_2_R', 'Ring.2.R', 'RightRing2', 'Right_Ring_2',
        'valvebipedbip01rringfinger2', 'valvebipedbip01rfinger31', 'bip01rring2',
        'mixamorig:RightHandRing2', 'mixamorig_RightHandRing2', 'righthandring2',
        '右薬指２', 'ik_ring_2_r', 'ring_intermediate.r'
    ],
    'ring_3_right': [
        # Ring distal segment (segment 3)
        'ring_3_r', 'ring3r', 'rring3', 'ring_distal_r', 'ringdistal_r',
        'ring.3.r', 'Ring_3_R', 'Ring.3.R', 'RightRing3', 'Right_Ring_3',
        'valvebipedbip01rringfinger3', 'valvebipedbip01rfinger32', 'bip01rring3',
        'mixamorig:RightHandRing3', 'mixamorig_RightHandRing3', 'righthandring3',
        '右薬指３', 'ik_ring_3_r', 'ring_distal.r'
    ],

    # Right Pinky finger segments
    'pinky_1_right': [
        # Pinky proximal segment (segment 1)
        'pinky_1_r', 'pinky1r', 'rpinky1', 'pinky_proximal_r', 'pinkyproximal_r',
        'little_1_r', 'little1r', 'rlittle1', 'little_proximal_r', 'littleproximal_r',
        'pinky.1.r', 'Pinky_1_R', 'Pinky.1.R', 'RightPinky1', 'Right_Pinky_1',
        'valvebipedbip01rpinky1', 'valvebipedbip01rfinger4', 'bip01rpinky1',
        'mixamorig:RightHandPinky1', 'mixamorig_RightHandPinky1', 'righthandpinky1',
        '右小指１', 'ik_pinky_1_r', 'pinky_proximal.r'
    ],
    'pinky_2_right': [
        # Pinky intermediate segment (segment 2)
        'pinky_2_r', 'pinky2r', 'rpinky2', 'pinky_intermediate_r', 'pinkyintermediate_r',
        'little_2_r', 'little2r', 'rlittle2', 'little_intermediate_r', 'littleintermediate_r',
        'pinky.2.r', 'Pinky_2_R', 'Pinky.2.R', 'RightPinky2', 'Right_Pinky_2',
        'valvebipedbip01rpinky2', 'valvebipedbip01rfinger41', 'bip01rpinky2',
        'mixamorig:RightHandPinky2', 'mixamorig_RightHandPinky2', 'righthandpinky2',
        '右小指２', 'ik_pinky_2_r', 'pinky_intermediate.r'
    ],
    'pinky_3_right': [
        # Pinky distal segment (segment 3)
        'pinky_3_r', 'pinky3r', 'rpinky3', 'pinky_distal_r', 'pinkydistal_r',
        'little_3_r', 'little3r', 'rlittle3', 'little_distal_r', 'littledistal_r',
        'pinky.3.r', 'Pinky_3_R', 'Pinky.3.R', 'RightPinky3', 'Right_Pinky_3',
        'valvebipedbip01rpinky3', 'valvebipedbip01rfinger42', 'bip01rpinky3',
        'mixamorig:RightHandPinky3', 'mixamorig_RightHandPinky3', 'righthandpinky3',
        '右小指３', 'ik_pinky_3_r', 'pinky_distal.r'
    ],
    
    # Detailed toe bones - each bone type gets its own category for proper opposite matching
    # Left toe bones
    'toe_little_proximal_left': [
        'toe_little_proximal_l', 'toe_little_proximal_l', 'toe_little_proximal.l',
        'little_toe_proximal_l', 'little_toe_proximal_l', 'littletoe_proximal_l'
    ],
    'toe_little_intermediate_left': [
        'toe_little_intermediate_l', 'toe_little_intermediate_l', 'toe_little_intermediate.l',
        'little_toe_intermediate_l', 'little_toe_intermediate_l', 'littletoe_intermediate_l'
    ],
    'toe_little_distal_left': [
        'toe_little_distal_l', 'toe_little_distal_l', 'toe_little_distal.l',
        'little_toe_distal_l', 'little_toe_distal_l', 'littletoe_distal_l'
    ],
    'toe_ring_proximal_left': [
        'toe_ring_proximal_l', 'toe_ring_proximal_l', 'toe_ring_proximal.l',
        'ring_toe_proximal_l', 'ring_toe_proximal_l', 'ringtoe_proximal_l'
    ],
    'toe_ring_intermediate_left': [
        'toe_ring_intermediate_l', 'toe_ring_intermediate_l', 'toe_ring_intermediate.l',
        'ring_toe_intermediate_l', 'ring_toe_intermediate_l', 'ringtoe_intermediate_l'
    ],
    'toe_ring_distal_left': [
        'toe_ring_distal_l', 'toe_ring_distal_l', 'toe_ring_distal.l',
        'ring_toe_distal_l', 'ring_toe_distal_l', 'ringtoe_distal_l'
    ],
    'toe_middle_proximal_left': [
        'toe_middle_proximal_l', 'toe_middle_proximal_l', 'toe_middle_proximal.l',
        'middle_toe_proximal_l', 'middle_toe_proximal_l', 'middletoe_proximal_l'
    ],
    'toe_middle_intermediate_left': [
        'toe_middle_intermediate_l', 'toe_middle_intermediate_l', 'toe_middle_intermediate.l',
        'middle_toe_intermediate_l', 'middle_toe_intermediate_l', 'middletoe_intermediate_l'
    ],
    'toe_middle_distal_left': [
        'toe_middle_distal_l', 'toe_middle_distal_l', 'toe_middle_distal.l',
        'middle_toe_distal_l', 'middle_toe_distal_l', 'middletoe_distal_l'
    ],
    'toe_index_proximal_left': [
        'toe_index_proximal_l', 'toe_index_proximal_l', 'toe_index_proximal.l',
        'index_toe_proximal_l', 'index_toe_proximal_l', 'indextoe_proximal_l'
    ],
    'toe_index_intermediate_left': [
        'toe_index_intermediate_l', 'toe_index_intermediate_l', 'toe_index_intermediate.l',
        'index_toe_intermediate_l', 'index_toe_intermediate_l', 'indextoe_intermediate_l'
    ],
    'toe_index_distal_left': [
        'toe_index_distal_l', 'toe_index_distal_l', 'toe_index_distal.l',
        'index_toe_distal_l', 'index_toe_distal_l', 'indextoe_distal_l'
    ],
    'toe_thumb_proximal_left': [
        'toe_thumb_proximal_l', 'toe_thumb_proximal_l', 'toe_thumb_proximal.l',
        'thumb_toe_proximal_l', 'thumb_toe_proximal_l', 'thumbtoe_proximal_l',
        'big_toe_proximal_l', 'big_toe_proximal_l', 'bigtoe_proximal_l'
    ],
    'toe_thumb_intermediate_left': [
        'toe_thumb_intermediate_l', 'toe_thumb_intermediate_l', 'toe_thumb_intermediate.l',
        'thumb_toe_intermediate_l', 'thumb_toe_intermediate_l', 'thumbtoe_intermediate_l',
        'big_toe_intermediate_l', 'big_toe_intermediate_l', 'bigtoe_intermediate_l'
    ],
    'toe_thumb_distal_left': [
        'toe_thumb_distal_l', 'toe_thumb_distal_l', 'toe_thumb_distal.l',
        'thumb_toe_distal_l', 'thumb_toe_distal_l', 'thumbtoe_distal_l',
        'big_toe_distal_l', 'big_toe_distal_l', 'bigtoe_distal_l'
    ],
    
    # Right toe bones
    'toe_little_proximal_right': [
        'toe_little_proximal_r', 'toe_little_proximal_r', 'toe_little_proximal.r',
        'little_toe_proximal_r', 'little_toe_proximal_r', 'littletoe_proximal_r'
    ],
    'toe_little_intermediate_right': [
        'toe_little_intermediate_r', 'toe_little_intermediate_r', 'toe_little_intermediate.r',
        'little_toe_intermediate_r', 'little_toe_intermediate_r', 'littletoe_intermediate_r'
    ],
    'toe_little_distal_right': [
        'toe_little_distal_r', 'toe_little_distal_r', 'toe_little_distal.r',
        'little_toe_distal_r', 'little_toe_distal_r', 'littletoe_distal_r'
    ],
    'toe_ring_proximal_right': [
        'toe_ring_proximal_r', 'toe_ring_proximal_r', 'toe_ring_proximal.r',
        'ring_toe_proximal_r', 'ring_toe_proximal_r', 'ringtoe_proximal_r'
    ],
    'toe_ring_intermediate_right': [
        'toe_ring_intermediate_r', 'toe_ring_intermediate_r', 'toe_ring_intermediate.r',
        'ring_toe_intermediate_r', 'ring_toe_intermediate_r', 'ringtoe_intermediate_r'
    ],
    'toe_ring_distal_right': [
        'toe_ring_distal_r', 'toe_ring_distal_r', 'toe_ring_distal.r',
        'ring_toe_distal_r', 'ring_toe_distal_r', 'ringtoe_distal_r'
    ],
    'toe_middle_proximal_right': [
        'toe_middle_proximal_r', 'toe_middle_proximal_r', 'toe_middle_proximal.r',
        'middle_toe_proximal_r', 'middle_toe_proximal_r', 'middletoe_proximal_r'
    ],
    'toe_middle_intermediate_right': [
        'toe_middle_intermediate_r', 'toe_middle_intermediate_r', 'toe_middle_intermediate.r',
        'middle_toe_intermediate_r', 'middle_toe_intermediate_r', 'middletoe_intermediate_r'
    ],
    'toe_middle_distal_right': [
        'toe_middle_distal_r', 'toe_middle_distal_r', 'toe_middle_distal.r',
        'middle_toe_distal_r', 'middle_toe_distal_r', 'middletoe_distal_r'
    ],
    'toe_index_proximal_right': [
        'toe_index_proximal_r', 'toe_index_proximal_r', 'toe_index_proximal.r',
        'index_toe_proximal_r', 'index_toe_proximal_r', 'indextoe_proximal_r'
    ],
    'toe_index_intermediate_right': [
        'toe_index_intermediate_r', 'toe_index_intermediate_r', 'toe_index_intermediate.r',
        'index_toe_intermediate_r', 'index_toe_intermediate_r', 'indextoe_intermediate_r'
    ],
    'toe_index_distal_right': [
        'toe_index_distal_r', 'toe_index_distal_r', 'toe_index_distal.r',
        'index_toe_distal_r', 'index_toe_distal_r', 'indextoe_distal_r'
    ],
    'toe_thumb_proximal_right': [
        'toe_thumb_proximal_r', 'toe_thumb_proximal_r', 'toe_thumb_proximal.r',
        'thumb_toe_proximal_r', 'thumb_toe_proximal_r', 'thumbtoe_proximal_r',
        'big_toe_proximal_r', 'big_toe_proximal_r', 'bigtoe_proximal_r'
    ],
    'toe_thumb_intermediate_right': [
        'toe_thumb_intermediate_r', 'toe_thumb_intermediate_r', 'toe_thumb_intermediate.r',
        'thumb_toe_intermediate_r', 'thumb_toe_intermediate_r', 'thumbtoe_intermediate_r',
        'big_toe_intermediate_r', 'big_toe_intermediate_r', 'bigtoe_intermediate_r'
    ],
    'toe_thumb_distal_right': [
        'toe_thumb_distal_r', 'toe_thumb_distal_r', 'toe_thumb_distal.r',
        'thumb_toe_distal_r', 'thumb_toe_distal_r', 'thumbtoe_distal_r',
        'big_toe_distal_r', 'big_toe_distal_r', 'bigtoe_distal_r'
    ],
    
    # Eye bones - critical for VRChat facial animation
    'eye_left': [
        'eye.l', 'eye_l', 'lefteye', 'left_eye', 'eyeleft', 'eyel', 'leye',
        'lefteye', 'left_eye', 'eyeleft', 'eye_left', 'eye.l',
        '左目', 'ik_左目', 'left_eyeball', 'eyeball.l', 'eyeball_l'
    ],
    'eye_right': [
        'eye.r', 'eye_r', 'righteye', 'right_eye', 'eyeright', 'eyer', 'reye',
        'righteye', 'right_eye', 'eyeright', 'eye_right', 'eye.r',
        '右目', 'ik_右目', 'right_eyeball', 'eyeball.r', 'eyeball_r'
    ],
    
    # Metacarpal finger bones (base segments) - complete 4-segment finger chains
    'thumb_metacarpal_left': [
        'thumb_0_l', 'thumb_metacarpal_l', 'thumb_0.l', 'thumb_metacarpal.l',
        'thumb_0_l', 'thumb_metacarpal_l', 'thumbmetacarpal_l', 'thumb_meta_l',
        'leftthumbmetacarpal', 'left_thumb_metacarpal'
    ],
    'thumb_metacarpal_right': [
        'thumb_0_r', 'thumb_metacarpal_r', 'thumb_0.r', 'thumb_metacarpal.r',
        'thumb_0_r', 'thumb_metacarpal_r', 'thumbmetacarpal_r', 'thumb_meta_r',
        'rightthumbmetacarpal', 'right_thumb_metacarpal'
    ],
    'index_metacarpal_left': [
        'index_0_l', 'index_metacarpal_l', 'index_0.l', 'index_metacarpal.l',
        'index_0_l', 'index_metacarpal_l', 'indexmetacarpal_l', 'index_meta_l',
        'leftindexmetacarpal', 'left_index_metacarpal'
    ],
    'index_metacarpal_right': [
        'index_0_r', 'index_metacarpal_r', 'index_0.r', 'index_metacarpal.r',
        'index_0_r', 'index_metacarpal_r', 'indexmetacarpal_r', 'index_meta_r',
        'rightindexmetacarpal', 'right_index_metacarpal'
    ],
    'middle_metacarpal_left': [
        'middle_0_l', 'middle_metacarpal_l', 'middle_0.l', 'middle_metacarpal.l',
        'middle_0_l', 'middle_metacarpal_l', 'middlemetacarpal_l', 'middle_meta_l',
        'leftmiddlemetacarpal', 'left_middle_metacarpal'
    ],
    'middle_metacarpal_right': [
        'middle_0_r', 'middle_metacarpal_r', 'middle_0.r', 'middle_metacarpal.r',
        'middle_0_r', 'middle_metacarpal_r', 'middlemetacarpal_r', 'middle_meta_r',
        'rightmiddlemetacarpal', 'right_middle_metacarpal'
    ],
    'ring_metacarpal_left': [
        'ring_0_l', 'ring_metacarpal_l', 'ring_0.l', 'ring_metacarpal.l',
        'ring_0_l', 'ring_metacarpal_l', 'ringmetacarpal_l', 'ring_meta_l',
        'leftringmetacarpal', 'left_ring_metacarpal'
    ],
    'ring_metacarpal_right': [
        'ring_0_r', 'ring_metacarpal_r', 'ring_0.r', 'ring_metacarpal.r',
        'ring_0_r', 'ring_metacarpal_r', 'ringmetacarpal_r', 'ring_meta_r',
        'rightringmetacarpal', 'right_ring_metacarpal'
    ],
    'pinky_metacarpal_left': [
        'pinky_0_l', 'pinky_metacarpal_l', 'pinky_0.l', 'pinky_metacarpal.l',
        'pinky_0_l', 'pinky_metacarpal_l', 'pinkymetacarpal_l', 'pinky_meta_l',
        'little_0_l', 'little_metacarpal_l', 'leftpinkymetacarpal', 'left_pinky_metacarpal'
    ],
    'pinky_metacarpal_right': [
        'pinky_0_r', 'pinky_metacarpal_r', 'pinky_0.r', 'pinky_metacarpal.r',
        'pinky_0_r', 'pinky_metacarpal_r', 'pinkymetacarpal_r', 'pinky_meta_r',
        'little_0_r', 'little_metacarpal_r', 'rightpinkymetacarpal', 'right_pinky_metacarpal'
    ],
    
    # Breast bones - for adult avatar compatibility
    'breast_upper_left': [
        'breast_upper_1_l', 'breast_upper_l', 'breast_1_l', 'breast.l',
        'breast_upper_1_l', 'breast_upper_l', 'breast_1_l', 'breast.l',
        'leftbreast', 'left_breast', 'breastl', 'lbreast', 'leftbreast', 'left_breast'
    ],
    'breast_upper_right': [
        'breast_upper_1_r', 'breast_upper_r', 'breast_1_r', 'breast.r',
        'breast_upper_1_r', 'breast_upper_r', 'breast_1_r', 'breast.r',
        'rightbreast', 'right_breast', 'breastr', 'rbreast', 'rightbreast', 'right_breast'
    ],
    'breast_lower_left': [
        'breast_upper_2_l', 'breast_lower_l', 'breast_2_l', 'breast_secondary_l',
        'breast_upper_2_l', 'breast_lower_l', 'breast_2_l', 'breast_secondary_l',
        'leftbreast2', 'left_breast_2', 'breastl2', 'lbreast2'
    ],
    'breast_lower_right': [
        'breast_upper_2_r', 'breast_lower_r', 'breast_2_r', 'breast_secondary_r',
        'breast_upper_2_r', 'breast_lower_r', 'breast_2_r', 'breast_secondary_r',
        'rightbreast2', 'right_breast_2', 'breastr2', 'rbreast2'
    ]
}

# Inheritance relationships - when parent bones change, these child categories should be checked
BONE_INHERITANCE_CHAINS = {
    'core': ['eye_left', 'eye_right'],  # Core/head changes can affect eye bones
    'shoulder_left': [],  # Shoulder bones are independent
    'shoulder_right': [],  # Shoulder bones are independent
    'upper_arm_left': ['forearm_left', 'hand_left'],  # Upper arm changes affect forearm and hand
    'forearm_left': ['hand_left'],  # Forearm changes affect hand
    'hand_left': [  # Left hand changes affect left finger segments and metacarpals
        # Metacarpal bones (segment 0)
        'thumb_metacarpal_left', 'index_metacarpal_left', 'middle_metacarpal_left',
        'ring_metacarpal_left', 'pinky_metacarpal_left',
        # Individual finger segments (1, 2, 3) - Avatar Toolkit approach
        'thumb_1_left', 'thumb_2_left', 'thumb_3_left',
        'index_1_left', 'index_2_left', 'index_3_left',
        'middle_1_left', 'middle_2_left', 'middle_3_left',
        'ring_1_left', 'ring_2_left', 'ring_3_left',
        'pinky_1_left', 'pinky_2_left', 'pinky_3_left'
    ],
    'upper_arm_right': ['forearm_right', 'hand_right'],  # Upper arm changes affect forearm and hand
    'forearm_right': ['hand_right'],  # Forearm changes affect hand
    'hand_right': [  # Right hand changes affect right finger segments and metacarpals
        # Metacarpal bones (segment 0)
        'thumb_metacarpal_right', 'index_metacarpal_right', 'middle_metacarpal_right',
        'ring_metacarpal_right', 'pinky_metacarpal_right',
        # Individual finger segments (1, 2, 3) - Avatar Toolkit approach
        'thumb_1_right', 'thumb_2_right', 'thumb_3_right',
        'index_1_right', 'index_2_right', 'index_3_right',
        'middle_1_right', 'middle_2_right', 'middle_3_right',
        'ring_1_right', 'ring_2_right', 'ring_3_right',
        'pinky_1_right', 'pinky_2_right', 'pinky_3_right'
    ],
    'upper_leg_left': ['lower_leg_left', 'foot_left', 'toe_left'],  # Upper leg changes affect lower leg, foot, toe
    'lower_leg_left': ['foot_left', 'toe_left'],  # Lower leg changes affect foot and toe
    'foot_left': ['toe_left'],  # Foot changes affect toe
    'toe_left': [  # Left toe changes affect left detailed toe bones
        'toe_little_proximal_left', 'toe_little_intermediate_left', 'toe_little_distal_left',
        'toe_ring_proximal_left', 'toe_ring_intermediate_left', 'toe_ring_distal_left',
        'toe_middle_proximal_left', 'toe_middle_intermediate_left', 'toe_middle_distal_left',
        'toe_index_proximal_left', 'toe_index_intermediate_left', 'toe_index_distal_left',
        'toe_thumb_proximal_left', 'toe_thumb_intermediate_left', 'toe_thumb_distal_left'
    ],
    'upper_leg_right': ['lower_leg_right', 'foot_right', 'toe_right'],  # Upper leg changes affect lower leg, foot, toe
    'lower_leg_right': ['foot_right', 'toe_right'],  # Lower leg changes affect foot and toe
    'foot_right': ['toe_right'],  # Foot changes affect toe
    'toe_right': [  # Right toe changes affect right detailed toe bones
        'toe_little_proximal_right', 'toe_little_intermediate_right', 'toe_little_distal_right',
        'toe_ring_proximal_right', 'toe_ring_intermediate_right', 'toe_ring_distal_right',
        'toe_middle_proximal_right', 'toe_middle_intermediate_right', 'toe_middle_distal_right',
        'toe_index_proximal_right', 'toe_index_intermediate_right', 'toe_index_distal_right',
        'toe_thumb_proximal_right', 'toe_thumb_intermediate_right', 'toe_thumb_distal_right'
    ],
    # Breast bones are independent - no inheritance chains needed as they don't typically have child bones
}

# Finger hierarchy structure (Avatar Toolkit style) - defines parent-child relationships
FINGER_HIERARCHY = {
    'left': [
        # (parent, child1, child2, child3) - hand connects to metacarpal, then segments 1->2->3
        ('arms_left', 'thumb_metacarpal_left', 'thumb_1_left', 'thumb_2_left', 'thumb_3_left'),
        ('arms_left', 'index_metacarpal_left', 'index_1_left', 'index_2_left', 'index_3_left'),
        ('arms_left', 'middle_metacarpal_left', 'middle_1_left', 'middle_2_left', 'middle_3_left'),
        ('arms_left', 'ring_metacarpal_left', 'ring_1_left', 'ring_2_left', 'ring_3_left'),
        ('arms_left', 'pinky_metacarpal_left', 'pinky_1_left', 'pinky_2_left', 'pinky_3_left')
    ],
    'right': [
        # (parent, child1, child2, child3) - hand connects to metacarpal, then segments 1->2->3
        ('arms_right', 'thumb_metacarpal_right', 'thumb_1_right', 'thumb_2_right', 'thumb_3_right'),
        ('arms_right', 'index_metacarpal_right', 'index_1_right', 'index_2_right', 'index_3_right'),
        ('arms_right', 'middle_metacarpal_right', 'middle_1_right', 'middle_2_right', 'middle_3_right'),
        ('arms_right', 'ring_metacarpal_right', 'ring_1_right', 'ring_2_right', 'ring_3_right'),
        ('arms_right', 'pinky_metacarpal_right', 'pinky_1_right', 'pinky_2_right', 'pinky_3_right')
    ]
}

# Logical bone groupings for more flexible access while maintaining mirror tool compatibility
BONE_LOGICAL_GROUPS = {
    # Core bone sub-groups (while keeping main 'core' category for mirror tool)
    'core_hips': [
        # Hips/Pelvis variations - Standard, Valve, Mixamo, Japanese, IK
        'hips', 'hip', 'pelvis', 'root', '腰', 'ik_腰', 'ik_hips',
        'valvebipedbip01pelvis', 'valvebipedbip01hip', 'hips', 'hip', 'pelvis', 'root',
        'mixamorig:hips', 'mixamorig_hips', 'mixamorighips', 'bip01pelvis', 'bip01_pelvis'
    ],
    'core_spine': [
        # Spine variations - Standard, Valve, Mixamo, Japanese, IK
        'spine', 'back', 'torso', '脊椎', 'ik_脊椎', 'ik_spine',
        'valvebipedbip01spine', 'valvebipedbip01spine1', 'spine', 'back', 'torso',
        'mixamorig:spine', 'mixamorig:spine1', 'mixamorig_spine', 'mixamorig_spine1',
        'bip01spine', 'bip01_spine', 'bip01spine1', 'bip01_spine1'
    ],
    'core_chest': [
        # Chest variations - Standard, Valve, Mixamo, Japanese, IK
        'chest', 'ribcage', 'upper_body', '胸', 'ik_胸', 'ik_chest',
        'upperchest', 'upper_chest', '上胸', 'ik_上胸', 'ik_upperchest',
        'valvebipedbip01spine2', 'valvebipedbip01spine3', 'chest', 'upperchest', 'upper_chest',
        'mixamorig:spine2', 'mixamorig:spine3', 'mixamorig_spine2', 'mixamorig_spine3',
        'bip01spine2', 'bip01_spine2', 'bip01spine3', 'bip01_spine3'
    ],
    'core_neck': [
        # Neck variations - Standard, Valve, Mixamo, Japanese, IK
        'neck', '首', 'ik_首', 'ik_neck',
        'valvebipedbip01neck1', 'valvebipedbip01neck', 'neck', 'neck1',
        'mixamorig:neck', 'mixamorig_neck', 'bip01neck', 'bip01_neck',
        'bip01neck1', 'bip01_neck1'
    ],
    'core_head': [
        # Head variations - Standard, Valve, Mixamo, Japanese, IK
        'head', '頭', 'ik_頭', 'ik_head',
        'valvebipedbip01head1', 'valvebipedbip01head', 'head', 'head1',
        'mixamorig:head', 'mixamorig_head', 'bip01head', 'bip01_head',
        'bip01head1', 'bip01_head1'
    ],
    
    # Broader functional groups
    'all_core_bones': ['core'],  # For mirror tool compatibility
    'all_finger_bones': [
        # All finger metacarpals and segments
        'thumb_metacarpal_left', 'thumb_metacarpal_right',
        'thumb_1_left', 'thumb_1_right', 'thumb_2_left', 'thumb_2_right', 'thumb_3_left', 'thumb_3_right',
        'index_metacarpal_left', 'index_metacarpal_right',
        'index_1_left', 'index_1_right', 'index_2_left', 'index_2_right', 'index_3_left', 'index_3_right',
        'middle_metacarpal_left', 'middle_metacarpal_right',
        'middle_1_left', 'middle_1_right', 'middle_2_left', 'middle_2_right', 'middle_3_left', 'middle_3_right',
        'ring_metacarpal_left', 'ring_metacarpal_right',
        'ring_1_left', 'ring_1_right', 'ring_2_left', 'ring_2_right', 'ring_3_left', 'ring_3_right',
        'pinky_metacarpal_left', 'pinky_metacarpal_right',
        'pinky_1_left', 'pinky_1_right', 'pinky_2_left', 'pinky_2_right', 'pinky_3_left', 'pinky_3_right'
    ],
    'all_toe_bones': [
        # All detailed toe categories  
        'toe_little_proximal_left', 'toe_little_intermediate_left', 'toe_little_distal_left',
        'toe_ring_proximal_left', 'toe_ring_intermediate_left', 'toe_ring_distal_left',
        'toe_middle_proximal_left', 'toe_middle_intermediate_left', 'toe_middle_distal_left',
        'toe_index_proximal_left', 'toe_index_intermediate_left', 'toe_index_distal_left',
        'toe_thumb_proximal_left', 'toe_thumb_intermediate_left', 'toe_thumb_distal_left',
        'toe_little_proximal_right', 'toe_little_intermediate_right', 'toe_little_distal_right',
        'toe_ring_proximal_right', 'toe_ring_intermediate_right', 'toe_ring_distal_right',
        'toe_middle_proximal_right', 'toe_middle_intermediate_right', 'toe_middle_distal_right',
        'toe_index_proximal_right', 'toe_index_intermediate_right', 'toe_index_distal_right',
        'toe_thumb_proximal_right', 'toe_thumb_intermediate_right', 'toe_thumb_distal_right'
    ],
    'all_limb_bones': ['arms_left', 'arms_right', 'legs_left', 'legs_right'],
    'all_facial_bones': ['eye_left', 'eye_right'],
    'all_body_extras': ['breast_upper_left', 'breast_upper_right', 'breast_lower_left', 'breast_lower_right']
}

def get_bones_by_logical_group(group_name):
    """
    Get all bone names from a logical group of categories.
    Maintains compatibility with mirror tool while providing flexible access.
    
    Args:
        group_name (str): Name of the logical group
        
    Returns:
        list: All bone names from the specified group
    """
    if group_name not in BONE_LOGICAL_GROUPS:
        return []
    
    # Handle category references vs direct bone lists
    group_content = BONE_LOGICAL_GROUPS[group_name]
    if not group_content:
        return []
        
    # If first item is a category name, expand categories
    if isinstance(group_content[0], str) and group_content[0] in VRCHAT_STANDARD_BONES:
        all_bones = []
        for item in group_content:
            if item in VRCHAT_STANDARD_BONES:
                all_bones.extend(VRCHAT_STANDARD_BONES[item])
            else:
                all_bones.append(item)  # Direct bone name
        return all_bones
    else:
        # Direct list of bone names
        return group_content

def get_core_bone_subgroup(subgroup):
    """
    Get specific core bone subgroup while maintaining mirror tool compatibility.
    
    Args:
        subgroup (str): 'hips', 'spine', 'chest', 'neck', or 'head'
        
    Returns:
        list: Bone names for the specified core subgroup
    """
    subgroup_key = f'core_{subgroup}'
    if subgroup_key in BONE_LOGICAL_GROUPS:
        return BONE_LOGICAL_GROUPS[subgroup_key]
    return []

def get_all_core_bones():
    """
    Get all core bones for mirror tool compatibility.
    This is the same as accessing VRCHAT_STANDARD_BONES['core'] directly.
    
    Returns:
        list: All core bone name variations
    """
    return VRCHAT_STANDARD_BONES.get('core', [])

def is_core_bone(bone_name):
    """
    Check if a bone name matches any core bone variation.
    Useful for mirror tool operations. Case-insensitive matching.
    
    Args:
        bone_name (str): The bone name to check
        
    Returns:
        bool: True if the bone is a core bone
    """
    if not bone_name:
        return False
    
    bone_lower = bone_name.lower()
    core_bones = get_all_core_bones()
    core_bones_lower = [std_name.lower() for std_name in core_bones]
    return any(std_name in bone_lower or bone_lower in std_name 
              for std_name in core_bones_lower)

def check_bone_compatibility(armature_bones, preset_bones):
    """
    SMART compatibility check - only checks categories relevant to the preset
    Returns: (compatibility_score, missing_categories, details)
    """
    if not armature_bones or not preset_bones:
        return 0.0, [], "No bones to compare"
    
    # Convert to lowercase for fuzzy matching
    armature_lower = [bone.lower() for bone in armature_bones]
    preset_lower = [bone.lower() for bone in preset_bones]
    
    # SMART DETECTION: Find which categories are actually relevant to this preset
    relevant_categories = {}
    for category, standard_names in VRCHAT_STANDARD_BONES.items():
        # Convert standard names to lowercase for case-insensitive matching
        standard_names_lower = [std_name.lower() for std_name in standard_names]
        
        # Check if preset contains bones from this category (case-insensitive)
        preset_matches_in_category = sum(1 for bone in preset_lower 
                                       if any(std_name in bone or bone in std_name for std_name in standard_names_lower))
        
        if preset_matches_in_category > 0:
            relevant_categories[category] = standard_names
            print(f"DEBUG: Category '{category}' is relevant - preset has {preset_matches_in_category} bones from this category")
        else:
            print(f"DEBUG: Category '{category}' is NOT relevant - preset has no bones from this category")
    
    # INHERITANCE CHECK: Add child categories that will be affected by parent bone changes
    inheritance_categories = {}
    for parent_category in relevant_categories.keys():
        if parent_category in BONE_INHERITANCE_CHAINS:
            child_categories = BONE_INHERITANCE_CHAINS[parent_category]
            for child_category in child_categories:
                if child_category not in relevant_categories:  # Don't duplicate if already relevant
                    inheritance_categories[child_category] = VRCHAT_STANDARD_BONES[child_category]
                    print(f"DEBUG: Category '{child_category}' added due to inheritance from '{parent_category}'")
    
    # Combine relevant and inheritance categories
    all_relevant_categories = {**relevant_categories, **inheritance_categories}
    
    if not all_relevant_categories:
        print("DEBUG: No relevant categories found, using fallback compatibility check")
        return 1.0, [], "Preset uses custom bone names - compatibility check not applicable"
    
    # Check all relevant categories (both direct and inheritance)
    category_results = {}
    missing_categories = []
    
    for category, standard_names in all_relevant_categories.items():
        # Convert standard names to lowercase for case-insensitive matching
        standard_names_lower = [std_name.lower() for std_name in standard_names]
        
        # Check how many bones from this category exist in both sets (case-insensitive)
        armature_matches = sum(1 for bone in armature_lower 
                             if any(std_name in bone or bone in std_name for std_name in standard_names_lower))
        preset_matches = sum(1 for bone in preset_lower 
                           if any(std_name in bone or bone in std_name for std_name in standard_names_lower))
        
        # Different scoring logic for direct vs inheritance categories
        if category in inheritance_categories:
            # INHERITANCE CATEGORIES: Don't penalize score when preset has no bones from this category
            # This is expected for focused presets (e.g., elbow-only shouldn't be penalized for no finger bones)
            if preset_matches == 0:
                category_score = 1.0  # Perfect score - no expectation of bones in this category
                print(f"DEBUG: {category} (inheritance) compatibility: 1.00 - OK (no bones expected in focused preset)")
            else:
                # If preset does have bones from inheritance category, check normally
                min_expected = min(len(standard_names), preset_matches)
                if min_expected == 0:
                    min_expected = 1
                category_score = min(armature_matches, preset_matches) / min_expected
                
                if category_score < 0.3:  # Lower threshold for inherited effects
                    missing_categories.append(category)
                    print(f"DEBUG: {category} (inheritance) compatibility: {category_score:.2f} - MISSING")
                else:
                    print(f"DEBUG: {category} (inheritance) compatibility: {category_score:.2f} - OK")
        else:
            # DIRECT CATEGORIES: Standard scoring for bones actually in preset
            min_expected = min(len(standard_names), preset_matches)
            if min_expected == 0:
                min_expected = 1
                
            category_score = min(armature_matches, preset_matches) / min_expected
            
            # Standard threshold for direct categories (bones actually in preset)  
            if category_score < 0.7:  # Higher threshold for direct bone matches
                missing_categories.append(category)
                print(f"DEBUG: {category} (direct) compatibility: {category_score:.2f} - MISSING")
            else:
                print(f"DEBUG: {category} (direct) compatibility: {category_score:.2f} - OK")
        
        category_results[category] = {
            'score': category_score,
            'armature_matches': armature_matches,
            'preset_matches': preset_matches
        }
    
    # Calculate overall compatibility score (weighted: direct categories count more)
    direct_scores = [result['score'] for cat, result in category_results.items() if cat in relevant_categories]
    inheritance_scores = [result['score'] for cat, result in category_results.items() if cat in inheritance_categories]
    
    # Use weighted average: direct categories weight=2, inheritance categories weight=1
    total_weighted_score = sum(score * 2 for score in direct_scores) + sum(score * 1 for score in inheritance_scores)
    total_weight = len(direct_scores) * 2 + len(inheritance_scores) * 1
    
    if total_weight > 0:
        compatibility_score = total_weighted_score / total_weight
    else:
        compatibility_score = 0.0
    
    # Generate details string
    details = []
    for category, result in category_results.items():
        category_type = "(direct)" if category in relevant_categories else "(inheritance)"
        details.append(f"{category} {category_type}: {result['armature_matches']} arm / {result['preset_matches']} preset matches")
    
    print(f"DEBUG: Smart compatibility result: {compatibility_score:.2f} based on {len(direct_scores)} direct + {len(inheritance_scores)} inheritance categories")
    return compatibility_score, missing_categories, "; ".join(details)

def get_compatibility_warning_message(compatibility_score, missing_categories, armature_name, preset_name):
    """Generate user-friendly warning message based on compatibility check"""
    if compatibility_score >= 0.8:
        return None  # High compatibility, no warning needed
    
    if compatibility_score >= 0.5:
        return f"Medium compatibility ({compatibility_score:.1%}) between '{armature_name}' and preset '{preset_name}'. Some bones may not match."
    
    missing_str = ", ".join(missing_categories) if missing_categories else "multiple areas"
    return f"Low compatibility ({compatibility_score:.1%}) between '{armature_name}' and preset '{preset_name}'. Missing matches in: {missing_str}. Many transforms may not apply."